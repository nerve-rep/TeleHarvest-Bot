@echo off
echo "Запуск Telegram-бота..."
call .\.venv\Scripts\activate.bat
python main.py
echo "Бот остановлен."
pause