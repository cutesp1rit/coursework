import pytest
from datetime import datetime

class TestChatMessageRepository:
    @pytest.mark.asyncio
    async def test_message_lifecycle(self, db):
        """Тест жизненного цикла сообщений"""
        # Добавляем тестового данные
        await db.users.add(111222333, True, "Sender", False)
        await db.messages.add(
            123456789, 987654321, 111222333, "Sender", 
            "Test message", datetime.now()
        )
        
        # Проверяем добавленное
        assert await db.messages.get_count(987654321) == 1
        assert await db.messages.get_oldest_message_id(987654321) == 123456789
        
        # Удаляем и проверяем
        await db.messages.delete(123456789)
        assert await db.messages.get_count(987654321) == 0

    @pytest.mark.asyncio
    async def test_dialogue_operations(self, db_with_data):
        """Тест работы с диалогами"""
        messages = await db_with_data.messages.get_dialogue_messages(
            123456789, 987654321, 10
        )
        assert len(messages) == 2
        assert messages[0]["message_text"] == "Hello"