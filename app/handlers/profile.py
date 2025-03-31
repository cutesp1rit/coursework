import os, glob
from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router
from app.keyboards.reg_kb import сhoose_gender_kb, nickname_kb, choose_voice_kb
from app.states.profile_states import ProfileStates

profile_router = Router()
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

@commands_router.message(Command('change_nickname'))
async def cmd_change_nickname(message: Message, state: FSMContext, db: Database):
    if message.chat.type != 'private':
        await message.reply("Эта команда доступна только в личных сообщениях.")
        return
        
    user_id = str(message.from_user.id)
    if not await db.users.exists(user_id):
        await message.reply("Сначала необходимо зарегистрироваться с помощью команды /registration")
        return

    await state.set_state(ProfileStates.waiting_for_nickname)
    username = message.from_user.username
    await message.reply("Введите новый никнейм:", reply_markup=nickname_kb(username))

@profile_router.message(ProfileStates.waiting_for_nickname)
async def process_nickname_change(message: Message, state: FSMContext, db: Database):
    user_id = str(message.from_user.id)
    new_nickname = message.text
    
    await db.users.update_nickname(user_id, new_nickname)
    await state.clear()
    await message.reply(f"Ваш никнейм успешно изменен на: {new_nickname}")

@commands_router.message(Command('change_gender'))
async def cmd_change_gender(message: Message, state: FSMContext, db: Database):
    if message.chat.type != 'private':
        await message.reply("Эта команда доступна только в личных сообщениях.")
        return
        
    user_id = str(message.from_user.id)
    if not await db.users.exists(user_id):
        await message.reply("Сначала необходимо зарегистрироваться с помощью команды /registration")
        return

    await state.set_state(ProfileStates.waiting_for_gender)
    await message.reply("Выберите пол:", reply_markup=сhoose_gender_kb())

@profile_router.message(ProfileStates.waiting_for_gender)
async def process_gender_change(message: Message, state: FSMContext, db: Database):
    if message.text.upper() not in ["М", "Ж"]:
        await message.reply("Пожалуйста, выберите М или Ж")
        return
        
    user_id = str(message.from_user.id)
    new_gender = False if message.text.upper() == "М" else True
    
    await db.users.update_gender(user_id, new_gender)
    await state.clear()
    await message.reply("Гендер успешно изменен")

@commands_router.message(Command('change_voice'))
async def cmd_change_voice(message: Message, state: FSMContext, db: Database):
    if message.chat.type != 'private':
        await message.reply("Эта команда доступна только в личных сообщениях.")
        return
        
    user_id = str(message.from_user.id)
    if not await db.users.exists(user_id):
        await message.reply("Сначала необходимо зарегистрироваться с помощью команды /registration")
        return

    await state.set_state(ProfileStates.waiting_for_voice)
    await message.reply("Выберите, каким голосом будут озвучиваться сообщения (ваш или голос бота):", reply_markup=choose_voice_kb())

@profile_router.message(ProfileStates.waiting_for_voice)
async def process_voice_choice(message: Message, state: FSMContext, db: Database):
    user_id = str(message.from_user.id)
    
    if message.text == "Озвучивать голосом бота":
        await db.users.update_voice(user_id, False)
        await state.clear()
        await message.reply("Установлен голос бота")
    elif message.text == "Озвучивать моим голосом":
        await message.reply('''Отлично, тогда запишите голосовое сообщение с вашим голосом примерно на 15 секунд. Вот скрипт для вас:

"Привет! Меня зовут [Имя]. Сегодня отличная погода, не так ли? Я проверяю, как звучит мой голос в этой системе. Один, два, три, четыре, пять... Хорошо! Теперь скажем: "Как быстро идут дела?" Отлично! Надеюсь, всё получится."''')
        await state.set_state(ProfileStates.waiting_for_voice_file)
    else:
        await message.reply("Пожалуйста, используйте кнопки для выбора")

@profile_router.message(ProfileStates.waiting_for_voice_file, F.voice)
async def process_voice_file(message: Message, state: FSMContext, db: Database, bot: Bot):
    user_id = str(message.from_user.id)
    
    # Проверка длительности голосового сообщения
    duration = message.voice.duration if message.voice else message.audio.duration
    if duration > 60:
        await message.reply("Длительность голосового сообщения не должна превышать 60 секунд. Пожалуйста, отправьте более короткое сообщение.")
        return
    
    try:
        user_data = await db.users.get_by_id(user_id)
        if user_data and user_data.get("voice"):
            file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")
            matching_files = glob.glob(file_pattern)
            for file_path in matching_files:
                try:
                    os.remove(file_path)
                except OSError:
                    # Продолжаем выполнение даже если не удалось удалить старый файл
                    pass
        
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        extension = "ogg" if message.voice else message.audio.file_name.split(".")[-1]
        
        telegram_file = await bot.get_file(file_id)
        file_path = os.path.join(voice_input_dir, f"{user_id}.{extension}")
        
        try:
            os.makedirs(voice_input_dir, exist_ok=True)
            await bot.download_file(telegram_file.file_path, file_path)
        except Exception:
            await message.reply("Не удалось сохранить голосовое сообщение. Пожалуйста, попробуйте еще раз.")
            return
        
        await db.users.update_voice(user_id, True)
        await state.clear()
        await message.reply("Голос успешно обновлен")
    except Exception:
        await state.clear()
        await message.reply("Произошла ошибка при обработке голосового сообщения. Пожалуйста, попробуйте позже.")

@commands_router.message(Command('change_lang'))
async def cmd_change_language(message: Message, state: FSMContext, db: Database):
    if message.chat.type != 'private':
        await message.reply("Эта команда доступна только в личных сообщениях.")
        return
        
    user_id = str(message.from_user.id)
    if not await db.users.exists(user_id):
        await message.reply("Сначала необходимо зарегистрироваться с помощью команды /registration")
        return

    await state.set_state(ProfileStates.waiting_for_language)
    languages = "\n".join([f"{code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()])
    await message.reply(f"Выберите язык для генерации аудио. Введите код языка (например, ru или en):\n\nДоступные языки:\n{languages}")

@profile_router.message(ProfileStates.waiting_for_language)
async def process_language_change(message: Message, state: FSMContext, db: Database):
    language_code = message.text.lower()
    if language_code not in SUPPORTED_LANGUAGES:
        await message.reply("Некорректный код языка. Пожалуйста, выберите из списка доступных.")
        return
        
    user_id = str(message.from_user.id)
    try:
        await db.users.update_language(user_id, language_code)
        await state.clear()
        await message.reply(f"Язык успешно изменен на {SUPPORTED_LANGUAGES[language_code]}")
    except Exception:
        await state.clear()
        await message.reply("Не удалось изменить язык. Пожалуйста, попробуйте позже.")
