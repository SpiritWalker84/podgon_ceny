# Настройка для запуска на VPS без браузера (Linux)

## Решенные проблемы

1. ✅ **Убрано множественное скачивание** - исправлена логика проверки файлов
2. ✅ **Добавлена поддержка headless режима** для VPS/серверов

## Требования для VPS (Linux)

### 1. Установка Chrome/Chromium

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Или для CentOS/RHEL
sudo yum install -y chromium chromedriver

# Или используйте Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
```

### 2. Установка Python зависимостей

```bash
pip install selenium python-dotenv openpyxl requests
```

### 3. Настройка виртуального дисплея (для headless)

Если используется старый headless режим, может потребоваться виртуальный дисплей:

```bash
# Установка Xvfb (виртуальный дисплей)
sudo apt-get install -y xvfb

# Запуск виртуального дисплея перед скриптом
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
```

Или используйте новый headless режим Chrome (уже включен в код).

### 4. Настройка .env для VPS

```bash
# В .env файле установите:
HEADLESS_BROWSER=true
USE_BROWSER_PROFILE=true
# BROWSER_PROFILE_PATH можно не указывать - будет создан временный профиль

# Или если хотите использовать конкретный путь к профилю:
# BROWSER_PROFILE_PATH=/path/to/profile/directory
```

### 5. Первая авторизация на VPS

**Проблема:** На VPS в headless режиме нельзя авторизоваться через SMS вручную.

**Решение:** 

1. **Вариант 1 (рекомендуется):** Скачайте cookies на локальном компьютере:
   ```bash
   # На локальном компьютере:
   # 1. Установите HEADLESS_BROWSER=false
   # 2. Запустите скрипт и авторизуйтесь
   # 3. Скопируйте файлы cookies на VPS:
   scp wb_cookies.pkl user@vps:/path/to/project/
   scp wb_cookies.json user@vps:/path/to/project/
   scp wb_cookies.storage.json user@vps:/path/to/project/
   ```

2. **Вариант 2:** Используйте X11 forwarding (для одноразовой авторизации):
   ```bash
   # На VPS установите:
   sudo apt-get install -y xvfb x11vnc
   
   # Временно отключите headless:
   HEADLESS_BROWSER=false
   
   # Запустите скрипт с X11 forwarding
   ssh -X user@vps
   python test_download_excel.py
   ```

3. **Вариант 3:** Используйте профиль браузера с уже авторизованной сессией:
   ```bash
   # На локальном компьютере:
   # 1. Экспортируйте профиль Chrome с авторизованной сессией
   # 2. Загрузите на VPS
   # 3. Укажите путь в .env:
   BROWSER_PROFILE_PATH=/path/to/chrome/profile
   ```

## Настройка скрипта для автоматического запуска

### systemd service (рекомендуется)

Создайте файл `/etc/systemd/system/wb-download.service`:

```ini
[Unit]
Description=Wildberries Excel Template Downloader
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/project
Environment="DISPLAY=:99"
ExecStart=/usr/bin/python3 /path/to/project/test_download_excel.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Cron для периодического запуска

```bash
# Редактируйте crontab
crontab -e

# Запуск каждый день в 9:00
0 9 * * * cd /path/to/project && /usr/bin/python3 test_download_excel.py >> /var/log/wb-download.log 2>&1
```

## Проверка работы

```bash
# Тест запуска
python3 test_download_excel.py

# Проверка что Chrome работает в headless
google-chrome --headless --disable-gpu --dump-dom https://www.google.com
```

## Решение проблем

### Chrome не запускается

```bash
# Проверьте что Chrome установлен
which google-chrome
which chromedriver

# Если chromedriver не найден, добавьте в PATH:
export PATH=$PATH:/usr/lib/chromium-browser/
```

### Ошибка "no display"

```bash
# Установите DISPLAY для виртуального дисплея
export DISPLAY=:99
# Или используйте headless режим (уже включен в код)
```

### Cookies не работают

```bash
# Убедитесь что файлы cookies скопированы и имеют правильные права:
chmod 644 wb_cookies.*
```

### Файл скачивается несколько раз

✅ **Исправлено!** Теперь скрипт проверяет только новые файлы и ждет завершения скачивания.

## Оптимизация для VPS

В коде уже добавлены оптимизации:
- ✅ `--no-sandbox` для работы без root
- ✅ `--disable-dev-shm-usage` для серверов с ограниченной памятью
- ✅ Отключены ненужные функции Chrome
- ✅ Новый headless режим (`--headless=new`)

## Примечания

- На VPS **обязательно** установите `HEADLESS_BROWSER=true`
- Cookies обычно действительны несколько дней/недель
- Профиль браузера сохраняется в `wb_browser_profile/` (можно удалить для новой сессии)
- Для автоматического обновления cookies можно настроить периодический перезапуск скрипта

