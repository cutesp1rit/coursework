import asyncio
import os
from aiogram import Bot, Dispatcher
from app.handlers import router
import torch
from TTS.api import TTS
import sys
from io import StringIO

async def main():
    bot = Bot(token=os.environ["bot_token"])
    dp = Dispatcher()
    dp.include_router(router)
    # sys.stdin = StringIO("y\n")
    # Get device
    # device = "cuda" if torch.cuda.is_available() else "cpu"

    # List available 🐸TTS models
    # print(TTS().list_models())
    
    # Init TTS
    # tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    directory_path = "/usr/src/app/tg_bot/voice_input"
    
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path, exist_ok=True)
            print(f"Папка '{directory_path}' успешно создана!")
        except PermissionError:
            print(f"Ошибка: недостаточно прав для создания папки '{directory_path}'.")
        except Exception as e:
            print(f"Ошибка при создании папки: {e}")

    else:
        print(f"Папка '{directory_path}' уже существует.")
    
    directory_path = "/usr/src/app/tg_bot/voice_files"
    
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path, exist_ok=True)
            print(f"Папка '{directory_path}' успешно создана!")
        except PermissionError:
            print(f"Ошибка: недостаточно прав для создания папки '{directory_path}'.")
        except Exception as e:
            print(f"Ошибка при создании папки: {e}")

    else:
        print(f"Папка '{directory_path}' уже существует.")

    await dp.start_polling(bot)

    print("Ты посмотри все хорошо!")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка.. {e}")