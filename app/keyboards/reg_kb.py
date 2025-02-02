from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def ChooseGender():
    gender = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="М"), KeyboardButton(text="Ж")]],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return gender

def Nickname(user_name):
    nickname = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user_name)]],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return nickname

def ChooseVoice():
    voice = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Генерировать на основе синтезированного голоса")],
                                           [KeyboardButton(text="Генерировать на основе моего голоса")]
                                           ],
                                                resize_keyboard=True,
                                                one_time_keyboard=True)
    return voice