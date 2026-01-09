# Быстрое исправление: установка ChromeDriver на сервере

Если вы получили ошибку 404 при установке ChromeDriver, используйте этот способ:

## Решение 1: Использовать системный chromedriver (рекомендуется)

```bash
# Установите через apt (это самый простой способ)
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver

# Проверьте установку
chromedriver --version

# Если chromedriver не найден в PATH, используйте полный путь:
/usr/lib/chromium-browser/chromedriver --version

# Или добавьте в PATH (для текущей сессии):
export PATH=$PATH:/usr/lib/chromium-browser

# Или добавьте в ~/.bashrc (для постоянного использования):
echo 'export PATH=$PATH:/usr/lib/chromium-browser' >> ~/.bashrc
source ~/.bashrc
```

## Решение 2: Указать путь к chromedriver в коде

Если chromedriver установлен, но не в PATH, можно указать путь в коде Selenium:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service('/usr/lib/chromium-browser/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
```

Но в нашем коде это не нужно - Selenium автоматически найдет chromedriver если он установлен.

## Решение 3: Скачать ChromeDriver вручную (если apt не работает)

```bash
# Получаем последнюю стабильную версию через новый API
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | grep -oP '"version": "\K[^"]+' | head -1)

echo "Скачиваю ChromeDriver версии: $CHROMEDRIVER_VERSION"

# Скачиваем и устанавливаем
wget "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O chromedriver_linux64.zip

unzip chromedriver_linux64.zip

sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Очистка
rm -rf chromedriver-linux64 chromedriver_linux64.zip

# Проверка
chromedriver --version
```

## Проверка после установки

```bash
# Проверьте что все работает
which chromedriver
chromedriver --version

# Запустите тест скрипта
cd ~/wildberries/price
python3 update_wb_prices_from_template.py
```

## Если ничего не помогает

Используйте альтернативный браузер или запустите на Windows с `HEADLESS_BROWSER=false`.

