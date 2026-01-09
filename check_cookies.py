#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки cookies
"""

import pickle
import json
from datetime import datetime
import time

cookies_file = "wb_cookies.pkl"

try:
    with open(cookies_file, 'rb') as f:
        cookies = pickle.load(f)
    
    print(f"Всего cookies: {len(cookies)}")
    print("\nСписок всех cookies:")
    for cookie in cookies:
        name = cookie.get('name', 'NO_NAME')
        domain = cookie.get('domain', 'NO_DOMAIN')
        expiry = cookie.get('expiry', None)
        
        if expiry:
            if isinstance(expiry, (int, float)):
                expiry_dt = datetime.fromtimestamp(expiry)
                is_expired = expiry < time.time()
                expiry_str = f"{expiry_dt.strftime('%Y-%m-%d %H:%M:%S')} ({'ИСТЕК' if is_expired else 'ДЕЙСТВИТЕЛЕН'})"
            else:
                expiry_str = str(expiry)
        else:
            expiry_str = "Без срока действия"
        
        print(f"  - {name:30} | домен: {domain:20} | срок: {expiry_str}")
    
    # Проверяем важные cookies
    important_cookies = ['WILDAUTHNEW_V3', 'WBToken', 'x-supplier-id', 'WBUID']
    print("\nПроверка важных cookies:")
    for important in important_cookies:
        found = [c for c in cookies if c.get('name') == important]
        if found:
            cookie = found[0]
            expiry = cookie.get('expiry')
            if expiry and isinstance(expiry, (int, float)):
                is_expired = expiry < time.time()
                print(f"  ✓ {important:20} - НАЙДЕН ({'ИСТЕК' if is_expired else 'ДЕЙСТВИТЕЛЕН'})")
            else:
                print(f"  ✓ {important:20} - НАЙДЕН (без срока)")
        else:
            print(f"  X {important:20} - НЕ НАЙДЕН")
    
    # Проверяем expiry для всех cookies
    expired_count = 0
    for cookie in cookies:
        expiry = cookie.get('expiry')
        if expiry and isinstance(expiry, (int, float)):
            if expiry < time.time():
                expired_count += 1
    
    print(f"\nИстекших cookies: {expired_count} из {len(cookies)}")
    
except FileNotFoundError:
    print(f"Файл {cookies_file} не найден!")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

