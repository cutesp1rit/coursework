import os

# ============================
# Класс для работы с диалогами
# ============================

class DialogueService:
    def __init__(self, db, tts_service, audio_service):
        self.db = db
        self.tts_service = tts_service
        self.audio_service = audio_service
        self.voice_output_dir = "/usr/src/app/tg_bot/voice_output"
        
    async def format_dialogue(self, messages: list) -> list:
        formatted_dialogue = []
        current_user = None
        current_text = ""
        current_user_id = None

        for msg in messages:
            user_id = msg['user_id']
            username = msg['username']
            text = msg['message_text']

            # Ограничиваем длину текста для ускорения
            if len(text) > 100:
                text = text[:100]

            user_data = await self.db.users.get_by_id(user_id)
            if user_data:
                nickname = user_data['nickname'] or username
                gender = user_data['gender']
                said = "сказал" if not gender else "сказала"
            else:
                nickname = username
                said = "сказал"

            intro_text = f"{nickname} {said}"

            # если сообщение от "нового" пользователя, добавляем текущий текст в диалог
            if user_id != current_user:
                if current_user is not None:
                    formatted_dialogue.append((current_user_id, current_text))

                current_user = user_id
                current_user_id = user_id
                current_text = f"{text}"
                formatted_dialogue.append((None, intro_text))
            else:
                # если сообщение от того же пользователя, объединяем текст
                current_text += f"\n{text}"

        # добавляем последнее сообщение
        if current_text:
            formatted_dialogue.append((current_user_id, current_text))

        return formatted_dialogue
    
    async def generate_dialogue_audio(self, dialogue_texts, chat_id):
        audio_files = []
        print(dialogue_texts)
        for idx, (user_id, text) in enumerate(dialogue_texts):
            wav_path = os.path.join(self.voice_output_dir, f"chat_{chat_id}_part_{idx}.wav")
            await self.tts_service.generate_voice(
                text=text,
                output_path=wav_path,
                user_id=user_id
            )
            audio_files.append(wav_path)
            
        return self.audio_service.combine_audio_files(audio_files, chat_id)