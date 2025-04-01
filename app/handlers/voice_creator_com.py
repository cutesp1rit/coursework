import os
import asyncio
from aiogram import F, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database_vm.database import Database
from app.handlers import commands_router
from app.voice_processing.voice_creator import VoiceCreator

voice_router = Router()

# команда voice message (отправляет сгенерированное аудио)
@commands_router.message(Command('vm'))
async def cmd_vm(message: Message, db: Database, voice_creator: VoiceCreator):
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
    
    try:
        # Запускаем генерацию в отдельной задаче чтобы не блокировать основной поток
        asyncio.create_task(voice_creator.process_voice_message(message, text_to_say, user_id))
    except Exception as e:
        await message.reply(f"Произошла ошибка при генерации аудио.")

# команда voice dialogue (генерирует диалог)
@commands_router.message(Command('vd'))
async def cmd_vd(message: Message, db: Database, voice_creator: VoiceCreator):
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
            await message.reply("Количество сообщений должно быть положительным числом.")
            return
        if count > 25:
            await message.reply("Максимальное количество сообщений для диалога - 25. Пожалуйста, укажите число от 1 до 25.")
            return
    except (IndexError, ValueError):
        await message.reply("Укажите корректное количество сообщений. Пример: /vd 6")
        return

    try:
        messages = await db.messages.get_dialogue_messages(replied_message_id, str(message.chat.id), count)

        if not messages:
            await message.reply("Не удалось найти сообщения для формирования диалога.")
            return

        await message.reply("Генерирую диалог для вас...")
        
        # Запускаем генерацию диалога в отдельной задаче для асинхронной обработки
        asyncio.create_task(process_dialogue_task(message, messages, voice_creator))
    except Exception as e:
        await message.reply(f"Произошла ошибка при получении сообщений из базы данных.")

async def process_dialogue_task(message: Message, messages: list, voice_creator: VoiceCreator):
    try:
        ogg_path = await voice_creator.process_dialogue(messages, str(message.chat.id))
        
        if not ogg_path or not os.path.exists(ogg_path):
            await message.reply("Произошла ошибка при создании аудиофайла.")
            return
            
        voice_file = FSInputFile(ogg_path)
        await message.reply_voice(voice_file)
        
    except Exception as e:
        await message.reply(f"Произошла ошибка при генерации аудио для диалога.")
    finally:
        # Удаляем временный файл, даже если произошла ошибка
        if 'ogg_path' in locals() and ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)

# если пришло обычное текстовое сообщение
@voice_router.message(F.text)
async def just_message(message: Message, state: FSMContext, db: Database, voice_creator: VoiceCreator):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)
        
        try:
            user_data = await db.users.get_by_id(user_id)
            
            if user_data and user_data.get("vmm"):
                # Проверка ограничения на длину текста
                if len(message.text) > 1000:
                    await message.reply("Текст слишком длинный. Максимальная длина для озвучки - 1000 символов.")
                    return
                    
                await message.reply("Генерирую аудио для вас...")
                
                # Запускаем генерацию в отдельной задаче для асинхронной обработки приватных сообщений
                asyncio.create_task(voice_creator.process_private_voice_message(message, user_id))
        except Exception as e:
            await message.reply(f"Произошла ошибка при обработке сообщения.")

    elif chat_type in ['group', 'supergroup']:
        try:
            await voice_creator.handle_group_message(message)
        except Exception as e:
            # В групповых чатах лучше логировать ошибки, а не отправлять сообщения
            print(f"Ошибка при обработке группового сообщения: {str(e)}")
    else:
        return