from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router

voice_router = Router()

# команда voice message (отправляет сгенерированное аудио)
@commands_router.message(Command('vm'))
async def cmd_vm(message: Message, db: Database):
    if message.reply_to_message:
        # Получаем сообщение, на которое отвечает пользователь
        replied_message = message.reply_to_message

        # Отправляем информацию о сообщении, на которое отвечено
        await message.reply(
            f"Вы ответили на сообщение: \n"
            f"Текст: {replied_message.text or 'Нет текста'}\n"
            f"Отправитель: {replied_message.from_user.full_name}"
        )
    else:
        # Если команда вызвана без ответа на сообщение
        await message.reply("Вы должны использовать эту команду как ответ на сообщение.")
    # проверка на наличие голоса пользователя в БД
    # отправляем с дефолтным если что

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