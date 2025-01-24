from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router
from app.states.registration import RegistrationUser
from app.keyboards.reg_kb import ChooseGender, Nickname, ChooseVoice

registration_router = Router()

@commands_router.message(Command('registration'))
async def cmd_registration(message: Message, db: Database, state: FSMContext):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЯ НЕТ В БД!!!
        if await db.is_user_exist(user_id):
            await message.reply(f"Вы уже зарегистрированы.")
            return

        await state.set_state(RegistrationUser.get_gender)
        await message.reply("Пожалуйста, выберите свой пол. Либо написав сообщение \"М\"\\\"Ж\", либо воспользовавшись кнопками.", reply_markup=ChooseGender())

    else:
        # в таком случае не реагируем
        return

@registration_router.message(RegistrationUser.get_gender)
async def get_gender(message: Message, state: FSMContext):
    if message.text == "М" or message.text == "Ж":
        data = await state.get_data()
        if message.text == "М":
            await state.update_data(gender=False)
        else:
            await state.update_data(gender=True)
        await state.set_state(RegistrationUser.get_nickname)
        username = message.from_user.username
        await message.reply("Теперь выберите, как называть вас при генерации диалога.", reply_markup=Nickname(username))

@registration_router.message(RegistrationUser.get_nickname)
async def get_nickname(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(nickname=message.text)
    await state.set_state(RegistrationUser.choose_voice)
    await message.reply("Теперь выберите, использовать синтезированный голос по умолчанию или генерировать на основе вашего.", reply_markup=ChooseVoice())

@registration_router.message(RegistrationUser.choose_voice)
async def choose_voice(message: Message, state: FSMContext, db: Database):
    if message.text == "Генерировать на основе синтезированного голоса":
        data = await state.get_data()
        user_id = str(message.from_user.id)

        gender = data.get("gender")
        nickname = data.get("nickname")

        await db.add_user(user_id, gender, nickname, False)
        await state.clear()
        await message.reply("Вы зарегистрированы и можете пользоваться полным функционалом бота!")
    elif message.text == "Генерировать на основе моего голоса":
        await state.set_state(RegistrationUser.get_voice)
        await message.reply("Отлично, тогда пришлите аудиофайл с вашим голосом.")
    
@registration_router.message(RegistrationUser.get_voice, F.document | F.audio | F.voice)
async def get_voice(message: Message, state: FSMContext, db: Database):
    # отправляем данные в бд
    data = await state.get_data()
    user_id = str(message.from_user.id)
    
    gender = data.get("gender")
    nickname = data.get("nickname")

    await db.add_user(user_id, gender, nickname, True)
    await message.reply("Вы зарегистрированы и можете пользоваться полным функционалом бота!")
    
    # сохраняем аудио в папку

    await state.clear()
