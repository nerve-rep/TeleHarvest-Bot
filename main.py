import logging
import json
import datetime
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, API_ID, API_HASH
from telethon import TelegramClient

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Helper для конвертации datetime в строку
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Отправь мне ссылку на открытый Telegram-канал (например, https://t.me/durov), и я выгружу последние 10 постов в JSON-файл.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение, когда пользователь вводит команду /help."""
    await update.message.reply_text("Отправь мне ссылку на канал, чтобы я начал работать.")

async def fetch_and_save_posts(channel_url: str) -> str:
    """
    Подключается к Telethon, выгружает посты из канала и сохраняет их в JSON-файл.
    Возвращает путь к созданному файлу.
    """
    client = TelegramClient('user_session', int(API_ID), API_HASH)
    file_path = None
    try:
        await client.start()

        entity = await client.get_entity(channel_url)
        messages = await client.get_messages(entity, limit=10)
        
        if not messages:
            raise ValueError("В канале нет постов или не удалось их получить.")

        posts_data = []
        for msg in reversed(messages):
            if msg:
                post_text = msg.text if msg.text is not None else ""
                posts_data.append({
                    'id': msg.id,
                    'text': post_text,
                    'date': msg.date,
                    'views': msg.views,
                    'sender_id': msg.sender_id,
                })
        
        file_path = f'posts_{entity.username}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=4, default=json_serial)
        
        return file_path, entity.username

    finally:
        if client.is_connected():
            await client.disconnect()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Отправь мне ссылку на открытый Telegram-канал, и я выгружу последние 10 постов в JSON-файл.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справочное сообщение."""
    await update.message.reply_text("Отправь мне ссылку на канал, чтобы я начал работать.")

async def download_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для бота: вызывает основную логику и отправляет результат."""
    channel_url = update.message.text
    await update.message.reply_text("Начинаю выгрузку постов... Это может занять некоторое время.")
    
    file_path = None
    try:
        file_path, channel_name = await fetch_and_save_posts(channel_url)
        
        with open(file_path, 'rb') as document:
            await update.message.reply_document(document=document, filename=file_path, caption=f"Посты из канала @{channel_name}")

    except Exception as e:
        logger.error(f"Ошибка при выгрузке постов: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")
    finally:
        # Удаляем временный файл после отправки
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex(r'https://t.me/\w+') & ~filters.COMMAND, download_posts))

    application.run_polling()


if __name__ == "__main__":
    main()