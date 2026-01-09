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
# CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1)
# CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
# wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
# unzip -q chromedriver_linux64.zip
# mv chromedriver /usr/local/bin/
# chmod +x /usr/local/bin/chromedriver
# rm chromedriver_linux64.zip

# Установка дополнительных зависимостей для Chrome
echo "[4/6] Установка дополнительных библиотек для Chrome..."
apt install -y \
    xvfb \
    libxss1 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    fonts-liberation \
    libappindicator3-1

# Проверка установки
echo "[5/6] Проверка установки..."
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium установлен: $(chromium-browser --version | head -1)"
else
    echo "❌ Chromium не найден!"
fi

if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver установлен: $(chromedriver --version | head -1)"
else
    echo "⚠️  ChromeDriver не найден в PATH, но может быть доступен через chromium-chromedriver"
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
echo "4. Установите Python зависимости: pip install selenium openpyxl requests python-dotenv"
echo "5. Настройте .env файл (см. VPS_DEPLOYMENT.md)"
echo "6. Скопируйте cookies с локальной машины"
echo "7. Запустите тест: python3 update_wb_prices_from_template.py"
echo
echo "Для автоматического запуска настройте cron (см. VPS_DEPLOYMENT.md)"

