from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_gender = State()
    waiting_for_voice = State() 
    waiting_for_voice_file = State() 
    waiting_for_language = State()