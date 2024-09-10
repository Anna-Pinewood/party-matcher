from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="gender_yes")],
        [InlineKeyboardButton(text="No", callback_data="gender_no")],
    ]
)

vk_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="vk_yes")],
        [InlineKeyboardButton(text="No", callback_data="vk_no")],
    ]
)

cv_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="cv_yes")],
        [InlineKeyboardButton(text="No", callback_data="cv_no")],
    ]
)

reddit_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="reddit_yes")],
        [InlineKeyboardButton(text="No", callback_data="reddit_no")],
    ]
)

get_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Send phone number", request_contact=True)]],
    resize_keyboard=True,
)
