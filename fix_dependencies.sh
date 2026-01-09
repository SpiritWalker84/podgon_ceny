#!/bin/bash
# Скрипт для установки зависимостей Chrome на Ubuntu (поддержка всех версий)

set -e

echo "Установка зависимостей для Chrome/Chromium..."

# Определяем версию Ubuntu
if command -v lsb_release &> /dev/null; then
    UBUNTU_VERSION=$(lsb_release -rs)
    UBUNTU_MAJOR=$(echo $UBUNTU_VERSION | cut -d. -f1)
    echo "Обнаружена Ubuntu $UBUNTU_VERSION"
else
    echo "Не удалось определить версию Ubuntu, используем универсальный метод"
    UBUNTU_MAJOR=22
fi

# Базовые пакеты (работают на всех версиях)
BASE_PACKAGES=(
    "xvfb"
    "libxss1"
    "libxrandr2"
    "libpangocairo-1.0-0"
    "libcairo-gobject2"
    "libgdk-pixbuf2.0-0"
    "fonts-liberation"
    "libappindicator3-1"
)

echo "Установка базовых пакетов..."
sudo apt install -y "${BASE_PACKAGES[@]}"

# Пакеты с разными именами в зависимости от версии Ubuntu
if [ "$UBUNTU_MAJOR" -ge 24 ]; then
    echo "Установка пакетов для Ubuntu 24.04+..."
    sudo apt install -y \
        libatk1.0-0t64 \
        libgtk-3-0t64 \
        libasound2t64 2>/dev/null || {
        echo "Пробуем альтернативные имена..."
        sudo apt install -y libatk1.0-0 libgtk-3-0 libasound2 2>/dev/null || true
    }
else
    echo "Установка пакетов для Ubuntu < 24.04..."
    sudo apt install -y \
        libatk1.0-0 \
        libgtk-3-0 \
        libasound2 \
        libgconf-2-4 2>/dev/null || {
        echo "Некоторые пакеты не установились (не критично)"
        # libgconf-2-4 может быть не нужен в некоторых случаях
    }
fi

echo "✅ Зависимости установлены!"

