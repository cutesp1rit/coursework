import pytest
from unittest.mock import AsyncMock, patch
from app.voice_processing.tts_service import TTSService

@pytest.fixture
def tts_service():
    db = AsyncMock()
    return TTSService(db)

class TestTTSService:
    @pytest.mark.asyncio
    async def test_generate_voice_with_user_data(self, tts_service):
        # Мокируем вызовы к БД
        tts_service.db.users.get_by_id = AsyncMock(return_value={
            'voice': True,
            'language': 'ru',
            'gender': False
        })
        
        with patch('glob.glob', return_value=['user_voice.wav']):
            with patch.object(tts_service.tts, 'tts_to_file') as mock_tts:
                await tts_service.generate_voice(
                    text="Test text",
                    output_path="output.wav",
                    user_id="user123"
                )
                
                # Проверяем вызовы
                mock_tts.assert_called_once()
                args, kwargs = mock_tts.call_args
                assert kwargs['speaker_wav'] == 'user_voice.wav'
                assert kwargs['language'] == 'ru'

    @pytest.mark.asyncio
    async def test_generate_voice_with_defaults(self, tts_service):
        # Мокируем вызовы к БД (пользователь не найден)
        tts_service.db.users.get_by_id = AsyncMock(return_value=None)
        
        with patch.object(tts_service.tts, 'tts_to_file') as mock_tts:
            # Вызываем тестируемый метод
            await tts_service.generate_voice(
                text="Test text",
                output_path="output.wav",
                user_id="user123"
            )
            
            # Проверяем вызовы
            mock_tts.assert_called_once()
            args, kwargs = mock_tts.call_args
            assert kwargs['speaker'] == 'Filip Traverse'
            assert kwargs['language'] == 'ru'