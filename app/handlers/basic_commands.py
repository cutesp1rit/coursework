from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.handlers import commands_router
from database_vm.database import Database

# Команда start
@commands_router.message(CommandStart())
async def cmd_start(message: Message, db: Database):
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = str(message.from_user.id)
        user_is_registered = await db.users.exists(user_id)

        start_message_private = """
👋 Привет! Я голосовой бот для преобразования текста в речь.

🔹 Озвучиваю сообщения и создаю аудиодиалоги.
🔹 Могу работать с вашим голосом, если загрузите образец.

📌 Доступные команды:
/start - приветственное сообщение
/help - справка о функционале
/vm - озвучить текст (ответьте командой на сообщение)
/vmm - автоозвучка всех текстовых сообщений
/stop_vmm - отключить автоозвучку
"""

        if user_is_registered:  # Проверяем, зарегистрирован ли пользователь
            start_message_private += """
/profile - управление данными вашего профиля
"""
        else:
            start_message_private += """
🚀 Для доступа к полному функционалу (/profile, настройка голоса) используйте /registration.
"""

        await message.answer(start_message_private)

    elif chat_type in ['group', 'supergroup']:
        start_message_group = """
👋 Привет! Я голосовой бот для преобразования текста в речь.

🔹 Озвучиваю сообщения и создаю аудиодиалоги.
🔹 Для работы с профилем и голосом используйте личные сообщения со мной.

📌 Доступные команды:
/start - приветственное сообщение
/help - справка о функционале
/vm - озвучить текст (ответьте командой на сообщение)
/vd <k> - сгенерировать диалог из k сообщений (начиная с того сообщения, на которое вы ответите данной командой)
"""
        await message.answer(start_message_group)
    else:
        # В таком случае не реагируем
        return

# Команда help
@commands_router.message(Command('help'))
async def cmd_help(message: Message):
    help_message = """
ℹ️ Как пользоваться ботом? 

🔹 Для озвучивания текста:  
   - Ответьте командой /vm на сообщение.  
   - Или включите автоозвучку (/vmm) (работает только в личных сообщениях).  

🔹 Для диалогов в группах: /vd 3 (озвучит 3 сообщения, начиная с того, на которое вы ответили).  

🔹 Настройки голоса (при условии, что вы зарегистированы):  
   - Изменить пол: /change_gender 
   - Изменить ник: /change_nickname
   - Изменить голос: /change_voice
   - Удалить данные о себе: /delete_data

📌 Если что-то не работает:  
   - Проверьте, зарегистрированы ли вы (/profile).  
   - Или напишите в поддержку: @cutespirit.  
"""
    await message.reply(help_message)
    
# Команда profile
@commands_router.message(Command('profile'))
async def cmd_profile(message: Message, db: Database):
    chat_type = message.chat.type
    user_id = str(message.from_user.id)

    if chat_type == "private":  # Личный чат
        user = await db.users.get_by_id(user_id)
        if not user:
            await message.answer(
                "🚀 Вы не зарегистрированы.\n"
                "Используйте /registration для доступа к функциям:\n"
                "- Персонализация голоса\n"
                "- Сохранение настроек\n"
                "- История сообщений"
            )
            return
        
        # Форматирование данных профиля
        voice_status = "✅ (используется ваш голос)" if user['voice'] else "🤖 (используется синтезированный голос)"
        gender_text = "Мужской" if not user['gender'] else "Женский"
        gender_emoji = "♂️" if not user['gender'] else "♀️"
        
        profile_text = (
            f"👤 <b>Ваш профиль</b>\n"
            f"├ {gender_emoji} Пол: {gender_text}\n"
            f"├ 📛 Никнейм: {user['nickname'] or 'не установлен'}\n"
            f"├ 🎙 Голос: {voice_status}\n"
            f"└ 🌐 Язык: {user['language']}\n\n"
            f"🔧 <b>Управление профилем</b>:\n"
            f"/change_nickname - изменить никнейм\n"
            f"/change_gender - выбрать пол голоса\n"
            f"/change_voice - загрузить образец голоса\n"
            f"/change_lang - сменить язык\n"
            f"/delete_data - удалить мои данные\n"
        )
        
        await message.answer(profile_text, parse_mode="HTML")
    
    else:  # Групповой чат
        await message.answer(
            "📢 Эту команду можно использовать только в личных сообщениях с ботом."
        )