from aiogram.fsm.state import State, StatesGroup

class RegistrationUser(StatesGroup):
    get_gender = State()
    get_nickname = State()
    choose_voice = State()
    get_language = State()
    get_voice = State()