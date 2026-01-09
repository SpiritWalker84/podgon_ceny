# Развертывание на Ubuntu VPS - Краткая инструкция

## Быстрая установка

### 1. Подключитесь к VPS по SSH
```bash
ssh user@your-vps-ip
```

### 2. Установите зависимости
```bash
# Автоматическая установка
sudo bash install_vps.sh

# Или вручную:
sudo apt update && sudo apt install -y python3 python3-pip python3-venv chromium-browser chromium-chromedriver
```

### 3. Скопируйте проект на сервер

**На локальной машине (Windows):**
```powershell
# Создайте архив (в директории проекта)
tar -czf wb_project.tar.gz *.py VPS_DEPLOYMENT.md install_vps.sh .env.example

# Скопируйте на сервер
scp wb_project.tar.gz user@your-vps-ip:/home/user/

# Скопируйте cookies (важно!)
scp wb_cookies.pkl user@your-vps-ip:/home/user/podgon_ceny/
scp wb_cookies.pkl.storage.json user@your-vps-ip:/home/user/podgon_ceny/ 2>$null
```

**На сервере:**
```bash
cd /home/user
tar -xzf wb_project.tar.gz
cd podgon_ceny  # или ваша директория
```

### 4. Настройте виртуальное окружение (ОБЯЗАТЕЛЬНО)

```bash
# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте окружение
source venv/bin/activate

# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install selenium openpyxl requests python-dotenv

# Создайте .env файл
cp .env.example .env
nano .env

# Важно: Всегда активируйте venv перед запуском скриптов!
```

**Важные настройки в .env:**
```env
WB_API_TOKEN=ваш_токен
HEADLESS_BROWSER=true  # ОБЯЗАТЕЛЬНО для VPS
USE_BROWSER_PROFILE=true
BROWSER_PROFILE_PATH=/home/user/podgon_ceny/wb_browser_profile
TARGET_DIR=/home/user/podgon_ceny
BASE_DIR=~/wildberries/price  # Директория с CSV файлами (brand_*.csv)
```

**Примечание:** CSV файлы (`brand_BOSCH.csv`, `brand_MANN.csv`, `brand_TRIALLI.csv`) должны находиться в `~/wildberries/price` на сервере. Они не включаются в репозиторий, так как уже есть на сервере.

### 5. Тестирование

```bash
# Перейдите в директорию проекта
cd /home/user/podgon_ceny

# Активируйте виртуальное окружение (ОБЯЗАТЕЛЬНО!)
source venv/bin/activate

# Проверьте что окружение активировано (должен быть префикс (venv))
# Запустите скрипт
python3 update_wb_prices_from_template.py

# После работы можете деактивировать (опционально)
# deactivate
```

### 6. Настройка автоматического запуска

```bash
# Создайте скрипт-обертку с проверкой виртуального окружения
cat > /home/user/podgon_ceny/run_update.sh << 'EOF'
#!/bin/bash
cd /home/user/podgon_ceny || exit 1

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "ОШИБКА: Виртуальное окружение не найдено!" >> logs/update_prices.log 2>&1
    exit 1
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем активацию
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ОШИБКА: Не удалось активировать venv!" >> logs/update_prices.log 2>&1
    exit 1
fi

# Создаем директорию логов
mkdir -p logs

# Запускаем скрипт
python3 update_wb_prices_from_template.py >> logs/update_prices.log 2>&1

EXIT_CODE=$?
deactivate
exit $EXIT_CODE
EOF

chmod +x /home/user/podgon_ceny/run_update.sh
mkdir -p /home/user/podgon_ceny/logs
```

# Настройте cron (запуск каждый день в 3:00)
crontab -e
# Добавьте строку:
0 3 * * * /home/user/podgon_ceny/run_update.sh
```

## Важные моменты

### Cookies и авторизация
- На VPS нельзя авторизоваться вручную (нет GUI)
- Скопируйте свежие cookies с локальной машины
- Cookies обычно действуют несколько дней/недель

### Проверка работы
```bash
# Просмотр логов
tail -f logs/update_prices.log

# Ручной запуск
cd /home/user/podgon_ceny
source venv/bin/activate
python3 update_wb_prices_from_template.py
```

### Обновление cookies
Когда cookies истекут:
1. На локальной машине запустите скрипт с `HEADLESS_BROWSER=false`
2. Авторизуйтесь вручную
3. Скопируйте новые cookies на VPS:
   ```bash
   scp wb_cookies.pkl user@vps:/home/user/podgon_ceny/
   ```

## Решение проблем

### Chrome не запускается
```bash
# Проверьте установку
chromium-browser --version
chromedriver --version

# Если chromedriver не найден
export PATH=$PATH:/usr/lib/chromium-browser/
```

### Ошибка прав доступа
```bash
chmod 600 wb_cookies.pkl
chmod -R 700 wb_browser_profile
```

### Недостаточно памяти
Убедитесь что в .env указано:
```env
HEADLESS_BROWSER=true
```
И в коде уже есть оптимизации для маломощных серверов.

Подробная документация: см. `VPS_DEPLOYMENT.md`

