import os, sys, glob, torch, datetime
from io import StringIO
from datetime import datetime

from pydub import AudioSegment
from TTS.api import TTS
from aiogram.types import Message

from database.database import Database


voice_input_dir = "/usr/src/app/tg_bot/voice_input"

sys.stdin = StringIO("y\n")
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

final_output_dir = "/usr/src/app/tg_bot/voice_files"
os.makedirs(final_output_dir, exist_ok=True)

async def generate_voice_message(text: str, user_id: str, db : Database, voice_dir : str):
    user_data = await db.get_user_by_id(user_id)
    uses_custom_voice = user_data and user_data.get("voice", False)

    file_pattern = os.path.join(voice_input_dir, f"{user_id}.*")
    matching_files = glob.glob(file_pattern)
    user_voice_path = matching_files[0] if matching_files else None

    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    if uses_custom_voice and user_voice_path:
        # await message.reply("Генерирую аудио с вашим индивидуальным голосом...")
        tts.tts_to_file(
            text=text,
            speaker_wav=user_voice_path,
            file_path=voice_dir,
            language="ru"
        )
    else:
        # await message.reply("Генерирую аудио с дефолтным голосом...")
        tts.tts_to_file(
            text=text,
            speaker="Ana Florence",
            file_path=voice_dir,
            language="ru"
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

        user_data = await db.get_user_by_id(user_id)
        if user_data:
            nickname = user_data['nickname'] or username
            gender = user_data['gender']
            said = "сказал" if not gender else "сказала"
        else:
            nickname = username
            said = "сказал"

        # если сообщение от "нового" пользователя, добавляем текущий текст в диалог
        if user_id != current_user:
            if current_user is not None:
                formatted_dialogue.append((current_user_id, current_text))  # Сохраняем user_id

            current_user = user_id
            current_user_id = user_id  # Запоминаем user_id
            current_text = f"{nickname} {said}: {text}"
        else:
            # если сообщение от того же пользователя, то можем объединять
            current_text += f"\n{text}"

    # добавляем последнее сообщение
    if current_text:
        formatted_dialogue.append((current_user_id, current_text))  # Сохраняем user_id

    return formatted_dialogue


# генерирует итоговое голосовое сообщение для каждой реплики
async def generate_audio_for_dialogue(dialogue_texts, chat_id, db):
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    output_dir = "/usr/src/app/tg_bot/voice_files"
    os.makedirs(output_dir, exist_ok=True)

    audio_files = []

    for idx, (user_id, text) in enumerate(dialogue_texts):
        wav_output_path = os.path.join(output_dir, f"chat_{chat_id}_part_{idx}.wav")
        
        # генерируем голосовое сообщение на основе данных пользователя
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
            combined += audio
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

    final_path = os.path.join(final_output_dir, f"chat_{str(chat_id)}_final_dialogue.wav")

    try:
        combined.export(final_path, format="wav")
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
def convert_wav_to_ogg(wav_path: str, ogg_path: str):
    audio = AudioSegment.from_wav(wav_path)
    audio.export(ogg_path, format="ogg")

    if os.path.exists(wav_path):
        os.remove(wav_path)

# обработка текстового сообщения в групповых чатах
async def handle_group_message(message: Message, db: Database):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    username = message.from_user.username
    message_text = message.text
    created_at = datetime.now()

    await db.add_chat_message(
        message_id=str(message.message_id),
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_text=message_text,
        created_at=created_at,
    )

    message_count = await db.get_message_count(chat_id)

    # если сообщений больше 1000, удаляем самое старое
    if message_count > 1000:
        oldest_message_id = await db.get_oldest_message_id(chat_id)
        if oldest_message_id:
            await db.delete_message(oldest_message_id)