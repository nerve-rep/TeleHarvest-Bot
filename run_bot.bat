@echo off
chcp 65001 > nul
echo "Запуск Telegram-бота..."
call .\.venv\Scripts\activate.bat
python main.py
echo "Бот остановлен."
pause