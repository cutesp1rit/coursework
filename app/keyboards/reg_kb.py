from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ====================================================
# МЕТОДЫ-КЛАВИАТУРЫ ПРИ РАБОТЕ С ДАННЫМИ ПОЛЬЗОВАТЕЛЯ
# ====================================================

def сhoose_gender_kb():
    gender = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="М"), KeyboardButton(text="Ж")]],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return gender

def nickname_kb(user_name):
    nickname = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user_name)]],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return nickname

def choose_voice_kb():
    voice = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Озвучивать голосом бота")],
                                           [KeyboardButton(text="Озвучивать моим голосом")]
                                           ],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return voice