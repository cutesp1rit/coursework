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
    await db.users.add(111222333, True, "Alice", False, "en")
    await db.users.add(444555666, False, "Bob", True, "ru")
    
    # Добавляем тестовые сообщения
    await db.messages.add(123456789, 987654321, 111222333, "Alice", "Hello", datetime.now())
    await db.messages.add(234567890, 987654321, 444555666, "Bob", "Hi there", datetime.now())
    
    return db