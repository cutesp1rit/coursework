import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import router
from database.database import Database

async def main():
    bot = Bot(token=os.environ["bot_token"])

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    db = Database()

    dp["bot"] = bot
    dp["db"] = db

    # Подключение к базе данных
    await db.connect()
    await db.init_tables()

    dp.include_router(router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка.. {e}")