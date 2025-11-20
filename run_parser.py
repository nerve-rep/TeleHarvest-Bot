import asyncio
import sys
from main import fetch_and_save_posts

async def run_standalone():
    """
    Автономный запуск парсера для указанного канала.
    """
    channel_url = ""
    limit = 10

    # Получаем URL
    if len(sys.argv) > 1:
        channel_url = sys.argv[1]
    else:
        channel_url = input("Введите URL Telegram-канала (например, https://t.me/durov): ")

    if not channel_url:
        print("URL не указан. Завершение работы.")
        return

    # Получаем лимит
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print(f"Неверное значение для количества: '{sys.argv[2]}'. Используется значение по умолчанию: 10.")
    else:
        limit_input = input("Введите количество постов для выгрузки (нажмите Enter для 10): ")
        if limit_input.isdigit():
            limit = int(limit_input)

    print(f"Начинаю выгрузку {limit} постов из канала {channel_url}...")
    
    try:
        file_path, channel_name = await fetch_and_save_posts(channel_url, limit)
        print(f"Успешно! Посты из канала @{channel_name} сохранены в файл: {file_path}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(run_standalone())