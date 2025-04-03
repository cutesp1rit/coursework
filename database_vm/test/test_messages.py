import pytest
from datetime import datetime

class TestChatMessageRepository:
    @pytest.mark.asyncio
    async def test_message_lifecycle(self, db):
        """Тест жизненного цикла сообщений"""
        # Добавляем тестового данные
        await db.users.add("sender", True, "Sender", False)
        await db.messages.add(
            "msg1", "chat1", "sender", "Sender", 
            "Test message", datetime.now()
        )
        
        # Проверяем добавленное
        assert await db.messages.get_count("chat1") == 1
        assert await db.messages.get_oldest_message_id("chat1") == "msg1"
        
        # Удаляем и проверяем
        await db.messages.delete("msg1")
        assert await db.messages.get_count("chat1") == 0

    @pytest.mark.asyncio
    async def test_dialogue_operations(self, db_with_data):
        """Тест работы с диалогами"""
        messages = await db_with_data.messages.get_dialogue_messages(
            "msg1", "chat1", 10
        )
        assert len(messages) == 2
        assert messages[0]["message_text"] == "Hello"