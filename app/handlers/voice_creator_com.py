import os

from aiogram import F, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.database import Database
from app.handlers import commands_router
from app.voice_creator import (
    generate_voice_message,
    convert_wav_to_ogg,
    format_dialogue,
    generate_audio_for_dialogue,
    combine_audio_files,
    handle_group_message
)

voice_output_dir = "/usr/src/app/tg_bot/voice_output"
os.makedirs(voice_output_dir, exist_ok=True)
voice_input_dir = "/usr/src/app/tg_bot/voice_input"

voice_router = Router()

# команда voice message (отправляет сгенерированное аудио)
@commands_router.message(Command('vm'))
async def cmd_vm(message: Message, db: Database):
    if not message.reply_to_message:
        await message.reply("Вы должны использовать эту команду как ответ на сообщение.")
        return

    text_to_say = message.reply_to_message.text
    if not text_to_say:
        await message.reply("Сообщение, на которое вы ответили, не содержит текста.")
        return
        
    # Проверка на ограничение длины текста
    if len(text_to_say) > 1000:
        await message.reply("Текст слишком длинный. Максимальная длина для озвучки - 1000 символов.")
        return

    await message.reply("Генерирую аудио для вас...")
    user_id = str(message.reply_to_message.from_user.id)

    output_path_wav = os.path.join(voice_output_dir, f"{user_id}_cloned.wav")
    output_path_ogg = os.path.join(voice_output_dir, f"{user_id}_cloned.ogg")

    await generate_voice_message(text_to_say, user_id, db, output_path_wav)

    convert_wav_to_ogg(output_path_wav, output_path_ogg)

    voice_file = FSInputFile(output_path_ogg)
    await message.answer_voice(voice_file)

    if os.path.exists(output_path_ogg):
        os.remove(output_path_ogg)

# команда voice dialogue (генерирует диалог)
@commands_router.message(Command('vd'))
async def cmd_vd(message: Message, db: Database):
    chat_type = message.chat.type

    # проверка, что это именно группа 
    if chat_type not in ['group', 'supergroup']:
        await message.reply("Команда /vd доступна только в групповых чатах.")
        return

    # проверка, что это ответ на сообщение
    if not message.reply_to_message:
        await message.reply("Вы должны использовать эту команду как ответ на сообщение.")
        return

    replied_message_id = str(message.reply_to_message.message_id)

    # парсим + получаем количество сообщений
    try:
        count = int(message.text.split(' ')[1])
        if count <= 0:
            raise ValueError
    except (IndexError, ValueError):
        await message.reply("Укажите корректное количество сообщений. Пример: /vd 6")
        return

    messages = await db.messages.get_dialogue_messages(replied_message_id, str(message.chat.id), count)

    if not messages:
        await message.reply("Не удалось найти сообщения для формирования диалога.")
        return

    await message.reply("Генерирую диалог для вас...")

    chat_id = str(message.chat.id)

    dialogue_texts = await format_dialogue(messages, db)

    audio_files = await generate_audio_for_dialogue(dialogue_texts, chat_id, db)

    final_audio_path = combine_audio_files(audio_files, chat_id)

    voice_file = FSInputFile(final_audio_path)
    await message.reply_voice(voice_file)

    if os.path.exists(final_audio_path):
        os.remove(final_audio_path)

# если пришло обычное текстовое сообщение
@voice_router.message(F.text)
async def just_message(message: Message, state: FSMContext, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)
        
        user_data = await db.users.get_by_id(user_id)
        
        if user_data and user_data.get("vmm"):
            # Проверка ограничения на длину текста
            if len(message.text) > 1000:
                await message.reply("Текст слишком длинный. Максимальная длина для озвучки - 1000 символов.")
                return
                
            await message.reply("Генерирую аудио для вас...")

            output_path_wav = os.path.join(voice_output_dir, f"{user_id}_cloned.wav")

            await generate_voice_message(message.text, user_id, db, output_path_wav)

            voice_file = FSInputFile(output_path_wav)
            await message.answer_voice(voice_file)

            if os.path.exists(output_path_wav):
                os.remove(output_path_wav)

    elif chat_type in ['group', 'supergroup']:
        await handle_group_message(message, db)
    else:
        return