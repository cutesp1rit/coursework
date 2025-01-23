from aiogram.fsm.state import State, StatesGroup

class ChangeVoice(StatesGroup):
    change_default = State()
    set_name = State()
    change_own = State()