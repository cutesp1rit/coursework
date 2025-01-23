import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database.database import Database

# подключение роутеров
from app.handlers import commands_router
from app.handlers.voice_creator import voice_router
from app.handlers.user_management import user_management_router
import app.handlers.basic_commands


def register_all_handlers(dp):
    for router in [
        commands_router,
        user_management_router,
        voice_router
    ]:
        dp.include_router(router)

async def main():
    bot = Bot(token=os.environ["bot_token"])

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    db = Database()

    dp["bot"] = bot
    dp["db"] = db

    # Подключение к базе данных
    await db.connect()
    await db.drop_all_tables()
    await db.init_tables()

    register_all_handlers(dp)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Произошла непредвиденная ошибка.. {e}")