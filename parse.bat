@echo off
chcp 65001 > nul
echo "Запуск автономного парсера..."
call .\.venv\Scripts\activate.bat
python run_parser.py %*
echo "Парсинг завершен."
pause