from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

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
    
# команда voice message mode (по)
@router.message(Command('vmm'))
async def cmd_vmm(message: Message):
    # проверка на личный чат
    await message.answer('')
    # поменять флаг в бд

@router.message(Command('stop_vmm'))
async def cmd_stop_vmm(message: Message):
    # проверка на личный чат
    await message.answer('')
    # поменять флаг в бд

@router.message(Command('changevoice'))
async def cmd_changevoice(message: Message):
    # проверка на личный чат
    await message.answer('')
    # запросить у пользователя файл + проверка на корректность типа файла
    # возможно добавить возможность с дефолтным голосом?
    # занесение голосового сообщения в базу данных

@router.message(Command('del'))
async def cmd_del(message: Message):
    # проверка на личный чат
    await message.answer('')
    # удаляет пользователя из базы данных (то есть все, что было в регистарции??)

@router.message(Command('registration'))
async def cmd_registration(message: Message):
    # проверка на личный чат
    await message.answer('')
    # регистрирует пользователя в базу данных