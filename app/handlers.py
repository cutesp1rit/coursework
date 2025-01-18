from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from TTS.api import TTS

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Привет! Чтобы пользоваться полным функционалом бота.. Вот здесь модели {TTS().list_models()}")

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Возможные вопросы и ответы к ним...')
    # something

@router.message(Command('vm'))
async def cmd_vm(message: Message):
    await message.answer('')
    # проверка на наличие голоса пользователя в БД

    # отправляем с дефолтным если что

@router.message(Command('vd'))
async def cmd_vd(message: Message):
    await message.answer('')

    # проверяем на то, что сообщение не слишком давнее + количество сообщений (флаг) парсим

@router.message(Command('vmm'))
async def cmd_vmm(message: Message):
    await message.answer('')
    # поменять флаг в бд

@router.message(Command('stop_vmm'))
async def cmd_stop_vmm(message: Message):
    await message.answer('')
    # поменять флаг в бд

@router.message(Command('changevoice'))
async def cmd_changevoice(message: Message):
    await message.answer('')

    # запросить у пользователя файл + проверка на корректность типа файла
    # занесение голосового сообщения в базу данных

@router.message(Command('del'))
async def cmd_del(message: Message):
    await message.answer('')

    # удаляет пользователя из базы данных