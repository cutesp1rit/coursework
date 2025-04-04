from pydub import AudioSegment
import os
import asyncio

# ========================
# Класс для работы с аудио
# ========================

class AudioService:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    async def convert_wav_to_ogg(self, wav_path: str, ogg_path: str):
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self._convert_wav_to_ogg_sync,
                wav_path,
                ogg_path
            )
        except Exception as e:
            print(f"Ошибка при конвертации WAV в OGG: {e}")
    
    def _convert_wav_to_ogg_sync(self, wav_path: str, ogg_path: str):
        try:
            audio = AudioSegment.from_wav(wav_path)
            
            audio.export(
                ogg_path,
                format="ogg", 
                codec="libopus",  # Используем Opus для формата голосового сообщения в Telegram
                bitrate="24k",
                parameters=[
                    "-ar", "24000",
                    "-ac", "1",
                    "-vbr", "on",
                    "-compression_level", "6"
                ]
            )
            
            if os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as e:
            print(f"Ошибка при синхронной конвертации WAV в OGG: {e}")
            raise
            
    def combine_audio_files(self, audio_files: list, chat_id: str) -> str:
        if not audio_files:
            # соединять нечего
            return None
            
        combined = AudioSegment.empty()
        for file_path in audio_files:
            try:
                audio = AudioSegment.from_file(file_path)
                # Ускоряем аудио для более быстрого воспроизведения
                audio = audio.speedup(playback_speed=1.2)
                combined += audio
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")
                
        final_path = os.path.join(self.output_dir, f"chat_{chat_id}_final_dialogue.wav")
        
        try:
            # Экспортируем с пониженным качеством (для ускорения)
            combined.export(final_path, format="wav", parameters=["-q:a", "0"])
            print(f"Файл успешно сохранен: {final_path}")
        except Exception as e:
            print(f"Ошибка при сохранении файла {final_path}: {e}")
            pass
        
        self._cleanup_files(audio_files)
        return final_path
        
    def _cleanup_files(self, files: list):
        for file_path in files:
            try:
                os.remove(file_path)
                print(f"Удален временный файл: {file_path}")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")