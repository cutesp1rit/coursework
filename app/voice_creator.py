import os, sys, glob, torch, datetime, asyncio
from io import StringIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from pydub import AudioSegment
from TTS.api import TTS
from aiogram.types import Message

from database.database import Database


voice_input_dir = "/usr/src/app/tg_bot/voice_input"

sys.stdin = StringIO("y\n")
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
# Установка параметров для ускорения генерации
tts.synthesizer.tts_model.inference_noise_scale = 0.2 # шум
tts.synthesizer.tts_model.length_scale = 0.7  # темп речи
tts.synthesizer.tts_model.inference_noise_scale_dp = 0.1  # шум

final_output_dir = "/usr/src/app/tg_bot/voice_files"
os.makedirs(final_output_dir, exist_ok=True)

# Создаем пул исполнителей для ограничения параллельных задач
executor_pool = ThreadPoolExecutor(max_workers=3)

async def generate_voice_message(text: str, user_id: str, db: Database, voice_dir: str):
    user_data = await db.users.get_by_id(user_id)
    uses_custom_voice = user_data and user_data.get("voice", False)
    language = user_data.get("language", "ru") if user_data else "ru"
    gender = user_data.get("gender", False) if user_data else False

    file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")
    matching_files = glob.glob(file_pattern)
    user_voice_path = matching_files[0] if matching_files else None

    # Используем ограниченный пул исполнителей для предотвращения перегрузки системы
    if uses_custom_voice and user_voice_path:
        await asyncio.get_event_loop().run_in_executor(
            executor_pool,
            lambda: tts.tts_to_file(
                text=text,
                speaker_wav=user_voice_path,
                file_path=voice_dir,
                language=language,
                speed=2
            )
        )
    else:
        speaker = "Ana Florence" if gender else "Filip Traverse"
        await asyncio.get_event_loop().run_in_executor(
            executor_pool,
            lambda: tts.tts_to_file(
                text=text,
                speaker=speaker,
                file_path=voice_dir,
                language=language,
                speed=2
            )
        )

# формирует сообщения в список на генерацию аудио диалога
async def format_dialogue(messages: list, db: Database) -> list:
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

        user_data = await db.users.get_by_id(user_id)
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
            formatted_dialogue.append(("", intro_text))
        else:
            # если сообщение от того же пользователя, объединяем текст
            current_text += f"\n{text}"

    # добавляем последнее сообщение
    if current_text:
        formatted_dialogue.append((current_user_id, current_text))

    return formatted_dialogue


# генерирует итоговое голосовое сообщение для каждой реплики
async def generate_audio_for_dialogue(dialogue_texts, chat_id, db):
    output_dir = "/usr/src/app/tg_bot/voice_files"
    os.makedirs(output_dir, exist_ok=True)

    audio_files = []
    
    # Генерируем последовательно, чтобы не перегружать систему
    for idx, (user_id, text) in enumerate(dialogue_texts):
        wav_output_path = os.path.join(output_dir, f"chat_{chat_id}_part_{idx}.wav")
        
        await generate_voice_message(
            text=text,
            user_id=user_id,
            db=db,
            voice_dir=wav_output_path
        )
        audio_files.append(wav_output_path)

    return audio_files

# соединяет все аудио в одно
def combine_audio_files(audio_files: list, chat_id: str) -> str:
    if not audio_files:
        # соединять нечего
        return

    combined = AudioSegment.empty()

    for file_path in audio_files:
        try:
            audio = AudioSegment.from_file(file_path)
            # Ускоряем аудио для более быстрого воспроизведения
            audio = audio.speedup(playback_speed=1.2)
            combined += audio
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

    final_path = os.path.join(final_output_dir, f"chat_{str(chat_id)}_final_dialogue.wav")

    try:
        # Экспортируем с пониженным качеством (для ускорения)
        combined.export(final_path, format="wav", parameters=["-q:a", "0"])
        print(f"Файл успешно сохранен: {final_path}")
    except Exception as e:
        pass

    for file_path in audio_files:
        try:
            os.remove(file_path)
            print(f"Удален временный файл: {file_path}")
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")

    return final_path

# конвертирует аудиофайл из формата WAV в OGG.
async def convert_wav_to_ogg(wav_path: str, ogg_path: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: _convert_wav_to_ogg_sync(wav_path, ogg_path))

def _convert_wav_to_ogg_sync(wav_path: str, ogg_path: str):
    audio = AudioSegment.from_wav(wav_path)
    # Экспортируем с пониженным качеством (для ускорения)
    audio.export(ogg_path, format="ogg", parameters=["-q:a", "0"])

    if os.path.exists(wav_path):
        os.remove(wav_path)

# обработка текстового сообщения в групповых чатах
async def handle_group_message(message: Message, db: Database):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    username = message.from_user.username
    message_text = message.text
    created_at = datetime.now()

    await db.messages.add(
        message_id=str(message.message_id),
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_text=message_text,
        created_at=created_at,
    )

    message_count = await db.messages.get_count(chat_id)

    # если сообщений больше 1000, удаляем самое старое
    if message_count > 1000:
        oldest_message_id = await db.messages.get_oldest_message_id(chat_id)
        if oldest_message_id:
            await db.messages.delete(oldest_message_id)