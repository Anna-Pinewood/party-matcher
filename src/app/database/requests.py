import json
from sqlalchemy import select

from app.database.models import Party, PartyUser, User, async_session


async def set_user(profile_data: dict) -> None:
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == profile_data["tg_id"])
        )

        if user:
            # If user is found, update their data
            user.name = profile_data["name"]
            user.gender = profile_data["gender"]
            user.age = profile_data["age"]
            user.vk_link = profile_data["vk_link"]
            user.reddit_link = profile_data["reddit_link"]
            user.phone_number = profile_data["phone_number"]
            user.language = profile_data["language"]
            user.cv = profile_data["cv"]
            user.text_desc = profile_data["text_desc"]
            user.parsed_resume = json.dumps(
                profile_data.get("parsed_resume", {}, ensure_ascii=False))
        else:
            # If user is not found, create a new one
            new_user = User(
                tg_id=profile_data["tg_id"],
                name=profile_data["name"],
                gender=profile_data["gender"],
                age=profile_data["age"],
                vk_link=profile_data["vk_link"],
                reddit_link=profile_data["reddit_link"],
                phone_number=profile_data["phone_number"],
                language=profile_data["language"],
                cv=profile_data["cv"],
                text_desc=profile_data["text_desc"],
                parsed_resume=json.dumps(profile_data.get("parsed_resume", {}, ensure_ascii=False))
            )
            session.add(new_user)

        await session.commit()


async def get_user(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))

        if result:
            # Если пользователь найден, возвращаем все его данные в виде словаря
            user_data = {
                "id": result.id,
                "tg_id": result.tg_id,
                "language": result.language,
                "name": result.name,
                "gender": result.gender,
                "age": result.age,
                "phone_number": result.phone_number,
                "vk_link": result.vk_link,
                "reddit_link": result.reddit_link,
                "cv": result.cv,
                "text_desc": result.text_desc,
            }
            return user_data
        else:
            # Если пользователь не найден
            return None


async def add_user_to_party(party_id: int, tg_id):
    async with async_session() as session:
        user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))

        if not user_id:
            return "no_user"

        party = await session.scalar(select(Party).where(Party.id == party_id))

        if party:
            result = await session.execute(
                select(PartyUser).where(
                    PartyUser.party_id == party_id,
                    PartyUser.user_id == user_id
                )
            )
            existing_record = result.scalar()

            if existing_record:
                return 'exist_record'

            new_party_user = PartyUser(
                party_id=party_id,
                user_id=user_id,
            )
            session.add(new_party_user)
            await session.commit()
            return "add_to_party"
        else:
            return "no_party"
