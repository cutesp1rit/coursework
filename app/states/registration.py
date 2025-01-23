from aiogram.fsm.state import State, StatesGroup

class RegistrationUser(StatesGroup):
    get_gender = State()
    get_nickname = State()
    get_voice = State()
    accept_agreement = State()