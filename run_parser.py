import asyncio
import sys
from main import fetch_and_save_posts

async def run_standalone():
    """
    Автономный запуск парсера для указанного канала.
    Принимает URL как аргумент командной строки или запрашивает у пользователя.
    """
    channel_url = ""
    # Проверяем, был ли передан аргумент
    if len(sys.argv) > 1:
        channel_url = sys.argv[1]
    else:
        # Если нет, запрашиваем у пользователя
        channel_url = input("Введите URL Telegram-канала (например, https://t.me/durov): ")

    if not channel_url:
        print("URL не указан. Завершение работы.")
        return

    print(f"Начинаю выгрузку постов из канала {channel_url}...")
    
    try:
        file_path, channel_name = await fetch_and_save_posts(channel_url)
        print(f"Успешно! Посты из канала @{channel_name} сохранены в файл: {file_path}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(run_standalone())