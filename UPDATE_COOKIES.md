# Как обновить cookies для сервера

## Проблема

Cookies на сервере не содержат критичные токены авторизации:
- ❌ `WILDAUTHNEW_V3` - НЕ НАЙДЕН
- ❌ `WBToken` - НЕ НАЙДЕН  
- ✅ `x-supplier-id` - есть, но недостаточно

## Решение: Создать новые cookies с полной авторизацией

### Шаг 1: На локальной машине (Windows)

1. **Удалите старые cookies (если есть):**
   ```powershell
   cd C:\projects\wbB\podgon_ceny
   Remove-Item wb_cookies.pkl -ErrorAction SilentlyContinue
   Remove-Item wb_cookies.* -ErrorAction SilentlyContinue
   ```

2. **Убедитесь что в .env:**
   ```env
   HEADLESS_BROWSER=false
   ```

3. **Запустите скрипт и дождитесь ПОЛНОЙ авторизации:**
   ```powershell
   py update_wb_prices_from_template.py
   ```
   
   **ВАЖНО:** Дождитесь успешного выполнения всего скрипта! Браузер должен:
   - Открыться видимо
   - Вы пройдете авторизацию через SMS
   - Скрипт должен успешно скачать шаблон
   - Только после этого будут сохранены правильные cookies

4. **Проверьте что cookies созданы и содержат важные токены:**
   ```powershell
   py check_cookies.py
   ```
   
   Должно показать:
   ```
   ✓ WILDAUTHNEW_V3     - НАЙДЕН
   ✓ WBToken            - НАЙДЕН  
   ✓ x-supplier-id      - НАЙДЕН
   ```

### Шаг 2: Скопируйте новые cookies на сервер

```powershell
cd C:\projects\wbB\podgon_ceny
"C:\Program Files\PuTTY\pscp.exe" -i "C:\b\VPS1.ppk" wb_cookies.pkl rinat@85.198.96.71:/home/rinat/podgon_ceny/
```

Если есть storage файл:
```powershell
"C:\Program Files\PuTTY\pscp.exe" -i "C:\b\VPS1.ppk" wb_cookies.pkl.storage.json rinat@85.198.96.71:/home/rinat/podgon_ceny/
```

### Шаг 3: На сервере проверьте

```bash
cd ~/podgon_ceny
python3 check_cookies.py
```

Должно показать все важные cookies.

### Шаг 4: Запустите скрипт на сервере

```bash
./run_update.sh
tail -f logs/update_prices.log
```

## Альтернатива: Использовать профиль браузера

Если cookies не работают, можно скопировать весь профиль браузера:

1. На локальной машине найдите профиль Chrome после авторизации
2. Скопируйте директорию профиля на сервер
3. В .env укажите:
   ```
   USE_BROWSER_PROFILE=true
   BROWSER_PROFILE_PATH=/home/rinat/podgon_ceny/wb_browser_profile
   ```

