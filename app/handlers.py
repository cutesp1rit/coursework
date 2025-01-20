from aiogram import F, Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
import torch
from TTS.api import TTS
import os

router = Router()

# Папки для сохранения входящих и исходящих голосовых сообщений
voice_input_dir = "/usr/src/app/tg_bot/voice_input"
voice_output_dir = "/usr/src/app/tg_bot/voice_files"

# Убедиться, что папки существуют
os.makedirs(voice_input_dir, exist_ok=True)
os.makedirs(voice_output_dir, exist_ok=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Отправьте файл в формате WAV, чтобы бот его обработал.")

@router.message(F.text)
async def handle_text_message(message: Message):
    # Определяем устройство (CPU или CUDA)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Инициализируем TTS модель для клонирования голоса
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Текст для синтеза
    text = message.text
    output_path = os.path.join(voice_output_dir, f"{message.from_user.id}_cloned.wav")
    # Выберите спикера
    speaker = "Abrahan Mack"  # Или "Ana Florence" "Craig Gutsy" для женского голоса
    language = "ru"  # Укажите язык (русский)

    # Генерация речи
    tts.tts_to_file(text=text, speaker=speaker, language=language, file_path=output_path)

    # Отправляем сгенерированное голосовое сообщение обратно пользователю
    voice_file = FSInputFile(output_path)
    await message.answer_voice(voice_file)
    
@router.message(F.document)
async def process_voice_file(message: Message):
    try:
        # Получаем информацию о присланном файле
        document = message.document

        # Путь для сохранения входящего файла
        wav_path = os.path.join(voice_input_dir, f"{message.from_user.id}_input.wav")
        output_path = os.path.join(voice_output_dir, f"{message.from_user.id}_cloned.wav")

        # Скачиваем файл на сервер
        file_info = await message.bot.get_file(document.file_id)
        file_url = file_info.file_path
        await message.bot.download_file(file_url, destination=wav_path)

        # Определяем устройство (CPU или CUDA)
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Инициализируем TTS модель для клонирования голоса
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        # Текст для генерации
        text_to_say = "Привет! У тебя получилось! Все работает!"
        tts.tts_to_file(
            text=text_to_say,
            speaker_wav=wav_path,  # Используем голос из присланного файла
            file_path=output_path,
            language="ru"  # Указываем язык текста
        )

        # Отправляем сгенерированное голосовое сообщение обратно пользователю
        voice_file = FSInputFile(output_path)
        await message.answer_voice(voice_file)

    except Exception as e:
        # Отправляем сообщение об ошибке
        await message.answer(f"Произошла ошибка при обработке файла: {e}")
