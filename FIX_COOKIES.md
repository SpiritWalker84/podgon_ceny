# Решение проблемы с авторизацией на сервере

## Проблема: Cookies истекли или не работают

Если вы видите ошибку:
```
[ERROR] Браузер в headless режиме - невозможно авторизоваться
```

Это означает, что cookies на сервере истекли или отсутствуют.

## Решение: Скопировать свежие cookies с локальной машины

### Шаг 1: На локальной машине (Windows)

1. **Убедитесь что скрипт работает локально:**
   ```powershell
   # В .env установите:
   HEADLESS_BROWSER=false
   
   # Запустите скрипт и авторизуйтесь:
   py update_wb_prices_from_template.py
   ```

2. **После успешной авторизации скопируйте cookies на сервер:**
   ```powershell
   # Скопируйте файлы cookies
   scp wb_cookies.pkl user@your-vps-ip:/home/rinat/podgon_ceny/
   scp wb_cookies.pkl.storage.json user@your-vps-ip:/home/rinat/podgon_ceny/ 2>$null
   ```

### Шаг 2: На сервере

1. **Проверьте что файлы скопировались:**
   ```bash
   ls -la ~/podgon_ceny/wb_cookies.*
   ```

2. **Установите правильные права:**
   ```bash
   chmod 600 ~/podgon_ceny/wb_cookies.pkl
   ```

3. **Переустановите зависимости (добавлен pandas):**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Проверьте .env файл:**
   ```bash
   cat .env | grep -E "WB_API_TOKEN|HEADLESS"
   ```
   
   Должно быть:
   ```
   WB_API_TOKEN=ваш_токен_здесь
   HEADLESS_BROWSER=true
   ```

5. **Запустите скрипт снова:**
   ```bash
   ./run_update.sh
   ```

## Альтернативный способ: Использовать профиль браузера

Если cookies не работают, можно скопировать весь профиль браузера:

### На локальной машине:
1. Найдите профиль Chrome/Edge (обычно в `%LOCALAPPDATA%\Google\Chrome\User Data\Default`)
2. Скопируйте директорию на сервер

### На сервере:
```bash
# В .env добавьте:
USE_BROWSER_PROFILE=true
BROWSER_PROFILE_PATH=/home/rinat/podgon_ceny/wb_browser_profile
```

## Проверка работоспособности

После копирования cookies:
```bash
# Проверьте логи
tail -f logs/update_prices.log

# Должны увидеть:
# [OK] Cookies загружены и применены
# [OK] Авторизация подтверждена
```

## Автоматическое обновление cookies

Cookies обычно действительны 7-30 дней. Когда истекут:
1. Повторите процедуру копирования с локальной машины
2. Или настройте периодическое обновление cookies (если доступно через API)

