from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router

import torch
from io import StringIO
import sys

import glob
import os
from aiogram.types import FSInputFile
from TTS.api import TTS
import torch
import datetime

sys.stdin = StringIO("y\n")
voice_output_dir = "/usr/src/app/tg_bot/voice_files"
voice_input_dir = "/usr/src/app/tg_bot/voice_input"

voice_router = Router()
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# команда voice message (отправляет сгенерированное аудио)
@commands_router.message(Command('vm'))
async def cmd_vm(message: Message, db: Database):
    if message.reply_to_message:
        text_to_say = message.reply_to_message.text

        if not text_to_say:
            await message.reply("Сообщение, на которое вы ответили, не содержит текста.")
            return

        user_id = str(message.reply_to_message.from_user.id)
        # даже если поставить здесь ogg, а не wav, то волны не появляются((
        output_path = os.path.join(voice_output_dir, f"{user_id}_cloned.wav")

        if not await db.is_user_exist(user_id):
            # используем дефолтного спикера
            await message.reply("Генерирую аудио с дефолтным голосом...")
            tts.tts_to_file(
                text=text_to_say,
                speaker="Ana Florence",
                file_path=output_path,
                language="ru"
            )
            voice_file = FSInputFile(output_path)
            await message.answer_voice(voice_file)
            return

        user_data = await db.get_user_by_id(user_id)

        file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")
        matching_files = glob.glob(file_pattern)
        user_voice_path = matching_files[0] if matching_files else None

        # если пользователь использует свой голос
        if user_data.get("voice") and user_voice_path:
            await message.reply("Генерирую аудио с вашим индивидуальным голосом...")
            tts.tts_to_file(
                text=text_to_say,
                speaker_wav=user_voice_path,
                file_path=output_path,
                language="ru"
            )
        else:
            # используем дефолтного спикера
            await message.reply("Генерирую аудио с дефолтным голосом...")
            tts.tts_to_file(
                text=text_to_say,
                speaker="Ana Florence",
                file_path=output_path,
                language="ru"
            )

        voice_file = FSInputFile(output_path)
        await message.answer_voice(voice_file)

    else:
        # если команда вызвана без ответа на сообщение
        await message.reply("Вы должны использовать эту команду как ответ на сообщение.")

# команда voice dialogue (генерирует диалог)
@commands_router.message(Command('vd'))
async def cmd_vd(message: Message, db: Database):
    # проверяем на то, что сообщение не слишком давнее + количество сообщений (флаг) парсим

    # проверка на групповой чат
    chat_type = message.chat.type

    if chat_type in ['group', 'supergroup']:
        # это групповой чат
        await message.reply("Это групповой чат.")
    else:
        # в таком случае не реагируем
        return

# метод для генерация голосового сообщения на основе текста
async def generate_voice_message(text: str, user_id: str, uses_custom_voice: bool, db: Database, message: Message):
    file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")
    matching_files = glob.glob(file_pattern)
    user_voice_path = matching_files[0] if matching_files else None

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    output_path = os.path.join(voice_output_dir, f"{user_id}_cloned.wav")

    if uses_custom_voice and user_voice_path:
        await message.reply("Генерирую аудио с вашим индивидуальным голосом...")
        tts.tts_to_file(
            text=text,
            speaker_wav=user_voice_path,
            file_path=output_path,
            language="ru"
        )
    else:
        await message.reply("Генерирую аудио с дефолтным голосом...")
        tts.tts_to_file(
            text=text,
            speaker="Ana Florence",
            file_path=output_path,
            language="ru"
        )

    voice_file = FSInputFile(output_path)
    await message.answer_voice(voice_file)

# обработка текстового сообщения в групповых чатах
async def handle_group_message(message: Message, db: Database):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    username = message.from_user.username
    message_text = message.text
    created_at = datetime.now()

    await db.add_chat_message(
        message_id=message.message_id,
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_text=message_text,
        created_at=created_at,
    )

    message_count = await db.get_message_count(chat_id)

    # если сообщений больше 1000, удаляем самое старое
    if message_count > 1000:
        oldest_message_id = await db.get_oldest_message_id(chat_id)
        if oldest_message_id:
            await db.delete_message(oldest_message_id)


# если пришло обычное текстовое сообщение
@voice_router.message(F.text)
async def just_message(message: Message, state: FSMContext, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        user_data = await db.get_user_by_id(user_id)
        if user_data and user_data.get("vmm"):
            await generate_voice_message(message.text, user_id, user_data.get("voice"), db, message)
    elif chat_type in ['group', 'supergroup']:
        await handle_group_message(message, db)
    else:
        return