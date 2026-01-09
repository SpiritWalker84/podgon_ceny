#!/bin/bash
# Скрипт запуска обновления цен с использованием виртуального окружения
# Использование: bash run_update.sh

set -e  # Прекратить выполнение при ошибке

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "ОШИБКА: Виртуальное окружение не найдено!"
    echo "Создайте его командой:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем что активация прошла успешно
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ОШИБКА: Не удалось активировать виртуальное окружение!"
    exit 1
fi

# Создаем директорию для логов если её нет
mkdir -p logs

# Запускаем скрипт
echo "Запуск обновления цен WB..."
echo "Виртуальное окружение: $VIRTUAL_ENV"
python3 update_wb_prices_from_template.py >> logs/update_prices.log 2>&1

# Сохраняем код выхода
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Скрипт выполнен успешно"
else
    echo "❌ Скрипт завершился с ошибкой (код: $EXIT_CODE)"
    echo "Проверьте логи: tail -f logs/update_prices.log"
fi

# Деактивируем окружение
deactivate

exit $EXIT_CODE

