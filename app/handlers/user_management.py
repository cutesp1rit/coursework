from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os, glob
from database_vm.database import Database
from app.handlers import commands_router

user_management_router = Router()

# команда voice message mode (устанавливаем "мод" постоянной генерации аудиосообщений на любой текст)
@commands_router.message(Command('vmm'))
async def cmd_vmm(message: Message, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        if not await db.users.exists(user_id):
            await message.reply(f"Для того чтобы воспользоваться этой функцией, пожалуйста, зарегистрируйтесь командой /registration.")
            return

        await db.users.update_vmm(user_id, True)
        await message.reply(f"Теперь на каждое обычное сообщение мы будем генерировать голосовое сообщение.")
    else:
        # в таком случае не реагируем
        return

# команда stop voice message mode (оставнавливает "мод" постоянной генерации аудиосообщений на любой текст)
@commands_router.message(Command('stop_vmm'))
async def cmd_stop_vmm(message: Message, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        if not await db.users.exists(user_id):
            await message.reply(f"Для того чтобы воспользоваться этой функцией, пожалуйста, зарегистрируйтесь командой /registration.")
            return

        await db.users.update_vmm(user_id, False)
        await message.reply(f"Постоянная генерация остановлена.")
    else:
        # в таком случае не реагируем
        return

@commands_router.message(Command('delete_data'))
async def cmd_delete_data(message: Message, db: Database):
    chat_type = message.chat.type

    # проверка чата на приватность
    if chat_type == 'private':
        user_id = str(message.from_user.id)

        if not await db.users.exists(user_id):
            await message.reply(f"Ваших данных нет в базе.")
            return

        user_data = await db.users.get_by_id(user_id)

        # проверяем, использует ли пользователь свой голос
        if user_data.get("voice"):
            voice_input_dir = "/usr/src/app/tg_bot/voice_input"
            file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")

            matching_files = glob.glob(file_pattern)

            for file_path in matching_files:
                try:
                    os.remove(file_path)
                except Exception:
                    # Если не удалось удалить файл, продолжаем с остальными
                    pass

        await db.users.delete(user_id)
        await message.reply(f"Ваши данные успешно удалены из базы!")
    else:
        # в таком случае не реагируем
        return