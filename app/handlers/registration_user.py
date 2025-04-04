import os
from aiogram import F, Router, Bot
from aiogram.types import Message, File
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database_vm.database import Database
from app.handlers import commands_router
from app.states.registration import RegistrationUser
from app.keyboards.reg_kb import сhoose_gender_kb, nickname_kb, choose_voice_kb

registration_router = Router()
voice_input_dir = "/usr/src/app/tg_bot/voice_input"

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'pl': 'Polish',
    'tr': 'Turkish',
    'ru': 'Russian',
    'nl': 'Dutch',
    'cs': 'Czech',
    'ar': 'Arabic',
    'zh-cn': 'Chinese',
    'ja': 'Japanese',
    'hu': 'Hungarian',
    'ko': 'Korean'
}

@commands_router.message(Command('registration'))
async def cmd_registration(message: Message, db: Database, state: FSMContext):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = message.from_user.id

        # Проверяем, существует ли пользователь в БД
        try:
            user_exists = await db.users.exists(user_id)
        except Exception as e:
            print(f"Ошибка при проверке существования пользователя {user_id}: {e}")
            await message.reply("⚠️ База данных временно недоступна. Пожалуйста, попробуйте позже.")
            return

        if user_exists:
            await message.reply(f"Вы уже зарегистрированы.")
            return

        await state.set_state(RegistrationUser.get_gender)
        await message.reply("Пожалуйста, выберите свой пол. Либо написав сообщение \"М\"\\\"Ж\", либо воспользовавшись кнопками.", reply_markup=сhoose_gender_kb())
    else:
        # в таком случае не реагируем
        return

@registration_router.message(RegistrationUser.get_gender)
async def get_gender(message: Message, state: FSMContext):
    if message.text.upper() == "М" or message.text.upper() == "Ж":
        if message.text.upper() == "М":
            await state.update_data(gender=False)
        else:
            await state.update_data(gender=True)
        
        await state.set_state(RegistrationUser.get_nickname)
        username = message.from_user.username
        await message.reply("Теперь выберите, как называть вас при генерации диалога.", reply_markup=nickname_kb(username))
    else:
        await message.reply("Пожалуйста, выберите М или Ж")

@registration_router.message(RegistrationUser.get_nickname)
async def get_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(RegistrationUser.get_language)
    languages = "\n".join([f"{code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()])
    await message.reply(f"Выберите язык для генерации аудио. Введите код языка (например, ru или en):\n\nДоступные языки:\n{languages}")

@registration_router.message(RegistrationUser.get_language)
async def get_language(message: Message, state: FSMContext):
    language_code = message.text.lower()
    if language_code not in SUPPORTED_LANGUAGES:
        await message.reply("Некорректный код языка. Пожалуйста, выберите из списка доступных.")
        return
    
    await state.update_data(language=language_code)
    await state.set_state(RegistrationUser.choose_voice)
    await message.reply("Выберите, каким голосом будут озвучиваться сообщения (ваш или голос бота):", reply_markup=choose_voice_kb())

@registration_router.message(RegistrationUser.choose_voice)
async def choose_voice(message: Message, state: FSMContext, db: Database):
    if message.text == "Озвучивать голосом бота":
        data = await state.get_data()
        user_id = message.from_user.id

        gender = data.get("gender")
        nickname = data.get("nickname")
        language = data.get("language")

        try:
            await db.users.add(user_id, gender, nickname, False, language)
        except Exception as e:
            print(f"Ошибка при добавлении пользователя {user_id} в базу данных: {e}")
            await message.reply("⚠️ База данных временно недоступна. Пожалуйста, попробуйте позже.")
            return
            
        await state.clear()
        await message.reply("Вы зарегистрированы и можете пользоваться полным функционалом бота!")
    elif message.text == "Озвучивать моим голосом":
        await state.set_state(RegistrationUser.get_voice)
        await message.reply('''Отлично, тогда запишите голосовое сообщение с вашим голосом примерно на 15 секунд. Вот скрипт для вас:

"Привет! Меня зовут [Имя]. Сегодня отличная погода, не так ли? Я проверяю, как звучит мой голос в этой системе. Один, два, три, четыре, пять... Хорошо! Теперь скажем: "Как быстро идут дела?" Отлично! Надеюсь, всё получится."''')
    else:
        await message.reply("Пожалуйста, используйте кнопки для выбора")
    
@registration_router.message(RegistrationUser.get_voice, F.voice)
async def get_voice(message: Message, state: FSMContext, db: Database, bot: Bot):
    try:
        # отправляем данные в бд
        data = await state.get_data()
        user_id = message.from_user.id
        
        gender = data.get("gender")
        nickname = data.get("nickname")
        language = data.get("language")
        
        # Проверка длительности голосового сообщения
        duration = message.voice.duration if message.voice else message.audio.duration
        if duration > 60:
            await message.reply("Длительность голосового сообщения не должна превышать 60 секунд. Пожалуйста, отправьте более короткое сообщение.")
            return
        
        file_id = None
        if message.voice:
            file_id = message.voice.file_id
            extension = "ogg"
        elif message.audio:
            file_id = message.audio.file_id
            extension = message.audio.file_name.split(".")[-1] if message.audio.file_name else "mp3"

        if not file_id:
            await message.reply("Не удалось обработать файл. Убедитесь, что вы отправили корректный аудиофайл.")
            return

        telegram_file: File = await bot.get_file(file_id)
        
        # Создаем директорию, если она не существует
        os.makedirs(voice_input_dir, exist_ok=True)
        
        file_path = os.path.join(voice_input_dir, f"{user_id}.{extension}")
        
        # Скачиваем файл
        await bot.download_file(telegram_file.file_path, file_path)

        # все прошло успешно - отправляем результат в БД
        try:
            await db.users.add(user_id, gender, nickname, True, language)
        except Exception as e:
            print(f"Ошибка при добавлении пользователя {user_id} с голосом в базу данных: {e}")
            await message.reply("⚠️ База данных временно недоступна. Пожалуйста, попробуйте позже.")
            return
            
        await state.clear()
        await message.reply("Вы зарегистрированы и можете пользоваться полным функционалом бота!")
    except Exception as e:
        print(f"Ошибка при обработке голосового сообщения: {e}")
        await message.reply("Не удалось обработать голосовое сообщение. Пожалуйста, попробуйте еще раз.")
