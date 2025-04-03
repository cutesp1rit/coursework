import pytest
from unittest.mock import AsyncMock, MagicMock
from app.voice_processing.dialogue_service import DialogueService

@pytest.fixture
def dialogue_service():
    db = AsyncMock()
    tts_service = AsyncMock()
    audio_service = MagicMock()
    return DialogueService(db, tts_service, audio_service)

class TestDialogueService:
    @pytest.mark.asyncio
    async def test_format_dialogue(self, dialogue_service):
        # Подготовка тестовых данных
        test_messages = [
            {'user_id': 'user1', 'username': 'User1', 'message_text': 'Hello'},
            {'user_id': 'user2', 'username': 'User2', 'message_text': 'Hi there'},
            {'user_id': 'user1', 'username': 'User1', 'message_text': 'How are you?'}
        ]
        
        # Мокируем вызовы к БД
        dialogue_service.db.users.get_by_id = AsyncMock(side_effect=[
            {'nickname': 'User1', 'gender': False},
            {'nickname': 'User2', 'gender': True},
            {'nickname': 'User1', 'gender': False}
        ])
        
        result = await dialogue_service.format_dialogue(test_messages)
        
        # Проверяем результат
        assert len(result) == 6  # 3 вступления (для каждого нового сообщения от пользователя) + 3 сообщения
        assert result[0] == (None, "User1 сказал")
        assert result[1] == ('user1', "Hello")
        assert result[2] == (None, "User2 сказала")
        assert result[3] == ('user2', "Hi there")
        assert result[4] == (None, "User1 сказал")
        assert result[5] == ('user1', "How are you?")

    @pytest.mark.asyncio
    async def test_generate_dialogue_audio(self, dialogue_service):
        test_dialogue = [
            (None, "User1 сказал"),
            ('user1', "Hello"),
            (None, "User2 сказала"),
            ('user2', "Hi there")
        ]
        
        # Мокируем вызовы
        dialogue_service.tts_service.generate_voice = AsyncMock()
        dialogue_service.audio_service.combine_audio_files = MagicMock(return_value="final.wav")
        
        result = await dialogue_service.generate_dialogue_audio(test_dialogue, "chat123")
        
        # Проверяем результат
        assert result == "final.wav"
        assert dialogue_service.tts_service.generate_voice.call_count == 4
        dialogue_service.audio_service.combine_audio_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_format_dialogue_empty_input(self, dialogue_service):
        """Тестирует обработку пустого списка сообщений"""
        result = await dialogue_service.format_dialogue([])
        assert result == []

    @pytest.mark.asyncio
    async def test_format_dialogue_error_handling(self, dialogue_service):
        """Тестирует обработку ошибок при форматировании"""
        dialogue_service.db.users.get_by_id = AsyncMock(side_effect=Exception("DB error"))
        result = await dialogue_service.format_dialogue([{"user_id": "1", "message_text": "test"}])
        assert result == []

    @pytest.mark.asyncio
    async def test_generate_dialogue_audio_error_handling(self, dialogue_service):
        """Тестирует обработку ошибок при генерации аудио"""
        dialogue_service.tts_service.generate_voice = AsyncMock(side_effect=Exception("TTS error"))
        dialogue_service.audio_service.combine_audio_files = MagicMock()
        
        result = await dialogue_service.generate_dialogue_audio([("1", "test")], "chat123")
        assert result is None        
        dialogue_service.audio_service.combine_audio_files.assert_not_called()
