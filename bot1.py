# Верно работающий самый последний по обновлению и включенный бот

import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты aiogram
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Импорт конфигурации
try:
    from config import BOT_TOKEN, ADMIN_ID
except ImportError:
    print("ОШИБКА: Файл config.py не найден или содержит ошибки!")
    print("Создайте файл config.py со следующими строками:")
    print("BOT_TOKEN = 'ваш_токен'")
    print("ADMIN_ID = 5726686565")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словари для хранения данных
user_sessions = {}
pending_replies = {}

# =================== КЛАВИАТУРЫ ===================

def get_user_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📨 Отправить сообщение")],
            [KeyboardButton(text="❓ Как это работает?")],
        ],
        resize_keyboard=True
    )
    return keyboard

def get_admin_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📖 Команды")],
            [KeyboardButton(text="👥 Все отправители"), KeyboardButton(text="🔄 Ссылка на бота")],
            [KeyboardButton(text="📨 Ответить кому-то"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_message_actions_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_{user_id}"),
                InlineKeyboardButton(text="👤 Инфо", callback_data=f"info_{user_id}")
            ]
        ]
    )
    return keyboard

# =================== КОМАНДЫ ===================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 Привет, хозяин!\n\n"
            "Я — твой личный бот для анонимных сообщений.\n\n"
            "Используй меню ниже или команды:\n"
            "/help — список команд\n"
            "/stats — статистика\n"
            "/users — все отправители\n"
            "/link — ссылка на бота\n\n"
            "Чтобы ответить на сообщение:\n"
            "1. Нажми кнопку 💬 Ответить\n"
            "2. Или просто reply на сообщение",
            reply_markup=get_admin_main_keyboard()
        )
    else:
        await message.answer(
            "Дарова\n\n"
            "Это бот для анонимок. Что угодно, что ты отправишь сюда, придёт ко мне.\n\n"
            "Можешь хоть сиськи скинуть, я не против.",
            reply_markup=get_user_main_keyboard()
        )

@dp.message(Command("help"))
@dp.message(F.text == "📖 Команды")
@dp.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "📚 КОМАНДЫ ДЛЯ АДМИНА:\n\n"
            "/start — главное меню\n"
            "/help — эта справка\n"
            "/stats — статистика\n"
            "/users — список отправителей\n"
            "/link — ссылка на бота\n"
            "/broadcast — рассылка\n"
            "/cancel — отмена ответа\n\n"
            "БЫСТРЫЕ КНОПКИ:\n"
            "📊 Статистика\n"
            "👥 Все отправители\n"
            "🔄 Ссылка на бота\n"
            "📨 Ответить кому-то",
            reply_markup=get_admin_main_keyboard()
        )
    else:
        await message.answer(
            "ℹ️ КАК ПОЛЬЗОВАТЬСЯ:\n\n"
            "1. Нажми 📨 Отправить сообщение\n"
            "2. Или просто напиши текст\n"
            "3. Можно отправить фото, видео, голосовое\n"
            "4. Твоё имя будет скрыто\n"
            "5. Можешь получить ответ\n\n"
            "Всё просто! Попробуй :)",
            reply_markup=get_user_main_keyboard()
        )

@dp.message(Command("stats"))
@dp.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    total = len(user_sessions)
    text_msgs = sum(1 for data in user_sessions.values() if data.get('type') == 'text')
    media_msgs = sum(1 for data in user_sessions.values() if data.get('type') == 'media')
    
    await message.answer(
        f"📊 СТАТИСТИКА:\n\n"
        f"👥 Уникальных отправителей: {total}\n"
        f"📝 Текстовых сообщений: {text_msgs}\n"
        f"📎 Медиа-сообщений: {media_msgs}\n"
        f"🔄 Всего: {text_msgs + media_msgs}",
        reply_markup=get_admin_main_keyboard()
    )

@dp.message(Command("users"))
@dp.message(F.text == "👥 Все отправители")
async def cmd_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not user_sessions:
        await message.answer("📭 Пока никто не писал")
        return
    
    users_text = "👥 Все отправители:\n\n"
    for i, (user_id, user_data) in enumerate(user_sessions.items(), 1):
        name = user_data.get('first_name', 'Без имени')
        users_text += f"{i}. {name} (ID: {user_id})\n"
    
    await message.answer(users_text)

@dp.message(Command("link"))
@dp.message(F.text == "🔄 Ссылка на бота")
async def cmd_link(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    
    await message.answer(
        f"🔗 Ссылка на бота:\n\n"
        f"{bot_link}\n\n"
        f"Отправь друзьям эту ссылку!",
        reply_markup=get_admin_main_keyboard()
    )

@dp.message(F.text == "📨 Ответить кому-то")
async def handle_reply_to_someone(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not user_sessions:
        await message.answer("📭 Пока никто не писал", reply_markup=get_admin_main_keyboard())
        return
    
    # Создаём клавиатуру с отправителями
    buttons = []
    user_ids = list(user_sessions.keys())
    
    # Берём последних 5 отправителей
    for user_id in user_ids[-5:]:
        user_data = user_sessions[user_id]
        name = user_data.get('first_name', 'Без имени')
        if len(name) > 10:
            name = name[:10] + "..."
        
        buttons.append([InlineKeyboardButton(
            text=f"👤 {name}",
            callback_data=f"reply_{user_id}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        "💬 Выбери, кому ответить:",
        reply_markup=keyboard
    )

@dp.message(F.text == "❓ Как это работает?")
async def handle_how_it_works(message: Message):
    await message.answer(
        "🤔 КАК ЭТО РАБОТАЕТ:\n\n"
        "1. Ты пишешь сообщение боту\n"
        "2. Бот пересылает его мне анонимно\n"
        "3. Я вижу сообщение, но не знаю кто ты\n"
        "4. Я могу ответить тебе\n"
        "5. Ответ придёт от бота",
        reply_markup=get_user_main_keyboard()
    )

@dp.message(F.text == "📨 Отправить сообщение")
async def handle_send_message_button(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Ты админчик! Тебе не нужно отправлять сообщения самому себе 😊",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    await message.answer(
        "📤 Напиши своё сообщение:\n\n"
        "Можно отправить текст, фото, видео, гс, документ или нюдсы.",
        reply_markup=get_user_main_keyboard()
    )

# =================== CALLBACK ОБРАБОТЧИКИ ===================

@dp.callback_query(F.data.startswith("reply_"))
async def handle_reply_button(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    pending_replies[callback.from_user.id] = user_id
    
    user_info = user_sessions.get(user_id, {})
    name = user_info.get('first_name', 'незнакомец')
    
    await callback.message.answer(
        f"💭 Ты отвечаешь {name} (ID: {user_id})\n\n"
        f"Напиши ответ. Он отправится анонимно.\n\n"
        f"Чтобы отменить, отправь /cancel",
        reply_markup=get_admin_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("info_"))
async def handle_info_button(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только для админа", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    user_data = user_sessions.get(user_id, {})
    
    info_text = (
        f"📋 Информация об отправителе\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{user_data.get('username', 'нет')}\n"
        f"📛 Имя: {user_data.get('first_name', 'нет')}\n"
        f"📛 Фамилия: {user_data.get('last_name', 'нет')}"
    )
    
    await callback.message.answer(info_text)
    await callback.answer()

# =================== ОБРАБОТКА СООБЩЕНИЙ ===================

@dp.message(F.text)
async def handle_text(message: Message):
    # Пропускаем если это кнопки
    if message.text in [
        "📨 Отправить сообщение", "❓ Как это работает?", 
        "📊 Статистика", "📖 Команды", "👥 Все отправители",
        "🔄 Ссылка на бота", "📨 Ответить кому-то", "❓ Помощь"
    ]:
        return
    
    # Если админ в режиме ответа
    if message.from_user.id == ADMIN_ID and pending_replies.get(message.from_user.id):
        user_id = pending_replies[message.from_user.id]
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"💌 Ответ на твоё сообщение:\n\n{message.text}"
            )
            
            await message.answer(
                f"✅ Ответ отправлен! (ID: {user_id})\n"
                f"Следующие сообщения тоже отправятся ему.\n"
                f"Чтобы прекратить, отправь /cancel",
                reply_markup=get_admin_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка отправки ответа: {e}")
            await message.answer(f"❌ Ошибка: {e}")
        
        return
    
    # Если это не админ - обрабатываем как анонимное сообщение
    if message.from_user.id != ADMIN_ID:
        user_id = message.from_user.id
        
        # Сохраняем информацию
        user_sessions[user_id] = {
            'username': message.from_user.username or "не указан",
            'first_name': message.from_user.first_name or "не указано",
            'last_name': message.from_user.last_name or "не указано",
            'type': 'text'
        }
        
        # Отправляем админу
        admin_text = (
            f"📩 Анонимное сообщение\n\n"
            f"{message.text}\n\n"
            f"Пошел нахуй!\n"
            f"🆔 Отправитель: {user_id}"
        )
        
        try:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                reply_markup=get_message_actions_keyboard(user_id)
            )
            
            await message.answer(
                "✅ Сообщение отправлено!\n\n"
                "Если я захочу ответить — ты получишь уведомление.",
                reply_markup=get_user_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Ошибка пересылки: {e}")
            await message.answer("😔 Не удалось отправить. Попробуй еще раз, но не спамь.")

@dp.message(F.photo | F.video | F.document | F.audio | F.voice | F.sticker)
async def handle_media(message: Message):
    if message.from_user.id == ADMIN_ID:
        return
    
    user_id = message.from_user.id
    
    # Сохраняем информацию
    user_sessions[user_id] = {
        'username': message.from_user.username or "не указан",
        'first_name': message.from_user.first_name or "не указано",
        'last_name': message.from_user.last_name or "не указано",
        'type': 'media'
    }
    
    caption = message.caption or "📎 Медиа-файл"
    
    try:
        media_caption = (
            f"📤 Анонимное медиа\n\n"
            f"{caption}\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🆔 Отправитель: {user_id}"
        )
        
        if message.photo:
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=message.photo[-1].file_id,
                caption=media_caption,
                reply_markup=get_message_actions_keyboard(user_id)
            )
        elif message.video:
            await bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=media_caption,
                reply_markup=get_message_actions_keyboard(user_id)
            )
        elif message.document:
            await bot.send_document(
                chat_id=ADMIN_ID,
                document=message.document.file_id,
                caption=media_caption,
                reply_markup=get_message_actions_keyboard(user_id)
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=ADMIN_ID,
                voice=message.voice.file_id,
                caption=media_caption,
                reply_markup=get_message_actions_keyboard(user_id)
            )
        elif message.sticker:
            await bot.send_sticker(
                chat_id=ADMIN_ID,
                sticker=message.sticker.file_id
            )
        
        await message.answer(
            "✅ Медиа отправлено!",
            reply_markup=get_user_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка пересылки медиа: {e}")
        await message.answer("😔 Не удалось отправить медиа.")

@dp.message(Command("cancel"))
async def cmd_cancel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if pending_replies.get(message.from_user.id):
        user_id = pending_replies.pop(message.from_user.id)
        await message.answer(f"❌ Ответ пользователю {user_id} отменён", reply_markup=get_admin_main_keyboard())
    else:
        await message.answer("🤷 Нечего отменять", reply_markup=get_admin_main_keyboard())

# =================== ЗАПУСК БОТА ===================

async def main():
    logger.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())