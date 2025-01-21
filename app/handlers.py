from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.database import Database

import asyncpg

router = Router()

# команда start
@router.message(CommandStart())
async def cmd_start(message: Message):
    # описание бота и его команд

    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    elif chat_type in ['group', 'supergroup']:
        # это групповой чат
        await message.reply("Это групповой чат.")
    else:
        # в таком случае не реагируем
        return

# команда help
@router.message(Command('help'))
async def cmd_help(message: Message):
    # возможные ответы на вопросы
    
    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    elif chat_type in ['group', 'supergroup']:
        # это групповой чат
        await message.reply("Это групповой чат.")
    else:
        # в таком случае не реагируем
        return

# команда voice message (отправляет сгенерированное аудио)
@router.message(Command('vm'))
async def cmd_vm(message: Message):
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
@router.message(Command('vd'))
async def cmd_vd(message: Message):
    # проверяем на то, что сообщение не слишком давнее + количество сообщений (флаг) парсим

    # проверка на групповой чат
    chat_type = message.chat.type

    if chat_type in ['group', 'supergroup']:
        # это групповой чат
        await message.reply("Это групповой чат.")
    else:
        # в таком случае не реагируем
        return
    
# команда voice message mode (устанавливаем "мод" постоянной генерации аудиосообщений на любой текст)
@router.message(Command('vmm'))
async def cmd_vmm(message: Message):\

    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    else:
        # в таком случае не реагируем
        return
    
    # поменять флаг в бд

# команда stop voice message mode (оставнавливает "мод" постоянной генерации аудиосообщений на любой текст)
@router.message(Command('stop_vmm'))
async def cmd_stop_vmm(message: Message):
    
    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    else:
        # в таком случае не реагируем
        return
    
    await message.answer('')
    # поменять флаг в бд

# команда change voice (изменяет текущее или устанавливает новое аудиосообщение пользователя для дальнейшей генерации)
@router.message(Command('change_voice'))
async def cmd_changevoice(message: Message):

    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    else:
        # в таком случае не реагируем
        return
    
    # запросить у пользователя файл + проверка на корректность типа файла
    # возможно добавить возможность с дефолтным голосом?
    # занесение голосового сообщения в базу данных

@router.message(Command('del'))
async def cmd_del(message: Message):
    chat_type = message.chat.type

    if chat_type == 'private':
        # это личный чат
        await message.reply("Это личный чат.")
    else:
        # в таком случае не реагируем
        return
    
    # удаляет пользователя из базы данных (то есть все, что было в регистарции??)

@router.message(Command('registration'))
async def cmd_registration(message: Message,  db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        
        user_id = str(message.from_user.id)
        nickname = message.from_user.username or "Unknown"

        # Получаем доступ к базе данных
        # db = message.bot['db']

        # Заносим пользователя в базу данных
        await db.add_user(telegram_user_id=user_id, nickname=nickname)

        # Получаем всех пользователей для проверки
        users = await db.get_all_users()

        # Форматируем ответ
        users_list = "\n".join([f"{u['telegram_user_id']} - {u['nickname']}" for u in users])
        await message.reply(f"Вы зарегистрированы!\n\nСписок пользователей:\n{users_list}")

    else:
        # в таком случае не реагируем
        return
    
    # регистрирует пользователя в базу данных