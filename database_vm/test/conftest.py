import pytest
from database_vm.database import Database
from datetime import datetime

@pytest.fixture
async def db():
    """Основная фикстура для работы с БД"""
    db = Database()
    await db.connect()
    await db.init_tables()
    try:
        yield db
    finally:
        await db.drop_all_tables()
        await db.connection.disconnect()

@pytest.fixture
async def db_with_data(db):
    """Фикстура с тестовыми данными"""
    # Добавляем тестовых пользователей
    await db.users.add("user1", True, "Alice", False, "en")
    await db.users.add("user2", False, "Bob", True, "ru")
    
    # Добавляем тестовые сообщения
    await db.messages.add("msg1", "chat1", "user1", "Alice", "Hello", datetime.now())
    await db.messages.add("msg2", "chat1", "user2", "Bob", "Hi there", datetime.now())
    
    return db