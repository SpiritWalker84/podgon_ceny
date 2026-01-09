#!/bin/bash
# Скрипт для проверки статуса и поиска файлов

echo "=== Проверка статуса скрипта ==="
echo

# Проверка логов
echo "1. Последние строки из логов:"
echo "--------------------------------"
tail -50 logs/update_prices.log 2>/dev/null || echo "Логи не найдены"
echo
echo

# Поиск файлов шаблонов
echo "2. Поиск Excel файлов шаблонов:"
echo "--------------------------------"
find . -name "Шаблон*.xlsx" -type f -mtime -1 2>/dev/null | head -5
echo
find ~/wildberries -name "Шаблон*.xlsx" -type f -mtime -1 2>/dev/null | head -5
echo

# Проверка текущей директории
echo "3. Текущая директория:"
echo "--------------------------------"
pwd
echo

# Проверка .env
echo "4. Настройки TARGET_DIR из .env:"
echo "--------------------------------"
if [ -f .env ]; then
    grep TARGET_DIR .env || echo "TARGET_DIR не указан в .env"
else
    echo ".env файл не найден"
fi
echo

# Проверка файлов в текущей директории
echo "5. Excel файлы в текущей директории:"
echo "--------------------------------"
ls -lh *.xlsx 2>/dev/null | tail -5 || echo "Excel файлы не найдены"
echo

# Проверка последнего запуска
echo "6. Время последнего запуска:"
echo "--------------------------------"
if [ -f logs/update_prices.log ]; then
    stat -c "Последнее изменение лога: %y" logs/update_prices.log
else
    echo "Лог файл не найден"
fi
echo

