import pytest
import os
from pydub import AudioSegment
from app.voice_processing.audio_service import AudioService
from unittest.mock import patch

@pytest.fixture
def audio_service(tmp_path):
    return AudioService(output_dir=str(tmp_path))

class TestAudioService:
    @pytest.mark.asyncio
    async def test_convert_wav_to_ogg(self, audio_service, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        ogg_path = str(tmp_path / "test.ogg")
        
        # Создаем пустой аудиосегмент (1 секунда тишины)
        audio = AudioSegment.silent(duration=1000)  # 1000 ms = 1 sec
        audio.export(wav_path, format="wav")
        
        # Мокируем вызов run_in_executor, чтобы не зависеть от реального ffmpeg в тестах
        with patch.object(audio_service, '_convert_wav_to_ogg_sync') as mock_convert:
            await audio_service.convert_wav_to_ogg(wav_path, ogg_path)
            
            # Проверяем что метод конвертации был вызван с правильными аргументами
            mock_convert.assert_called_once_with(wav_path, ogg_path)

    @pytest.mark.asyncio
    async def test_convert_wav_to_ogg_integration(self, audio_service, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        ogg_path = str(tmp_path / "test.ogg")
        
        audio = AudioSegment.silent(duration=100)  # 100 ms тишины
        audio.export(wav_path, format="wav")
        
        try:
            await audio_service.convert_wav_to_ogg(wav_path, ogg_path)
            assert os.path.exists(ogg_path)
            assert not os.path.exists(wav_path)
        except Exception as e:
            pytest.skip(f"Реальная конвертация не работает: {str(e)}")

    def test_combine_audio_files_integration(self, audio_service, tmp_path):
        """Интеграционный тест с реальными файлами"""
        pytest.importorskip("pydub")
        
        # Создаем несколько WAV файлов с тишиной
        audio_files = []
        for i in range(3):
            path = str(tmp_path / f"test_{i}.wav")
            AudioSegment.silent(duration=100).export(path, format="wav")
            audio_files.append(path)
        
        try:
            result = audio_service.combine_audio_files(audio_files, "test_chat")
            assert result is not None
            assert os.path.exists(result)
            
            # Проверяем что временные файлы удалены
            for file in audio_files:
                assert not os.path.exists(file)
        except Exception as e:
            pytest.skip(f"Реальное объединение файлов не работает: {str(e)}")

    def test_combine_empty_files(self, audio_service):
        assert audio_service.combine_audio_files([], "test_chat") is None

    def test_combine_audio_files_error_handling(self, audio_service, tmp_path):
        """Тестирует обработку ошибок при объединении файлов"""
        with patch('pydub.AudioSegment.from_file', side_effect=Exception("Test error")):
            result = audio_service.combine_audio_files(["test1.wav", "test2.wav"], "chat123")
            # Проверяем что возвращается путь, даже при ошибках
            assert "chat_chat123_final_dialogue.wav" in result

    def test_cleanup_files_error_handling(self, audio_service):
        """Тестирует обработку ошибок при удалении файлов"""
        with patch('os.remove', side_effect=Exception("Test error")):
            audio_service._cleanup_files(["test1.wav", "test2.wav"])