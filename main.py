import logging
import json
import datetime
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, API_ID, API_HASH
from telethon import TelegramClient

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Helper для конвертации данных, несериализуемых в JSON по умолчанию
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode('utf-8', 'ignore')
    raise TypeError ("Type %s not serializable" % type(obj))


async def fetch_and_save_posts(channel_url: str, limit: int = 10) -> str:
    """
    Подключается к Telethon с русским языковым кодом, выгружает посты и сохраняет их в JSON.
    Возвращает путь к файлу и имя канала.
    """
    # Создаем клиент с указанием языка для получения локализованного контента
    client = TelegramClient('user_session', int(API_ID), API_HASH, lang_code='ru')
    file_path = None
    try:
        await client.start()

        entity = await client.get_entity(channel_url)
        messages = await client.get_messages(entity, limit=limit)
        
        if not messages:
            raise ValueError("В канале нет постов или не удалось их получить.")

        posts_data = []
        for msg in reversed(messages):
            if msg:
                # Возвращаемся к сокращенному формату JSON
                post_text = msg.text if msg.text is not None else ""
                posts_data.append({
                    'id': msg.id,
                    'text': post_text,
                    'date': msg.date,
                    'views': msg.views,
                    'sender_id': msg.sender_id,
                })
        
        # Создаем папку downloads, если она не существует
        os.makedirs('downloads', exist_ok=True)
        
        file_path = f'downloads/posts_{entity.username}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=4, default=json_serial)
        
        return file_path, entity.username

    finally:
        if client.is_connected():
            await client.disconnect()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение."""
    await update.message.reply_text("Отправь мне ссылку на канал и, через пробел, количество постов (например, https://t.me/durov 50).")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справочное сообщение."""
    await update.message.reply_text("Отправь ссылку на канал и количество постов (по умолчанию 10).")

async def download_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для бота: вызывает основную логику и отправляет результат."""
    match = re.match(r'(https://t.me/\w+)\s*(\d*)', update.message.text)
    if not match:
        await update.message.reply_text("Неверный формат. Пожалуйста, отправь ссылку в формате https://t.me/channel_name [количество].")
        return

    channel_url = match.group(1)
    limit = int(match.group(2)) if match.group(2) else 10
    
    await update.message.reply_text(f"Начинаю выгрузку {limit} постов... Это может занять некоторое время.")
    
    file_path = None
    try:
        file_path, channel_name = await fetch_and_save_posts(channel_url, limit)
        
        with open(file_path, 'rb') as document:
            await update.message.reply_document(document=document, filename=file_path, caption=f"Посты из канала @{channel_name}")

    except Exception as e:
        logger.error(f"Ошибка при выгрузке постов: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex(r'https://t.me/\w+(\s*\d*)?') & ~filters.COMMAND, download_posts))

    application.run_polling()


if __name__ == "__main__":
    main()