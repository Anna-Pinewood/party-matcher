import asyncio
import json
import logging
import aiohttp
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.database import requests as rq
from app.matching.matching import calculate_similarity
from app.matching.llm_matching import get_matching_llm
import json
from aiogram.types import Message
from aiogram.filters import Command

import app.database.requests as rq
import app.keyboards as kb
from parsers.parse_resume import (parse_resume_yandexgpt,
                                  parse_resume_openaigpt)

logging.basicConfig(level=logging.INFO)


router = Router()


class ProfileForm(StatesGroup):
    tg_id = State()
    language = State()
    name = State()
    gender = State()
    age = State()
    phone_number = State()
    vk_link = State()
    reddit_link = State()
    cv = State()
    text_desc = State()
    all_load = State()


@router.message(CommandStart())
async def get_user_info(message: Message, state: FSMContext):
    description = (
        "Hi! I'm your bot. Here's what I can do:\n"
        "/start - Show this message\n"
        "/create_profile - create a profile\n"
        "/join_party - join to party\n"
        "get_matches - when you created profile u can get matches\n"
    )
    await message.answer(description)


@router.message(Command("create_profile"))
async def create_profile(message: Message, state: FSMContext):
    user = message.from_user
    user_id = user.id
    language = user.language_code

    await state.update_data(tg_id=user_id)
    await state.update_data(language=language)
    await state.set_state(ProfileForm.name)
    await message.answer("What's your name?")


@router.message(ProfileForm.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProfileForm.gender)
    await message.answer("You're a woman?", reply_markup=kb.gender_kb)


@router.callback_query(F.data.in_({"gender_yes", "gender_no"}))
async def register_gender(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    if answer == "gender_yes":
        await state.update_data(gender=1)
    elif answer == "gender_no":
        await state.update_data(gender=0)

    await callback.answer("Your answer has been saved")
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.set_state(ProfileForm.age)
    await callback.message.answer("How old are you?")


@router.message(ProfileForm.age)
async def register_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if 1 <= age <= 120:
            await state.update_data(age=age)
            await state.set_state(ProfileForm.phone_number)
            await message.answer("Send your phone number", reply_markup=kb.get_number)
        else:
            await message.answer("Please enter the correct age.")
    except ValueError:
        await message.answer("Please enter the correct age.")


@router.message(ProfileForm.phone_number, F.contact)
async def register_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=str(message.contact.phone_number))
    await message.answer(
        "Your number has been saved", reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Are you willing to share your VK profile?", reply_markup=kb.vk_kb
    )


@router.callback_query(F.data.in_({"vk_yes", "vk_no"}))
async def register_vk(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    if answer == "vk_yes":
        await callback.message.answer(
            "Are you willing to share your vk profile that starts with 'https://vk.com/'?"
        )
        await state.set_state(ProfileForm.vk_link)
    elif answer == "vk_no":
        await state.update_data(vk_link=None)
        await callback.message.answer(
            "Are you willing to share your reddit profile?", reply_markup=kb.reddit_kb
        )

    await callback.answer("Your answer has been saved")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(ProfileForm.vk_link)
async def register_vk_link(message: Message, state: FSMContext):
    try:
        if message.text.startswith("https://vk.com/"):
            await state.update_data(vk_link=message.text)
            await message.answer(
                "Are you willing to share your reddit profile?",
                reply_markup=kb.reddit_kb,
            )
        else:
            await message.answer(
                "Please enter a link that begins with 'https://vk.com/'"
            )
    except ValueError:
        await message.answer("Please enter the correct link.")


@router.callback_query(F.data.in_({"reddit_yes", "reddit_no"}))
async def register_reddit(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    if answer == "reddit_yes":
        await callback.message.answer("Please send your Reddit username")
        await state.set_state(ProfileForm.reddit_link)
    elif answer == "reddit_no":
        await state.update_data(reddit_link=None)
        await callback.message.answer(
            "Are you willing to share your CV (pdf format)?", reply_markup=kb.cv_kb
        )

    await callback.answer("Your answer has been saved")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(ProfileForm.reddit_link)
async def register_reddit_link(message: Message, state: FSMContext):
    try:
        await state.update_data(reddit_link=message.text)
        await message.answer(
            "Are you willing to share your CV (pdf format)?",
            reply_markup=kb.cv_kb,
        )
    except ValueError:
        await message.answer("Please enter the correct profile.")


@router.callback_query(F.data.in_({"cv_yes", "cv_no"}))
async def register_cv(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    if answer == "cv_yes":
        await callback.message.answer("Attach a CV in pdf format")
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.set_state(ProfileForm.cv)
    elif answer == "cv_no":
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.update_data(cv=None)
        await callback.message.answer("Tell me who you'd like to socialize with.")
        await state.set_state(ProfileForm.text_desc)


@router.message(ProfileForm.cv, F.document.mime_type == "application/pdf")
async def process_cv(message: Message, state: FSMContext):
    document = message.document

    # Download PDF file
    file_id = document.file_id
    file_info = await message.bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot"
    file_url = f"{file_url}/{message.bot.token}/{file_info.file_path}"

    file_path = f"/app/media/{message.from_user.id}.pdf"
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                with open(file_path, "wb") as f:
                    f.write(await response.read())

    parsed_resume = await asyncio.to_thread(parse_resume_openaigpt, file_path)
    parsed_resume_json = json.dumps(parsed_resume, ensure_ascii=False)

    await state.update_data(cv=file_path, parsed_resume=parsed_resume_json)

    await message.answer(
        "The CV has been successfully saved and parsed!\nTell me who you'd like to socialize with."
    )
    await state.set_state(ProfileForm.text_desc)


@router.message(ProfileForm.cv, F.document.mime_type != "application/pdf")
async def process_non_pdf(message: Message):
    await message.answer("Attach a CV in PDF format.")


@router.message(ProfileForm.text_desc)
async def register_text_desc(message: Message, state: FSMContext):
    await state.update_data(text_desc=message.text)
    await message.answer("Questionnaire successfully filled out! Thank you!")
    await state.set_state(ProfileForm.all_load)
    await set_user(message, state)


@router.message(ProfileForm.all_load)
async def set_user(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await rq.set_user(user_data)

    formatted_data = "\n".join(
        f"{key}: {value}" for key, value in user_data.items())
    await message.answer(f"Вот все ваши данные:\n{formatted_data}")

    # new_party_id = await rq.add_party('popopepe', 'asdasda')
    # await message.answer(f"Party '{name}' added successfully with ID {new_party_id}!")

    # user_data = await rq.get_user(user_data['tg_id'])
    # formatted_data = "\n".join(f"{key}: {value}" for key, value in user_data.items())
    # await message.answer(f"Вот все ваши данные с БД:\n{formatted_data}")

    await state.clear()


class PartyJoin(StatesGroup):
    waiting_for_party_id = State()


@router.message(Command("join_party"))
async def join_party_command(message: Message, state: FSMContext):
    await message.answer("Please enter the Party ID you want to join:")
    await state.set_state(PartyJoin.waiting_for_party_id)


@router.message(PartyJoin.waiting_for_party_id)
async def process_party_id(message: Message, state: FSMContext):
    try:
        tg_id = message.from_user.id
        party_id = int(message.text)

        result = await rq.add_user_to_party(party_id, tg_id)

        if result == "no_user":
            await message.answer(
                "This user does not exist, you need to create profile.\n /create_profile"
            )
        elif result == "exist_record":
            await message.answer("You're already a member of the party.")
        elif result == "add_to_party":
            await message.answer("You have successfully joined the party!")
        else:
            await message.answer("Sorry, the party with this ID does not exist.")
    except ValueError:
        await message.answer("Invalid Party ID. Please enter a valid number.")
    finally:
        await state.clear()


@router.message(Command("get_matches"))
async def get_matches(message: Message):
    tg_id = message.from_user.id

    user_profile = await rq.get_user(tg_id)
    if not user_profile:
        await message.answer("You need to create a profile first. Use /create_profile command.")
        return

    party_id = await rq.get_user_party_id(tg_id)
    if not party_id:
        await message.answer("You're not in any party. Join a party first using /join_party command.")
        return

    party_users = await rq.get_party_users(party_id)
    logging.info('Got %s users', len(party_users))

    user_similarities = []
    for other_user in party_users:
        if other_user['tg_id'] != tg_id:
            similarity = calculate_similarity(user_profile, other_user)
            user_similarities.append((other_user, similarity))

    user_similarities.sort(key=lambda x: x[1], reverse=True)
    logging.info('Top scores\n%s', "\n".join(user_similarities[:10]))

    top_users = [user for user, _ in user_similarities[:10]]

    matching_result = get_matching_llm(user_profile, top_users)

    # try:
    #     matches = json.loads(matching_result)
    #     response = "Your top matches:\n\n"
    #     for match in matches:
    #         response += f"Name: {match['name']}\n"
    #         response += f"Similarity: {match['similarity']}\n"
    #         response += f"Explanation: {match['explanation']}\n"
    #         user = next(
    #             (u for u in top_users if u['name'] == match['name']), None)
    #         if user:
    #             response += f"Contact: {user.get('phone_number', 'N/A')}\n"
    #         response += "\n"
    # except json.JSONDecodeError:
    #     response = "An error occurred while processing your matches. Please try again later."

    await message.answer(matching_result)
