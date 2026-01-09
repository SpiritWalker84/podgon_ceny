#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест запуска браузера
"""

import sys
print("[INFO] Тест запуска браузера...")
print()

try:
    from selenium import webdriver
    print("[OK] Selenium импортирован")
except Exception as e:
    print(f"[ERROR] Ошибка импорта Selenium: {e}")
    sys.exit(1)

try:
    from selenium.webdriver.chrome.options import Options
    print("[OK] Chrome Options импортирован")
except Exception as e:
    print(f"[ERROR] Chrome Options не найден: {e}")

try:
    from selenium.webdriver.edge.options import Options as EdgeOptions
    print("[OK] Edge Options импортирован")
except Exception as e:
    print(f"[ERROR] Edge Options не найден: {e}")

print()
print("[INFO] Пробую запустить Edge (Windows)...")
print("[INFO] Это может занять время, пожалуйста подождите...")

try:
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")  # Без интерфейса для теста
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    
    print("[DEBUG] Создаю WebDriver...")
    driver = webdriver.Edge(options=edge_options)
    print("[SUCCESS] Браузер запущен!")
    
    print("[INFO] Открываю страницу...")
    driver.get("https://www.google.com")
    print(f"[OK] Страница открыта: {driver.title}")
    
    driver.quit()
    print("[OK] Браузер закрыт")
    print()
    print("[SUCCESS] Тест пройден успешно!")
    
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


