import os
import glob
import torch
import asyncio
from io import StringIO
import sys
from TTS.api import TTS
from concurrent.futures import ThreadPoolExecutor
from database.database import Database

# ============================
# Класс для TTS сервиса
# ============================

class TTSService:
    def __init__(self, db: Database):
        sys.stdin = StringIO("y\n")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = self._initialize_tts()
        self.executor_pool = ThreadPoolExecutor(max_workers=3)
        self.voice_input_dir = "/usr/src/app/tg_bot/voice_input"
        self.db = db
        
    def _initialize_tts(self):
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            tts.synthesizer.tts_model.inference_noise_scale = 0.2
            tts.synthesizer.tts_model.length_scale = 0.7
            tts.synthesizer.tts_model.inference_noise_scale_dp = 0.1
            return tts
        except Exception as e:
            print(f"Ошибка при инициализации TTS модели: {e}")
    
    async def generate_voice(self, text: str, output_path: str, user_id: str = None, speaker_wav=None, speaker="Filip Traverse", language="ru", speed=2):
        print(f"Generating voice for user: {user_id}")
        try:
            if user_id:
                user_data = await self.db.users.get_by_id(user_id)
                uses_custom_voice = user_data and user_data.get("voice", False)
                language = user_data.get("language", "ru") if user_data else "ru"
                gender = user_data.get("gender", False) if user_data else False
                
                file_pattern = os.path.join(self.voice_input_dir, f"{user_id}.*")
                matching_files = glob.glob(file_pattern)
                user_voice_path = matching_files[0] if matching_files else None
                
                if uses_custom_voice and user_voice_path:
                    speaker_wav = user_voice_path
                else:
                    speaker = "Ana Florence" if gender else "Filip Traverse"
            
            await asyncio.get_event_loop().run_in_executor(
                self.executor_pool,
                lambda: self._generate_voice_sync(text, output_path, speaker_wav, speaker, language, speed)
            )
        except Exception as e:
            print(f"Ошибка при подготовке генерации голоса: {e}")
    
    def _generate_voice_sync(self, text, output_path, speaker_wav=None, speaker="Filip Traverse", language="ru", speed=2):
        try:
            if speaker_wav:
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    file_path=output_path,
                    language=language,
                    speed=speed
                )
            else:
                self.tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=output_path,
                    language=language,
                    speed=speed
                )
        except Exception as e:
            print(f"Ошибка при генерации голоса: {e}")