import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, Chat, User
from app.voice_processing.voice_creator import VoiceCreator

@pytest.fixture
def voice_creator():
    db = AsyncMock()
    return VoiceCreator(db)

@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 123
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 456
    message.from_user.username = "test_user"
    message.text = "Test message"
    message.message_id = 789
    return message

class TestVoiceCreator:
    @pytest.mark.asyncio
    async def test_process_voice_message(self, voice_creator, mock_message):
        # Мокируем все зависимости
        voice_creator.tts_service.generate_voice = AsyncMock()
        voice_creator.audio_service.convert_wav_to_ogg = AsyncMock()
        mock_message.reply_voice = AsyncMock()
        
        # Мокируем файловые операции
        with patch('os.path.exists', return_value=True), \
             patch('os.remove') as mock_remove, \
             patch('os.path.join', side_effect=lambda *args: "/mock/path/" + args[-1]):
            
            await voice_creator.process_voice_message(
                message=mock_message,
                text="Test text",
                user_id="user123"
            )
            
            # Проверяем вызовы
            voice_creator.tts_service.generate_voice.assert_called_once()
            voice_creator.audio_service.convert_wav_to_ogg.assert_called_once()
            mock_message.reply_voice.assert_called_once()
            mock_remove.assert_called_once_with("/mock/path/user123_cloned.ogg")

    @pytest.mark.asyncio
    async def test_process_voice_message_file_not_found(self, voice_creator, mock_message):
        # Мокируем зависимости
        voice_creator.tts_service.generate_voice = AsyncMock()
        voice_creator.audio_service.convert_wav_to_ogg = AsyncMock()
        mock_message.reply = AsyncMock()
        
        # Мокируем os.path.exists чтобы вернуть False
        with patch('os.path.exists', return_value=False):
            await voice_creator.process_voice_message(
                message=mock_message,
                text="Test text",
                user_id="user123"
            )
            
            # Проверяем что было отправлено сообщение об ошибке
            mock_message.reply.assert_called_with("Произошла ошибка при создании аудиофайла.")

    @pytest.mark.asyncio
    async def test_handle_group_message_normal(self, voice_creator, mock_message):
        """Тестирует обработку обычного группового сообщения"""
        voice_creator.db.messages.add = AsyncMock()
        voice_creator.db.messages.get_count = AsyncMock(return_value=999)
        
        await voice_creator.handle_group_message(mock_message)
        
        voice_creator.db.messages.add.assert_called_once()
        voice_creator.db.messages.get_count.assert_called_once_with(str(mock_message.chat.id))

    @pytest.mark.asyncio
    async def test_handle_group_message_with_cleanup(self, voice_creator, mock_message):
        """Тестирует очистку старых сообщений при превышении лимита"""
        voice_creator.db.messages.add = AsyncMock()
        voice_creator.db.messages.get_count = AsyncMock(return_value=1001)
        voice_creator.db.messages.get_oldest_message_id = AsyncMock(return_value="old_123")
        voice_creator.db.messages.delete = AsyncMock()
        
        await voice_creator.handle_group_message(mock_message)
        
        voice_creator.db.messages.delete.assert_called_once_with("old_123")

    @pytest.mark.asyncio
    async def test_process_private_voice_message_success(self, voice_creator, mock_message):
        """Тестирует успешную обработку приватного сообщения"""
        with patch('os.path.exists', return_value=True), \
            patch('os.remove'), \
            patch('app.voice_processing.voice_creator.FSInputFile'):
            
            voice_creator.generate_voice_message = AsyncMock()
            voice_creator.audio_service.convert_wav_to_ogg = AsyncMock()
            mock_message.answer_voice = AsyncMock()
            
            await voice_creator.process_private_voice_message(mock_message, "user123")
            
            mock_message.answer_voice.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_private_voice_message_failure(self, voice_creator, mock_message):
        """Тестирует обработку ошибок в приватном сообщении"""
        with patch('os.path.exists', return_value=False):
            voice_creator.generate_voice_message = AsyncMock()
            voice_creator.audio_service.convert_wav_to_ogg = AsyncMock()
            mock_message.reply = AsyncMock()
            
            await voice_creator.process_private_voice_message(mock_message, "user123")
            
            mock_message.reply.assert_called_with("Произошла ошибка при создании аудиофайла.")

    @pytest.mark.asyncio
    async def test_init_directory_creation_error(self, tmp_path):
        """Тестирует обработку ошибок при создании директорий"""
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            db = AsyncMock()
            with pytest.raises(OSError):
                VoiceCreator(db)

    @pytest.mark.asyncio
    async def test_process_dialogue_flow(self, voice_creator):
        """Тестирует основной сценарий обработки диалога"""
        with patch.object(voice_creator.dialogue_service, 'format_dialogue', 
                        AsyncMock(return_value="formatted")), \
            patch.object(voice_creator.dialogue_service, 'generate_dialogue_audio',
                        AsyncMock(return_value="test.wav")), \
            patch.object(voice_creator.audio_service, 'convert_wav_to_ogg',
                        AsyncMock(return_value="test.ogg")):
            
            result = await voice_creator.process_dialogue([{"user_id": "1"}], "chat123")
            assert result == "test.ogg"