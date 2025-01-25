from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router

import os
from aiogram.types import FSInputFile
from TTS.api import TTS
import torch

voice_output_dir = "/usr/src/app/tg_bot/voice_output"
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

        user_id = str(message.from_user.id)
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

        user_voice_path = os.path.join(voice_input_dir, f"{user_id}.wav")

        uses_custom_voice = user_data.get("voice") and os.path.exists(user_voice_path)

        output_path = os.path.join(voice_output_dir, f"{user_id}_cloned.wav")

        # если пользователь использует свой голос
        if uses_custom_voice:
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