import os
from datetime import datetime
from aiogram.types import Message, FSInputFile
from database.database import Database
from app.voice_processing.tts_service import TTSService 
from app.voice_processing.audio_service import AudioService
from app.voice_processing.dialogue_service import DialogueService

class VoiceCreator:
    def __init__(self, db: Database):
        self.voice_input_dir = "/usr/src/app/tg_bot/voice_input"
        self.voice_output_dir = "/usr/src/app/tg_bot/voice_output"
        self.final_output_dir = "/usr/src/app/tg_bot/voice_files"
        
        os.makedirs(self.voice_output_dir, exist_ok=True)
        os.makedirs(self.final_output_dir, exist_ok=True)
        
        self.db = db
        self.tts_service = TTSService(db)
        self.audio_service = AudioService(self.final_output_dir) 
        self.dialogue_service = DialogueService(db, self.tts_service, self.audio_service)

    async def generate_voice_message(self, text: str, user_id: str, output_path: str):
        await self.tts_service.generate_voice(text, output_path, user_id=user_id)

    async def handle_group_message(self, message: Message):
        chat_id = str(message.chat.id)
        user_id = str(message.from_user.id)
        username = message.from_user.username
        message_text = message.text
        created_at = datetime.now()

        await self.db.messages.add(
            message_id=str(message.message_id),
            chat_id=chat_id,
            user_id=user_id,
            username=username,
            message_text=message_text,
            created_at=created_at,
        )

        message_count = await self.db.messages.get_count(chat_id)
        if message_count > 1000:
            oldest_message_id = await self.db.messages.get_oldest_message_id(chat_id)
            if oldest_message_id:
                await self.db.messages.delete(oldest_message_id)

    async def process_dialogue(self, messages: list, chat_id: str):
        """Обрабатывает диалог и создает аудио"""
        formatted_dialogue = await self.dialogue_service.format_dialogue(messages)
        final_path = await self.dialogue_service.generate_dialogue_audio(formatted_dialogue, chat_id)
        
        if final_path:
            ogg_path = final_path.replace('.wav', '.ogg')
            await self.audio_service.convert_wav_to_ogg(final_path, ogg_path)
            return ogg_path
        return None

    async def process_voice_message(self, message: Message, text: str, user_id: str):
        """Обрабатывает команду генерации голосового сообщения"""
        output_path_wav = os.path.join(self.voice_output_dir, f"{user_id}_cloned.wav")
        output_path_ogg = os.path.join(self.voice_output_dir, f"{user_id}_cloned.ogg")

        await self.generate_voice_message(text, user_id, output_path_wav)
        await self.audio_service.convert_wav_to_ogg(output_path_wav, output_path_ogg)

        if not os.path.exists(output_path_ogg):
            await message.reply("Произошла ошибка при создании аудиофайла.")
            return

        voice_file = FSInputFile(output_path_ogg)
        await message.reply_voice(voice_file)

        if os.path.exists(output_path_ogg):
            os.remove(output_path_ogg)

    async def process_private_voice_message(self, message: Message, user_id: str):
        """Обрабатывает приватное голосовое сообщение"""
        output_path_wav = os.path.join(self.voice_output_dir, f"{user_id}_cloned.wav")
        output_path_ogg = os.path.join(self.voice_output_dir, f"{user_id}_cloned.ogg")

        await self.generate_voice_message(message.text, user_id, output_path_wav)
        await self.audio_service.convert_wav_to_ogg(output_path_wav, output_path_ogg)
        
        if not os.path.exists(output_path_ogg):
            await message.reply("Произошла ошибка при создании аудиофайла.")
            return

        voice_file = FSInputFile(output_path_ogg)
        await message.answer_voice(voice_file)

        if os.path.exists(output_path_ogg):
            os.remove(output_path_ogg)