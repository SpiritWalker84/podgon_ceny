#!/bin/bash
# Скрипт автоматической установки зависимостей для Ubuntu VPS
# Использование: bash install_vps.sh

set -e  # Прекратить выполнение при ошибке

echo "=========================================="
echo "Установка зависимостей для WB Prices Update"
echo "=========================================="
echo

# Проверка что скрипт запущен от имени root или с sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Запустите скрипт с sudo: sudo bash install_vps.sh"
    exit 1
fi

# Обновление системы
echo "[1/6] Обновление системы..."
apt update
apt upgrade -y

# Установка Python и pip
echo "[2/6] Установка Python и pip..."
apt install -y python3 python3-pip python3-venv

# Установка Chromium и ChromeDriver
echo "[3/6] Установка Chromium и ChromeDriver..."
apt install -y chromium-browser chromium-chromedriver

# Альтернатива: установка Google Chrome (раскомментируйте если нужно)
# echo "[3/6] Установка Google Chrome..."
# wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
# echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
# apt update
# apt install -y google-chrome-stable
#
# # Установка ChromeDriver для Chrome через новый Chrome for Testing API
# CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1 | cut -d. -f1)
# if [ -z "$CHROME_VERSION" ]; then
#     echo "  [WARN] Не удалось определить версию Chrome, используем последнюю"
#     CHROME_VERSION="131"  # Примерная версия
# fi
# 
# # Получаем версию ChromeDriver через Chrome for Testing API
# CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}")
# if [ -z "$CHROMEDRIVER_VERSION" ] || [[ "$CHROMEDRIVER_VERSION" == *"<"* ]]; then
#     # Если не получилось, пробуем получить последнюю стабильную версию
#     CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | grep -oP '"version": "\K[^"]+' | head -1)
# fi
# 
# if [ ! -z "$CHROMEDRIVER_VERSION" ]; then
#     echo "  [INFO] Скачиваю ChromeDriver версии $CHROMEDRIVER_VERSION..."
#     wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O chromedriver_linux64.zip
#     if [ $? -eq 0 ] && [ -f chromedriver_linux64.zip ]; then
#         unzip -q chromedriver_linux64.zip
#         mv chromedriver-linux64/chromedriver /usr/local/bin/
#         chmod +x /usr/local/bin/chromedriver
#         rm -rf chromedriver-linux64 chromedriver_linux64.zip
#         echo "  [OK] ChromeDriver установлен"
#     else
#         echo "  [WARN] Не удалось скачать ChromeDriver, используйте системный chromedriver"
#     fi
# else
#     echo "  [WARN] Не удалось определить версию ChromeDriver, используйте системный chromedriver"
# fi

# Установка дополнительных зависимостей для Chrome
echo "[4/6] Установка дополнительных библиотек для Chrome..."

# Определяем версию Ubuntu для совместимости
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "22.04")
UBUNTU_MAJOR=$(echo $UBUNTU_VERSION | cut -d. -f1)

# Базовые пакеты (общие для всех версий)
BASE_PACKAGES="xvfb libxss1 libxrandr2 libpangocairo-1.0-0 libcairo-gobject2 libgdk-pixbuf2.0-0 fonts-liberation libappindicator3-1"

# Пакеты для Ubuntu 24.04+ (с суффиксом t64)
if [ "$UBUNTU_MAJOR" -ge 24 ]; then
    echo "  [INFO] Обнаружена Ubuntu 24.04+, используем новые имена пакетов..."
    PACKAGES="$BASE_PACKAGES libatk1.0-0t64 libgtk-3-0t64 libasound2t64"
    # libgconf-2-4 не нужен в новых версиях или заменен
    PACKAGES="$PACKAGES libgconf-2-4t64 2>/dev/null" || true
else
    echo "  [INFO] Ubuntu < 24.04, используем старые имена пакетов..."
    PACKAGES="$BASE_PACKAGES libatk1.0-0 libgtk-3-0 libasound2 libgconf-2-4"
fi

# Устанавливаем пакеты (игнорируем ошибки для опциональных)
apt install -y $PACKAGES || {
    echo "  [WARN] Некоторые пакеты не установились, пробуем без опциональных..."
    # Пробуем без libgconf (он может быть не нужен)
    apt install -y $BASE_PACKAGES libatk1.0-0t64 libgtk-3-0t64 libasound2t64 2>/dev/null || \
    apt install -y $BASE_PACKAGES libatk1.0-0 libgtk-3-0 libasound2 2>/dev/null || true
}

# Проверка установки
echo "[5/6] Проверка установки..."
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium установлен: $(chromium-browser --version | head -1)"
else
    echo "❌ Chromium не найден!"
fi

# Проверяем ChromeDriver в нескольких местах
CHROMEDRIVER_PATH=""
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_PATH=$(which chromedriver)
    echo "✅ ChromeDriver установлен: $CHROMEDRIVER_PATH"
    chromedriver --version 2>/dev/null | head -1 || echo "   (версия недоступна через --version)"
elif [ -f "/usr/lib/chromium-browser/chromedriver" ]; then
    CHROMEDRIVER_PATH="/usr/lib/chromium-browser/chromedriver"
    echo "✅ ChromeDriver найден: $CHROMEDRIVER_PATH"
    # Добавляем в PATH если нужно
    if ! grep -q "/usr/lib/chromium-browser" /etc/environment 2>/dev/null; then
        echo "   💡 Совет: добавьте в PATH: export PATH=\$PATH:/usr/lib/chromium-browser"
    fi
elif [ -f "/usr/bin/chromedriver" ]; then
    CHROMEDRIVER_PATH="/usr/bin/chromedriver"
    echo "✅ ChromeDriver найден: $CHROMEDRIVER_PATH"
else
    echo "⚠️  ChromeDriver не найден в стандартных местах"
    echo "   Попробуйте: sudo apt install chromium-chromedriver"
fi

if command -v python3 &> /dev/null; then
    echo "✅ Python установлен: $(python3 --version)"
else
    echo "❌ Python не найден!"
fi

# Создание директории для логов (опционально)
echo "[6/6] Создание структуры директорий..."
PROJECT_DIR=${1:-"/home/$(logname)/podgon_ceny"}
mkdir -p "$PROJECT_DIR/logs"
chown -R $(logname):$(logname) "$PROJECT_DIR" 2>/dev/null || true

echo
echo "=========================================="
echo "✅ Установка завершена!"
echo "=========================================="
echo
echo "Следующие шаги:"
echo "1. Перейдите в директорию проекта: cd $PROJECT_DIR"
echo "2. Создайте виртуальное окружение: python3 -m venv venv"
echo "3. Активируйте окружение: source venv/bin/activate"
echo "4. Установите Python зависимости: pip install -r requirements.txt"
echo "   (или вручную: pip install selenium openpyxl requests python-dotenv)"
echo "5. Настройте .env файл (см. VPS_DEPLOYMENT.md)"
echo "6. Скопируйте cookies с локальной машины"
echo "7. Запустите тест: source venv/bin/activate && python3 update_wb_prices_from_template.py"
echo
echo "ВАЖНО: Всегда активируйте venv перед запуском скриптов!"
echo "Для автоматического запуска используйте run_update.sh скрипт (см. VPS_DEPLOYMENT.md)"

