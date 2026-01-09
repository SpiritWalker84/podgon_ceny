# Развертывание скрипта обновления цен WB на Ubuntu VPS

## Требования

- Ubuntu 20.04+ или Debian 11+
- Python 3.8+
- Доступ по SSH к серверу

## Шаг 1: Установка зависимостей

### 1.1 Обновление системы
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Установка Python и pip
```bash
sudo apt install -y python3 python3-pip python3-venv
```

### 1.3 Установка Chrome/Chromium и ChromeDriver
```bash
# Установка Chromium
sudo apt install -y chromium-browser chromium-chromedriver

# Или установка Google Chrome (альтернатива)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Установка ChromeDriver для Chrome
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
```

### 1.4 Установка дополнительных зависимостей
```bash
sudo apt install -y \
    xvfb \
    libxss1 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0
```

## Шаг 2: Настройка проекта

### 2.1 Копирование файлов на сервер

```bash
# На локальной машине создайте архив проекта
tar -czf wb_prices.tar.gz \
    update_wb_prices_from_template.py \
    test_download_excel.py \
    update_prices.py \
    update_wb_stocks_prices.py \
    .env.example

# Скопируйте на сервер
scp wb_prices.tar.gz user@your-vps-ip:/home/user/

# На сервере распакуйте
ssh user@your-vps-ip
cd /home/user
tar -xzf wb_prices.tar.gz
cd podgon_ceny  # или ваша директория проекта
```

### 2.2 Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install selenium openpyxl requests python-dotenv
```

### 2.3 Настройка .env файла

```bash
nano .env
```

Добавьте в файл:
```env
# API токен WB (обязательно)
WB_API_TOKEN=ваш_токен_здесь

# Директория для работы
TARGET_DIR=/home/user/podgon_ceny

# Режим браузера (для VPS обязательно headless=true)
HEADLESS_BROWSER=true

# Путь к Chrome/Chromium (если установлен не в стандартном месте)
BROWSER_PATH=/usr/bin/chromium-browser
# Или для Chrome:
# BROWSER_PATH=/usr/bin/google-chrome

# Использование профиля браузера (рекомендуется для сохранения сессии)
USE_BROWSER_PROFILE=true
BROWSER_PROFILE_PATH=/home/user/podgon_ceny/wb_browser_profile

# URL WB
WB_BASE_URL=https://seller.wildberries.ru
WB_PRICES_URL=https://seller.wildberries.ru/discount-and-prices
```

## Шаг 3: Перенос cookies с локальной машины на VPS

### 3.1 На локальной машине (Windows)

```powershell
# Скопируйте файлы cookies на сервер
scp wb_cookies.pkl user@your-vps-ip:/home/user/podgon_ceny/
scp wb_cookies.pkl.storage.json user@your-vps-ip:/home/user/podgon_ceny/ 2>$null
```

Или через SFTP клиент (FileZilla, WinSCP):
- Файлы для копирования:
  - `wb_cookies.pkl`
  - `wb_cookies.pkl.storage.json` (если есть)
  - `wb_browser_profile/` (весь каталог, если используете профиль браузера)

### 3.2 На сервере проверьте права доступа

```bash
chmod 600 wb_cookies.pkl
chmod -R 700 wb_browser_profile  # если используется
```

## Шаг 4: Тестирование

### 4.1 Проверка установки Chrome/Chromium

```bash
chromium-browser --version
# или
google-chrome --version

chromedriver --version
```

### 4.2 Запуск скрипта вручную

```bash
cd /home/user/podgon_ceny
source venv/bin/activate
python3 update_wb_prices_from_template.py
```

## Шаг 5: Настройка автоматического запуска (Cron)

### 5.1 Создание скрипта-обертки

```bash
nano /home/user/podgon_ceny/run_update_prices.sh
```

Содержимое:
```bash
#!/bin/bash
cd /home/user/podgon_ceny
source venv/bin/activate
python3 update_wb_prices_from_template.py >> /home/user/podgon_ceny/logs/update_prices.log 2>&1
```

Сделайте исполняемым:
```bash
chmod +x /home/user/podgon_ceny/run_update_prices.sh
mkdir -p /home/user/podgon_ceny/logs
```

### 5.2 Настройка Cron

```bash
crontab -e
```

Добавьте строку для запуска каждый день в 3:00:
```cron
0 3 * * * /home/user/podgon_ceny/run_update_prices.sh
```

Или для запуска каждые 6 часов:
```cron
0 */6 * * * /home/user/podgon_ceny/run_update_prices.sh
```

Для запуска каждый час:
```cron
0 * * * * /home/user/podgon_ceny/run_update_prices.sh
```

### 5.3 Просмотр логов

```bash
tail -f /home/user/podgon_ceny/logs/update_prices.log
```

## Шаг 6: Решение проблем

### Проблема: Браузер не запускается в headless режиме

**Решение:**
```bash
# Проверьте, установлен ли ChromeDriver
which chromedriver

# Если нет, установите заново
sudo apt install chromium-chromedriver

# Или используйте Xvfb (виртуальный дисплей)
sudo apt install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

### Проблема: Cookies не работают / требуется авторизация

**Решение:**
1. Скопируйте свежие cookies с локальной машины
2. Убедитесь, что файл `wb_cookies.pkl` не поврежден
3. Проверьте права доступа к файлу

### Проблема: Недостаточно памяти

**Решение:**
Добавьте в скрипт дополнительные опции Chrome:
```python
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
```

### Проблема: Ошибка "ChromeDriver version mismatch"

**Решение:**
```bash
# Обновите ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

## Шаг 7: Мониторинг и уведомления

### 7.1 Настройка email уведомлений (опционально)

Создайте скрипт для отправки email:
```bash
nano /home/user/podgon_ceny/send_notification.sh
```

```bash
#!/bin/bash
# Установите mailutils: sudo apt install mailutils
echo "Обновление цен WB завершено. Проверьте логи." | mail -s "WB Prices Update" your-email@example.com
```

### 7.2 Интеграция с Telegram ботом (опционально)

Можно добавить отправку уведомлений в Telegram при ошибках.

## Важные замечания

1. **Авторизация**: На VPS нельзя авторизоваться вручную через SMS. Поэтому важно:
   - Скопировать свежие cookies с локальной машины
   - Настроить автоматическое обновление cookies при истечении

2. **Ресурсы**: Скрипт использует браузер, который может потреблять память. Убедитесь, что на VPS достаточно RAM (минимум 1GB, рекомендуется 2GB+).

3. **Безопасность**:
   - Не коммитьте `.env` файл в git
   - Ограничьте права доступа к файлам cookies
   - Используйте SSH ключи вместо паролей

4. **Обновление cookies**: Cookies могут истечь. Планируйте периодическое обновление cookies вручную или автоматизацию через API (если доступно).

## Быстрый старт (краткая версия)

```bash
# 1. Установка зависимостей
sudo apt update && sudo apt install -y python3 python3-pip chromium-browser chromium-chromedriver

# 2. Настройка проекта
python3 -m venv venv
source venv/bin/activate
pip install selenium openpyxl requests python-dotenv

# 3. Копирование файлов и cookies (с локальной машины)

# 4. Настройка .env с HEADLESS_BROWSER=true

# 5. Тест
python3 update_wb_prices_from_template.py

# 6. Настройка cron для автоматического запуска
```

