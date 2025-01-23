from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.database import Database
from app.handlers import commands_router

user_management_router = Router()

# команда voice message mode (устанавливаем "мод" постоянной генерации аудиосообщений на любой текст)
@commands_router.message(Command('vmm'))
async def cmd_vmm(message: Message, db: Database):

    chat_type = message.chat.type

    if chat_type == 'private':
        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЬ ЕСТЬ В БД!!!
        user_id = str(message.from_user.id)

        if not await db.is_user_exist(user_id):
            await message.reply(f"Для того чтобы воспользоваться этой функцией, пожалуйста, зарегистрируйтесь командой /registration.")
            return

        await db.set_vmm_true(telegram_user_id=user_id)
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

        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЬ ЕСТЬ В БД!!!
        if not await db.is_user_exist(user_id):
            await message.reply(f"Для того чтобы воспользоваться этой функцией, пожалуйста, зарегистрируйтесь командой /registration.")
            return

        await db.set_vmm_false(telegram_user_id=user_id)
        await message.reply(f"Постоянная генерация остановлена.")
    else:
        # в таком случае не реагируем
        return

# команда change voice (изменяет текущее или устанавливает новое аудиосообщение пользователя для дальнейшей генерации)
@commands_router.message(Command('change_voice'))
async def cmd_changevoice(message: Message, db: Database):

    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЬ ЕСТЬ В БД!!!
        if not await db.is_user_exist(user_id):
            await message.reply(f"Для того чтобы воспользоваться этой функцией, пожалуйста, зарегистрируйтесь командой /registration.")
            return

        # это личный чат
        await message.reply("Это личный чат.")
    else:
        # в таком случае не реагируем
        return
    
    # запросить у пользователя файл + проверка на корректность типа файла
    # возможно добавить возможность с дефолтным голосом?
    # занесение голосового сообщения в базу данных

@commands_router.message(Command('del'))
async def cmd_del(message: Message, db: Database):
    chat_type = message.chat.type

    # проверка чата на приватность
    if chat_type == 'private':
        user_id = str(message.from_user.id)

        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЬ ЕСТЬ В БД!!!
        if not await db.is_user_exist(user_id):
            await message.reply(f"Ваших данных нет в базе.")
            return

        await db.delete_user(telegram_user_id=user_id)
        await message.reply(f"Ваши данные успешно удалены из базы!")
    else:
        # в таком случае не реагируем
        return
    
    # добавить удаление также его голоса
    # надо ли проверять, что он уже удален из бд? 

@commands_router.message(Command('registration'))
async def cmd_registration(message: Message, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)

        # ПРОВЕРИТЬ ЧТО ПОЛЬЗОВАТЕЛЯ НЕТ В БД!!!
        if not await db.is_user_exist(user_id):
            await message.reply(f"Вы уже зарегистрированы.")
            return
        
        nickname = message.from_user.username or "Unknown"

        # Заносим пользователя в базу данных
        await db.add_user(telegram_user_id=user_id, nickname=nickname)

        await message.reply(f"Вы зарегистрированы!\n")

    else:
        # в таком случае не реагируем
        return
    
    # регистрирует пользователя в базу данных

@commands_router.message(Command('get_users'))
async def cmd_get_users(message: Message, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        
        user_id = str(message.from_user.id)
        nickname = message.from_user.username or "Unknown"

        # Получаем всех пользователей для проверки
        users = await db.get_all_users()

        # Форматируем ответ
        users_list = "\n".join([f"{u['telegram_user_id']} - {u['nickname']}" for u in users])
        await message.reply(f"Список пользователей:\n{users_list}")

    else:
        # в таком случае не реагируем
        return