# Автоматическая загрузка Excel шаблона на Linux сервере

## Вариант 1: Через API (предпочтительно, но может не работать)

Скрипт автоматически попытается скачать шаблон через API, используя ваш `WB_API_TOKEN`. 
Если это не сработает, перейдет к варианту 2.

## Вариант 2: Через headless браузер на Linux

### Установка Chromium на Linux сервере:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

**CentOS/RHEL:**
```bash
sudo yum install -y chromium chromium-headless chromium-driver
```

**Или установите через snap:**
```bash
sudo snap install chromium
```

### Настройка в .env:

```env
AUTO_DOWNLOAD_EXCEL=true
HEADLESS_BROWSER=true  # Обязательно true для Linux сервера
BROWSER_PATH=/usr/bin/chromium-browser  # Или путь к вашему Chrome/Chromium
```

### Проблема с авторизацией на сервере:

На Linux сервере без GUI авторизация через браузер может быть проблематичной.
Есть несколько решений:

#### Решение A: Использовать сохраненные cookies

1. Скачайте cookies с вашего рабочего компьютера (где вы авторизованы в WB):
   - Откройте браузер с DevTools (F12)
   - Перейдите на https://seller.wildberries.ru
   - Вкладка Application → Cookies → скопируйте cookies
   
2. Или используйте расширение браузера для экспорта cookies в формате JSON

3. Сохраните cookies в файл `wb_cookies.pkl` (используя скрипт на рабочем ПК)

#### Решение B: Использовать API токен для прямых запросов

Попробуйте найти прямую ссылку на скачивание Excel шаблона и использовать ее с API токеном.

#### Решение C: Ручная загрузка (самый надежный)

Если автоматизация не работает, можно:
1. Периодически скачивать Excel шаблон вручную
2. Загружать его на сервер
3. Скрипт автоматически использует последний доступный файл

## Вариант 3: Использовать requests с cookies

Если у вас есть валидные cookies, можно скачать файл напрямую через requests:

```python
import requests

cookies = {
    'WBToken': 'ваш_токен',
    # другие cookies
}

response = requests.get(
    'https://seller.wildberries.ru/.../download-template',
    cookies=cookies
)
```

## Рекомендация

Для production сервера лучше использовать **Вариант C** (ручная загрузка):
- Более надежно
- Не требует браузера
- Не зависит от изменений в интерфейсе WB
- Можно автоматизировать через cron и scp/sftp


