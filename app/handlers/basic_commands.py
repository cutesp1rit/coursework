from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.handlers import commands_router

# команда start
@commands_router.message(CommandStart())
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
@commands_router.message(Command('help'))
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