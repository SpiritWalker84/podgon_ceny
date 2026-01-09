#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки автоматической загрузки Excel шаблона
"""

import os
import sys
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
load_dotenv('.env')

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

def download_excel_only() -> str:
    """
    Автономная функция для скачивания Excel шаблона.
    Использует сохраненные cookies и работает автоматически без ожидания.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.common.action_chains import ActionChains
    except ImportError:
        print("[ERROR] Selenium не установлен. Установите: py -m pip install selenium")
        return None
    
    # Настройки из .env
    wb_base_url = os.getenv('WB_BASE_URL', 'https://seller.wildberries.ru')
    wb_prices_url = os.getenv('WB_PRICES_URL', 'https://seller.wildberries.ru/discount-and-prices')
    cookies_file = Path.cwd() / "wb_cookies.pkl"
    download_dir = str(Path.cwd())
    headless = os.getenv('HEADLESS_BROWSER', 'false').lower() == 'true'
    
    os.makedirs(download_dir, exist_ok=True)
    driver = None
    
    try:
        # Создаем браузер
        print("[INFO] Запускаю браузер...")
        
        # Проверяем, можно ли использовать профиль браузера (для сохранения сессии)
        use_browser_profile = os.getenv('USE_BROWSER_PROFILE', 'false').lower() == 'true'
        browser_profile_path = os.getenv('BROWSER_PROFILE_PATH', None)
        
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")  # Используем новый headless режим
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")  # Обязательно для VPS/серверов
            chrome_options.add_argument("--disable-dev-shm-usage")  # Для серверов с ограниченной памятью
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-breakpad")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-web-resources")
            chrome_options.add_argument("--metrics-recording-only")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--safebrowsing-disable-auto-update")
            chrome_options.add_argument("--enable-automation")
            chrome_options.add_argument("--password-store=basic")
            chrome_options.add_argument("--use-mock-keychain")  # Для macOS в headless
            
            # Добавляем User-Agent чтобы не выглядеть как бот
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Используем профиль браузера если указан (для сохранения сессии)
            if use_browser_profile and browser_profile_path:
                if Path(browser_profile_path).exists():
                    chrome_options.add_argument(f"--user-data-dir={browser_profile_path}")
                    print(f"[INFO] Использую профиль браузера: {browser_profile_path}")
            elif use_browser_profile:
                # Используем временный профиль в текущей директории
                profile_dir = Path.cwd() / "wb_browser_profile"
                profile_dir.mkdir(exist_ok=True)
                chrome_options.add_argument(f"--user-data-dir={profile_dir}")
                print(f"[INFO] Использую временный профиль: {profile_dir}")
            
            # Отключаем детекцию автоматизации
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Убираем webdriver флаг через JavaScript
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            print("[OK] Браузер запущен")
        except Exception as chrome_error:
            print(f"[WARN] Chrome не запустился: {chrome_error}")
            try:
                edge_options = EdgeOptions()
                if headless:
                    edge_options.add_argument("--headless")
                edge_options.add_argument("--disable-gpu")
                edge_options.add_argument("--no-sandbox")
                
                prefs = {
                    "download.default_directory": download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                edge_options.add_experimental_option("prefs", prefs)
                
                driver = webdriver.Edge(options=edge_options)
                print("[OK] Edge браузер запущен")
            except Exception as edge_error:
                print(f"[ERROR] Не удалось запустить браузер: {edge_error}")
                return None
        
        # Загружаем cookies ПЕРЕД переходом на страницу
        # Всегда сначала открываем базовую страницу
        driver.get(wb_base_url)
        time.sleep(2)
        
        if cookies_file.exists():
            try:
                import pickle
                import json
                print("[INFO] Загружаю сохраненные cookies...")
                
                with open(cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                print(f"[DEBUG] Загружено {len(cookies)} cookies из файла")
                
                # Добавляем cookies
                added_count = 0
                failed_count = 0
                for cookie in cookies:
                    try:
                        # Проверяем что cookie не истек
                        if 'expiry' in cookie and cookie['expiry']:
                            from datetime import datetime
                            expiry_time = cookie['expiry']
                            if isinstance(expiry_time, (int, float)):
                                if expiry_time < time.time():
                                    failed_count += 1
                                    continue  # Пропускаем истекший cookie
                        
                        # Создаем словарь только с нужными полями
                        cookie_dict = {
                            'name': cookie.get('name'),
                            'value': cookie.get('value'),
                            'domain': cookie.get('domain', '.wildberries.ru'),
                            'path': cookie.get('path', '/'),
                        }
                        
                        # Добавляем опциональные поля
                        if 'expiry' in cookie:
                            cookie_dict['expiry'] = cookie['expiry']
                        if 'secure' in cookie:
                            cookie_dict['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            cookie_dict['httpOnly'] = cookie['httpOnly']
                        
                        # Исправляем домен
                        domain = cookie_dict['domain']
                        if domain:
                            if 'wildberries.ru' not in domain:
                                cookie_dict['domain'] = '.wildberries.ru'
                            elif not domain.startswith('.'):
                                # Убираем лишнее и добавляем точку в начале
                                domain_clean = domain.replace('https://', '').replace('http://', '').split('/')[0]
                                cookie_dict['domain'] = '.' + domain_clean
                        
                        driver.add_cookie(cookie_dict)
                        added_count += 1
                    except Exception as e:
                        failed_count += 1
                        # Игнорируем ошибки отдельных cookies
                        pass
                
                print(f"[DEBUG] Добавлено {added_count} cookies, пропущено {failed_count}")
                
                # Пробуем загрузить localStorage/sessionStorage если есть
                storage_file = cookies_file.with_suffix('.storage.json')
                if storage_file.exists():
                    try:
                        with open(storage_file, 'r', encoding='utf-8') as f:
                            storage_data = json.load(f)
                        
                        # Применяем localStorage
                        if 'localStorage' in storage_data:
                            driver.execute_script("""
                                const data = arguments[0];
                                for (const [key, value] of Object.entries(data)) {
                                    localStorage.setItem(key, value);
                                }
                            """, storage_data['localStorage'])
                            print(f"[DEBUG] Загружено {len(storage_data['localStorage'])} элементов localStorage")
                        
                        # Применяем sessionStorage
                        if 'sessionStorage' in storage_data:
                            driver.execute_script("""
                                const data = arguments[0];
                                for (const [key, value] of Object.entries(data)) {
                                    sessionStorage.setItem(key, value);
                                }
                            """, storage_data['sessionStorage'])
                            print(f"[DEBUG] Загружено {len(storage_data['sessionStorage'])} элементов sessionStorage")
                    except Exception as e:
                        print(f"[DEBUG] Не удалось загрузить хранилище: {e}")
                
                # Обновляем страницу чтобы применить cookies
                driver.refresh()
                time.sleep(4)  # Увеличил время ожидания
                
                # Проверяем что cookies применились
                current_cookies = driver.get_cookies()
                print(f"[DEBUG] Текущие cookies в браузере: {len(current_cookies)}")
                print("[OK] Cookies загружены и применены")
            except Exception as e:
                print(f"[WARN] Не удалось загрузить cookies: {e}")
                import traceback
                traceback.print_exc()
        
        # Улучшенная проверка авторизации
        def check_authorization(driver_instance) -> bool:
            """Проверяет авторизацию несколькими способами"""
            try:
                current_url = driver_instance.current_url.lower()
                
                # Способ 1: Проверка URL
                if "login" in current_url or "auth" in current_url or "signin" in current_url:
                    return False
                
                # Способ 2: Проверка важных cookies (токены авторизации)
                cookies = driver_instance.get_cookies()
                auth_cookies = ['WILDAUTHNEW_V3', 'WBToken', 'x-supplier-id', 'WBUID']
                has_auth_cookie = any(cookie.get('name') in auth_cookies for cookie in cookies)
                
                if has_auth_cookie:
                    print("[DEBUG] Найдены cookies авторизации")
                    return True
                
                # Способ 3: Проверка localStorage/sessionStorage через JavaScript
                try:
                    local_storage_auth = driver_instance.execute_script("""
                        return window.localStorage.getItem('auth') || 
                               window.localStorage.getItem('token') ||
                               window.localStorage.getItem('WBToken') ||
                               window.sessionStorage.getItem('auth') ||
                               window.sessionStorage.getItem('token');
                    """)
                    if local_storage_auth:
                        print("[DEBUG] Найдены данные авторизации в хранилище")
                        return True
                except:
                    pass
                
                # Способ 4: Проверка элементов кабинета продавца
                try:
                    seller_indicators = [
                        "//*[contains(text(), 'Товары')]",
                        "//*[contains(text(), 'Аналитика')]",
                        "//*[contains(text(), 'Продавцу')]",
                        "//*[contains(@class, 'seller')]",
                        "//*[contains(@href, '/seller')]"
                    ]
                    for indicator in seller_indicators:
                        elements = driver_instance.find_elements(By.XPATH, indicator)
                        if elements and any(elem.is_displayed() for elem in elements):
                            print("[DEBUG] Найдены элементы кабинета продавца")
                            return True
                except:
                    pass
                
                # Способ 5: Проверка по URL (должен быть seller.wildberries.ru)
                if "seller.wildberries.ru" in current_url:
                    # Дополнительная проверка - нет редиректа на логин
                    time.sleep(1)
                    final_url = driver_instance.current_url.lower()
                    if "login" not in final_url and "auth" not in final_url:
                        print("[DEBUG] URL указывает на кабинет продавца")
                        return True
                
                return False
            except Exception as e:
                print(f"[DEBUG] Ошибка проверки авторизации: {e}")
                return False
        
        # Проверяем авторизацию
        is_authorized = check_authorization(driver)
        current_url = driver.current_url.lower()
        
        # Если не авторизованы - даем возможность авторизоваться вручную (WB использует SMS)
        if not is_authorized and ("login" in current_url or "auth" in current_url or "signin" in current_url):
            print("[WARN] Обнаружена страница авторизации")
            print("[INFO] WB использует SMS для авторизации - автоматическая авторизация невозможна")
            
            if headless:
                print("[ERROR] Браузер в headless режиме - невозможно авторизоваться через SMS")
                print("[INFO] Установите HEADLESS_BROWSER=false в .env для ручной авторизации")
                if driver:
                    driver.quit()
                return None
            
            # Браузер открыт в видимом режиме - даем время на ручную авторизацию
            print("[INFO] Браузер открыт - авторизуйтесь вручную через SMS")
            print("[INFO] Ожидаю максимум 60 секунд для авторизации...")
            
            max_wait_auth = 60
            waited_auth = 0
            while waited_auth < max_wait_auth:
                time.sleep(2)
                waited_auth += 2
                current_url_check = driver.current_url.lower()
                
                # Проверяем авторизацию через улучшенную функцию
                if check_authorization(driver):
                    print("[OK] Авторизация обнаружена!")
                    is_authorized = True
                    
                    # Сохраняем cookies после успешной авторизации
                    try:
                        import pickle
                        import json
                        # Ждем немного чтобы все cookies установились
                        time.sleep(2)
                        
                        # Переходим на базовый URL чтобы получить все cookies
                        driver.get(wb_base_url)
                        time.sleep(3)  # Даем время на установку всех cookies
                        
                        # Получаем все cookies
                        all_cookies = driver.get_cookies()
                        print(f"[DEBUG] Получено {len(all_cookies)} cookies с сайта")
                        
                        # Проверяем наличие важных cookies авторизации
                        important_cookies = ['WILDAUTHNEW_V3', 'WBToken', 'x-supplier-id', 'WBUID']
                        found_important = [c.get('name') for c in all_cookies if c.get('name') in important_cookies]
                        if found_important:
                            print(f"[DEBUG] Найдены важные cookies авторизации: {found_important}")
                        else:
                            print("[WARN] Не найдены важные cookies авторизации, но продолжаю сохранение")
                        
                        # Очищаем и нормализуем cookies перед сохранением
                        cleaned_cookies = []
                        for cookie in all_cookies:
                            # Сохраняем только нужные поля
                            clean_cookie = {
                                'name': cookie.get('name'),
                                'value': cookie.get('value'),
                                'domain': cookie.get('domain', '.wildberries.ru'),
                                'path': cookie.get('path', '/'),
                            }
                            
                            # Добавляем опциональные поля если они есть
                            if 'expiry' in cookie:
                                clean_cookie['expiry'] = cookie['expiry']
                            if 'secure' in cookie:
                                clean_cookie['secure'] = cookie['secure']
                            if 'httpOnly' in cookie:
                                clean_cookie['httpOnly'] = cookie['httpOnly']
                            
                            # Исправляем домен если нужно
                            if 'domain' in clean_cookie:
                                domain = clean_cookie['domain']
                                if domain and 'wildberries.ru' in domain:
                                    if not domain.startswith('.'):
                                        clean_cookie['domain'] = '.' + domain.split('://')[-1].split('/')[0]
                                else:
                                    clean_cookie['domain'] = '.wildberries.ru'
                            
                            cleaned_cookies.append(clean_cookie)
                        
                        # Сохраняем cookies
                        with open(cookies_file, 'wb') as f:
                            pickle.dump(cleaned_cookies, f)
                        
                        # Также сохраняем JSON версию для отладки
                        json_file = cookies_file.with_suffix('.json')
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(cleaned_cookies, f, indent=2, ensure_ascii=False)
                        
                        # Сохраняем localStorage/sessionStorage если возможно
                        try:
                            storage_data = driver.execute_script("""
                                return {
                                    localStorage: Object.fromEntries(
                                        Object.keys(localStorage).map(key => [key, localStorage.getItem(key)])
                                    ),
                                    sessionStorage: Object.fromEntries(
                                        Object.keys(sessionStorage).map(key => [key, sessionStorage.getItem(key)])
                                    )
                                };
                            """)
                            storage_file = cookies_file.with_suffix('.storage.json')
                            with open(storage_file, 'w', encoding='utf-8') as f:
                                json.dump(storage_data, f, indent=2, ensure_ascii=False)
                            print(f"[DEBUG] Сохранены данные хранилища в {storage_file.name}")
                        except:
                            pass  # Не критично если не получилось
                        
                        print(f"[OK] Cookies сохранены ({len(cleaned_cookies)} cookies)")
                        print(f"[DEBUG] Домены: {set([c.get('domain', '') for c in cleaned_cookies])}")
                        print(f"[DEBUG] Cookies также сохранены в {json_file.name} для проверки")
                    except Exception as e:
                        print(f"[ERROR] Не удалось сохранить cookies: {e}")
                        import traceback
                        traceback.print_exc()
                    break
                
                if waited_auth % 10 == 0:
                    print(f"[INFO] Ожидание авторизации... ({waited_auth}/{max_wait_auth} сек)")
            
            if not is_authorized:
                print("[ERROR] Авторизация не завершена за отведенное время")
                if driver:
                    driver.quit()
                return None
        
        if not is_authorized:
            print("[ERROR] Не удалось авторизоваться")
            if driver:
                driver.quit()
            return None
        
        # Переходим на страницу цен
        print(f"[INFO] Перехожу на страницу цен: {wb_prices_url}")
        driver.get(wb_prices_url)
        time.sleep(5)  # Увеличил время ожидания
        
        # Проверяем еще раз авторизацию после перехода
        current_url = driver.current_url.lower()
        if not check_authorization(driver) or ("login" in current_url or "auth" in current_url):
            print("[WARN] После перехода обнаружена страница авторизации")
            print("[INFO] Пробую перезагрузить cookies и повторить переход...")
            
            # Пробуем еще раз загрузить cookies
            if cookies_file.exists():
                try:
                    import pickle
                    driver.get(wb_base_url)
                    time.sleep(2)
                    with open(cookies_file, 'rb') as f:
                        cookies = pickle.load(f)
                        for cookie in cookies:
                            try:
                                driver.add_cookie(cookie)
                            except:
                                pass
                    driver.refresh()
                    time.sleep(3)
                    
                    # Пробуем снова перейти на страницу цен
                    driver.get(wb_prices_url)
                    time.sleep(5)
                    current_url = driver.current_url.lower()
                except:
                    pass
            
            # Если все еще на странице авторизации - даем возможность авторизоваться вручную
            if "login" in current_url or "auth" in current_url:
                if headless:
                    print("[ERROR] Браузер в headless режиме - невозможно авторизоваться")
                    if driver:
                        driver.quit()
                    return None
                
                # Браузер открыт - даем время на ручную авторизацию через SMS
                print("[INFO] Cookies не помогли - требуется авторизация через SMS")
                print("[INFO] Браузер открыт - авторизуйтесь вручную")
                print("[INFO] Ожидаю максимум 60 секунд для авторизации...")
                
                max_wait_auth = 60
                waited_auth = 0
                while waited_auth < max_wait_auth:
                    time.sleep(2)
                    waited_auth += 2
                    current_url_check = driver.current_url.lower()
                    
                    if check_authorization(driver):
                        print("[OK] Авторизация обнаружена!")
                        
                        # Сохраняем новые cookies (та же логика что и выше)
                        try:
                            import pickle
                            import json
                            time.sleep(2)
                            driver.get(wb_base_url)
                            time.sleep(3)
                            all_cookies = driver.get_cookies()
                            
                            cleaned_cookies = []
                            for cookie in all_cookies:
                                clean_cookie = {
                                    'name': cookie.get('name'),
                                    'value': cookie.get('value'),
                                    'domain': cookie.get('domain', '.wildberries.ru'),
                                    'path': cookie.get('path', '/'),
                                }
                                if 'expiry' in cookie:
                                    clean_cookie['expiry'] = cookie['expiry']
                                if 'secure' in cookie:
                                    clean_cookie['secure'] = cookie['secure']
                                if 'httpOnly' in cookie:
                                    clean_cookie['httpOnly'] = cookie['httpOnly']
                                
                                if 'domain' in clean_cookie:
                                    domain = clean_cookie['domain']
                                    if domain and 'wildberries.ru' in domain:
                                        if not domain.startswith('.'):
                                            clean_cookie['domain'] = '.' + domain.split('://')[-1].split('/')[0]
                                    else:
                                        clean_cookie['domain'] = '.wildberries.ru'
                                
                                cleaned_cookies.append(clean_cookie)
                            
                            with open(cookies_file, 'wb') as f:
                                pickle.dump(cleaned_cookies, f)
                            
                            json_file = cookies_file.with_suffix('.json')
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump(cleaned_cookies, f, indent=2, ensure_ascii=False)
                            
                            print(f"[OK] Новые cookies сохранены ({len(cleaned_cookies)} cookies)")
                            print(f"[DEBUG] Домены: {set([c.get('domain', '') for c in cleaned_cookies])}")
                        except Exception as e:
                            print(f"[ERROR] Не удалось сохранить cookies: {e}")
                            import traceback
                            traceback.print_exc()
                        
                        # Переходим снова на страницу цен
                        driver.get(wb_prices_url)
                        time.sleep(5)
                        current_url = driver.current_url.lower()
                        break
                    
                    if waited_auth % 10 == 0:
                        print(f"[INFO] Ожидание авторизации... ({waited_auth}/{max_wait_auth} сек)")
                
                # Финальная проверка
                if not check_authorization(driver) or ("login" in current_url or "auth" in current_url):
                    print("[ERROR] Не удалось авторизоваться - cookies невалидны или истекли")
                    print("[INFO] Удалите файл wb_cookies.pkl и запустите скрипт снова для новой авторизации")
                    if driver:
                        driver.quit()
                    return None
        
        # Шаг 1: Ищем меню "Цены и скидки"
        print("[INFO] Шаг 1: Ищу меню 'Цены и скидки'...")
        menu_selectors = [
            "//*[contains(text(), 'Цены и скидки')]",
            "//*[contains(text(), 'Товары и цены')]",
            "//button[contains(., 'Цены')]",
            "//a[contains(., 'Цены')]",
        ]
        
        menu_element = None
        for selector in menu_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed():
                        menu_element = elem
                        print(f"[OK] Найдено меню: '{elem.text[:50]}'")
                        break
                if menu_element:
                    break
            except:
                continue
        
        if menu_element:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", menu_element)
                time.sleep(0.5)
                menu_element.click()
                print("[OK] Меню открыто")
                time.sleep(2)
            except:
                pass
        
        # Шаг 2: Ищем кнопку "Обновить через Excel"
        print("[INFO] Шаг 2: Ищу кнопку 'Обновить через Excel'...")
        excel_selectors = [
            "//*[contains(text(), 'Обновить через Excel')]",
            "//*[contains(text(), 'Excel') and contains(text(), 'Обновить')]",
            "//button[contains(., 'Excel')]",
            "//a[contains(., 'Excel')]",
        ]
        
        excel_button = None
        for selector in excel_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    text = elem.text.lower()
                    if "excel" in text and elem.is_displayed() and elem.is_enabled():
                        excel_button = elem
                        print(f"[OK] Найдена кнопка: '{elem.text[:50]}'")
                        break
                if excel_button:
                    break
            except:
                continue
        
        if not excel_button:
            print("[ERROR] Кнопка 'Обновить через Excel' не найдена")
            if driver:
                driver.quit()
            return None
        
        print("[INFO] Кликаю на кнопку 'Обновить через Excel'...")
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", excel_button)
            time.sleep(1)
            excel_button.click()
            print("[OK] Кнопка нажата")
            time.sleep(3)  # Ждем открытия выпадающего меню
        except Exception as e:
            print(f"[WARN] Ошибка при клике: {e}, пробую через JavaScript")
            try:
                driver.execute_script("arguments[0].click();", excel_button)
                time.sleep(3)
            except:
                pass
        
        # Шаг 3: В выпадающем меню выбираем "Цены и скидки" (верхняя строчка)
        print("[INFO] Шаг 3: Ищу пункт 'Цены и скидки' в выпадающем меню...")
        time.sleep(3)  # Увеличил время ожидания появления выпадающего меню
        
        # Сначала выводим все элементы меню для диагностики
        print("[DEBUG] Поиск всех элементов выпадающего меню...")
        try:
            # Ищем все возможные элементы меню
            menu_elements = driver.find_elements(By.XPATH, "//*[@role='menuitem'] | //*[@role='option'] | //li | //a | //div[contains(@class, 'menu')] | //div[contains(@class, 'dropdown')]")
            visible_menu_items = []
            for elem in menu_elements:
                try:
                    if elem.is_displayed():
                        text = (elem.text or "").strip()
                        if text:
                            visible_menu_items.append((elem.tag_name, text[:60]))
                except:
                    pass
            
            if visible_menu_items:
                print(f"[DEBUG] Найдено {len(visible_menu_items)} видимых элементов меню:")
                for tag, text in visible_menu_items[:10]:
                    print(f"  - {tag}: '{text}'")
            else:
                print("[DEBUG] Видимые элементы меню не найдены")
        except:
            pass
        
        prices_menu_item = None
        menu_item_selectors = [
            "//*[@role='menuitem'][contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
            "//a[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
            "//button[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
            "//li[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
            "//div[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
            "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'цены') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скидки')]",
        ]
        
        for attempt in range(10):
            for selector in menu_item_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = (elem.text or "").strip().lower()
                        if "цены" in text and "скидки" in text and elem.is_displayed():
                            prices_menu_item = elem
                            print(f"[OK] Найден пункт меню: '{elem.text[:50]}'")
                            break
                    if prices_menu_item:
                        break
                except:
                    continue
            if prices_menu_item:
                break
            if attempt < 9:
                time.sleep(1)
                print(f"[DEBUG] Поиск пункта меню... попытка {attempt + 1}/10")
        
        if prices_menu_item:
            print("[INFO] Кликаю на 'Цены и скидки'...")
            try:
                # Пробуем убрать перекрывающий элемент или кликнуть через JavaScript
                try:
                    # Скроллим к элементу
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prices_menu_item)
                    time.sleep(0.5)
                    # Сначала пробуем обычный клик
                    prices_menu_item.click()
                    print("[OK] Пункт меню выбран (обычный клик)")
                except Exception as e:
                    print(f"[WARN] Обычный клик не сработал: {e}, пробую через JavaScript")
                    # Кликаем через JavaScript - это обходит перекрывающие элементы
                    driver.execute_script("arguments[0].click();", prices_menu_item)
                    print("[OK] Пункт меню выбран (через JavaScript)")
                
                # Проверяем что модальное окно появилось
                print("[INFO] Ожидаю открытия модального окна после клика...")
                time.sleep(3)
                
                # Проверяем появилось ли модальное окно
                try:
                    modal_check = driver.find_elements(By.XPATH, "//*[contains(text(), 'Шаг 1') or contains(text(), 'Сформируйте шаблон') or contains(text(), 'Обновить цены и скидки через Excel')]")
                    if modal_check:
                        print("[OK] Модальное окно обнаружено после клика на 'Цены и скидки'")
                    else:
                        print("[WARN] Модальное окно не обнаружено, но продолжаю...")
                except:
                    pass
                
                time.sleep(2)  # Дополнительное ожидание
            except Exception as e:
                print(f"[ERROR] Ошибка при клике: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[ERROR] Пункт 'Цены и скидки' не найден в выпадающем меню!")
            print("[DEBUG] Попробуйте проверить вручную, что выпадающее меню открылось после клика на 'Обновить через Excel'")
            if driver:
                driver.quit()
            return None
        
        # Шаг 4: В модальном окне ищем кнопки "Сформировать шаблон" и "Скачать шаблон"
        print("[INFO] Шаг 4: Ищу кнопки в модальном окне...")
        print("[INFO] Ожидаю открытия модального окна...")
        
        # Ждем появления модального окна - ищем по тексту "Шаг 1" или "Сформируйте шаблон"
        try:
            print("[DEBUG] Ожидаю появления текста 'Шаг 1' или 'Сформируйте шаблон' в модальном окне...")
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Шаг 1')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Сформируйте шаблон')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Сформировать шаблон')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@role, 'dialog')]"))
                )
            )
            print("[OK] Модальное окно обнаружено")
            time.sleep(2)  # Дополнительное ожидание для полной загрузки
        except:
            print("[WARN] Модальное окно не найдено стандартными методами, продолжаю поиск кнопки...")
            time.sleep(3)
        
        # Ищем кнопку "Сформировать шаблон" - это первая (левая) кнопка из двух рядом
        create_button = None
        print("[DEBUG] Поиск кнопки 'Сформировать шаблон'...")
        
        for attempt in range(15):
            try:
                # Сначала пробуем найти модальное окно и искать кнопки только внутри него
                modal_container = None
                try:
                    # Ищем модальное окно по разным признакам
                    modal_selectors = [
                        "//*[@role='dialog']",
                        "//*[contains(@class, 'modal')]",
                        "//*[contains(@class, 'dialog')]",
                        "//*[contains(@class, 'Modal')]",
                        "//*[contains(@class, 'Dialog')]",
                        "//div[contains(., 'Шаг 1')]",
                    ]
                    for selector in modal_selectors:
                        modals = driver.find_elements(By.XPATH, selector)
                        for modal in modals:
                            if modal.is_displayed():
                                modal_container = modal
                                print(f"[DEBUG] Найдено модальное окно: {selector}")
                                break
                        if modal_container:
                            break
                except:
                    pass
                
                # Ищем кнопки - если есть модальное окно, ищем внутри него
                if modal_container:
                    all_buttons = modal_container.find_elements(By.XPATH, ".//button | .//a | .//*[@role='button'] | .//*[@type='button'] | .//*[contains(@class, 'button')] | .//*[contains(@class, 'Button')]")
                    print(f"[DEBUG] Поиск кнопок внутри модального окна: найдено {len(all_buttons)} кнопок")
                else:
                    all_buttons = driver.find_elements(By.XPATH, "//button | //a | //*[@role='button'] | //*[@type='button'] | //*[contains(@class, 'button')] | //*[contains(@class, 'Button')]")
                    print(f"[DEBUG] Поиск кнопок на всей странице: найдено {len(all_buttons)} кнопок")
                
                # Сначала ищем кнопку "Сформировать шаблон" (левая кнопка из двух рядом)
                # Стратегия: ищем все кнопки с текстом содержащим "сформировать", и берем ПЕРВУЮ (левую)
                
                candidate_buttons = []
                
                for btn in all_buttons:
                    try:
                        if not btn.is_displayed():
                            continue
                            
                        # Получаем текст кнопки
                        text = (btn.text or "").strip()
                        text_lower = text.lower().replace('\n', ' ').replace('\r', ' ')
                        
                        # Проверяем что кнопка содержит "сформировать" и "шаблон"
                        if "сформировать" in text_lower and "шаблон" in text_lower:
                            # Это может быть либо отдельная кнопка, либо контейнер
                            # Если это контейнер с обеими кнопками, ищем дочерние
                            if "скачать" in text_lower:
                                # Это контейнер - ищем дочерние кнопки
                                try:
                                    child_buttons = btn.find_elements(By.XPATH, ".//button | .//a | .//*[@role='button'] | .//*[@type='button']")
                                    for child_btn in child_buttons:
                                        if not child_btn.is_displayed():
                                            continue
                                        child_text = (child_btn.text or "").strip().lower()
                                        if "сформировать" in child_text and "шаблон" in child_text and "скачать" not in child_text:
                                            if child_btn.is_enabled():
                                                # Получаем позицию элемента
                                                try:
                                                    location = child_btn.location
                                                    candidate_buttons.append((location['x'], child_btn, child_text))
                                                except:
                                                    candidate_buttons.append((0, child_btn, child_text))
                                except:
                                    pass
                            else:
                                # Отдельная кнопка "Сформировать шаблон"
                                if btn.is_enabled():
                                    try:
                                        location = btn.location
                                        candidate_buttons.append((location['x'], btn, text_lower))
                                    except:
                                        candidate_buttons.append((0, btn, text_lower))
                        
                        # Также проверяем по атрибутам
                        aria_label = (btn.get_attribute('aria-label') or "").lower()
                        title = (btn.get_attribute('title') or "").lower()
                        if ("сформировать" in aria_label and "шаблон" in aria_label and "скачать" not in aria_label) or \
                           ("сформировать" in title and "шаблон" in title and "скачать" not in title):
                            if btn.is_enabled():
                                try:
                                    location = btn.location
                                    candidate_buttons.append((location['x'], btn, text_lower if text_lower else 'по атрибутам'))
                                except:
                                    candidate_buttons.append((0, btn, text_lower if text_lower else 'по атрибутам'))
                    except Exception as e:
                        continue
                
                # Если нашли кандидатов, берем самую левую (первую по X координате)
                if candidate_buttons:
                    candidate_buttons.sort(key=lambda x: x[0])  # Сортируем по X координате (слева направо)
                    create_button = candidate_buttons[0][1]
                    print(f"[OK] Найдена кнопка 'Сформировать шаблон' (самая левая из {len(candidate_buttons)}): '{candidate_buttons[0][2][:60]}'")
                else:
                    # Если не нашли по координатам, продолжаем обычный поиск
                    for btn in all_buttons:
                        try:
                            if not btn.is_displayed():
                                continue
                            text = (btn.text or "").strip().lower()
                            if "сформировать" in text and "шаблон" in text and "скачать" not in text:
                                if btn.is_enabled():
                                    create_button = btn
                                    print(f"[OK] Найдена кнопка 'Сформировать шаблон': '{text[:60]}'")
                                    break
                        except:
                            continue
                
                if create_button:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Ошибка при поиске: {e}")
            
            if attempt < 14:
                time.sleep(1)
                if attempt % 3 == 0:
                    print(f"[INFO] Поиск кнопки 'Сформировать шаблон'... попытка {attempt + 1}/15")
        
        # Если не нашли, выводим расширенную диагностику
        if not create_button:
            print("[DEBUG] Кнопка 'Сформировать шаблон' не найдена. Расширенная диагностика:")
            try:
                # Ищем все видимые элементы с текстом содержащим "формировать" или "шаблон"
                print("[DEBUG] Поиск элементов содержащих 'формировать' или 'шаблон':")
                text_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'формировать') or contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'шаблон') or contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скачать')]")
                for elem in text_elements[:10]:
                    try:
                        if elem.is_displayed():
                            text = (elem.text or "").strip()[:80]
                            tag = elem.tag_name
                            print(f"  - {tag}: '{text}'")
                    except:
                        pass
                
                # Список всех видимых кнопок
                print("[DEBUG] Список всех видимых кнопок:")
                all_buttons = driver.find_elements(By.XPATH, "//button | //a | //*[@role='button'] | //*[@type='button'] | //*[contains(@class, 'button')] | //*[contains(@class, 'Button')]")
                visible_count = 0
                for btn in all_buttons:
                    try:
                        if btn.is_displayed():
                            text = (btn.text or "").strip()
                            if not text:
                                continue
                            tag = btn.tag_name
                            enabled = "enabled" if btn.is_enabled() else "disabled"
                            print(f"  - {tag} ({enabled}): '{text[:80]}'")
                            visible_count += 1
                            if visible_count >= 20:
                                print("[DEBUG] ... (показано 20 из всех)")
                                break
                    except:
                        pass
            except Exception as e:
                print(f"[DEBUG] Ошибка при диагностике: {e}")
            
            print("[ERROR] Кнопка 'Сформировать шаблон' не найдена")
            print("[INFO] Попробуйте запустить скрипт еще раз или проверьте, что модальное окно открылось")
            if driver:
                driver.quit()
            return None
        
        # Шаг 4.1: Кликаем на кнопку "Сформировать шаблон"
        print("[INFO] Нажимаю кнопку 'Сформировать шаблон'...")
        try:
            # Сохраняем текст кнопки до клика для проверки
            button_text_before = create_button.text if create_button.text else ""
            print(f"[DEBUG] Текст кнопки до клика: '{button_text_before[:50]}'")
            
            # Скроллим и ждем
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", create_button)
            time.sleep(1)
            
            # Убеждаемся что кнопка видима и доступна
            if not create_button.is_displayed():
                print("[WARN] Кнопка не видима, пробую скролл еще раз...")
                driver.execute_script("window.scrollTo(0, arguments[0].getBoundingClientRect().top + window.pageYOffset - 200);", create_button)
                time.sleep(1)
            
            if not create_button.is_enabled():
                print("[WARN] Кнопка недоступна (disabled)")
            
            # Пробуем обычный клик
            clicked = False
            try:
                # Проверяем что кнопка все еще доступна перед кликом
                if not create_button.is_enabled():
                    print("[ERROR] Кнопка стала недоступна перед кликом!")
                    if driver:
                        driver.quit()
                    return None
                
                # Проверяем что элемент действительно видимый
                is_visible = driver.execute_script("""
                    var elem = arguments[0];
                    return elem.offsetWidth > 0 && elem.offsetHeight > 0 && 
                           window.getComputedStyle(elem).display !== 'none' &&
                           window.getComputedStyle(elem).visibility !== 'hidden';
                """, create_button)
                
                if not is_visible:
                    print("[WARN] Элемент не видимый по JavaScript проверке, пробую скролл еще раз...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_button)
                    time.sleep(1)
                
                create_button.click()
                print("[OK] Кнопка 'Сформировать шаблон' нажата (обычный клик)")
                
                # Проверяем что клик сработал - ждем небольшое изменение
                time.sleep(1.5)
                clicked_successfully = False
                try:
                    # Проверяем несколько признаков успешного клика
                    # 1. Кнопка стала недоступной
                    if not create_button.is_enabled():
                        print("[DEBUG] ✓ Кнопка стала недоступна после клика - клик сработал!")
                        clicked_successfully = True
                    else:
                        # 2. Проверяем что появился индикатор загрузки
                        loading_check = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'формирова') or contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'загрузк')]")
                        if loading_check and any(e.is_displayed() for e in loading_check):
                            print("[DEBUG] ✓ Обнаружен индикатор формирования - клик сработал!")
                            clicked_successfully = True
                        else:
                            print("[DEBUG] ⚠ Кнопка все еще доступна и нет индикатора, но продолжаю...")
                except:
                    pass  # Элемент мог измениться
                
                if not clicked_successfully:
                    print("[WARN] Не уверен что клик сработал, но продолжаю...")
                
                clicked = True
            except Exception as e:
                print(f"[WARN] Обычный клик не сработал: {e}, пробую через JavaScript")
                try:
                    # Пробуем клик через JavaScript с более точным позиционированием
                    driver.execute_script("""
                        var elem = arguments[0];
                        var rect = elem.getBoundingClientRect();
                        var x = rect.left + rect.width / 2;
                        var y = rect.top + rect.height / 2;
                        var event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        });
                        elem.dispatchEvent(event);
                    """, create_button)
                    print("[OK] Кнопка 'Сформировать шаблон' нажата (через JavaScript с событием)")
                    clicked = True
                except Exception as e2:
                    print(f"[WARN] JavaScript клик через событие не сработал: {e2}, пробую простой JavaScript клик")
                    try:
                        driver.execute_script("arguments[0].click();", create_button)
                        print("[OK] Кнопка 'Сформировать шаблон' нажата (через простой JavaScript)")
                        clicked = True
                    except Exception as e3:
                        print(f"[WARN] Простой JavaScript клик не сработал: {e3}, пробую ActionChains")
                        # Пробуем через действия
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(create_button).pause(0.5).click().perform()
                            print("[OK] Кнопка 'Сформировать шаблон' нажата (через ActionChains)")
                            clicked = True
                        except Exception as e4:
                            print(f"[ERROR] ActionChains клик не сработал: {e4}")
            
            if not clicked:
                print("[ERROR] Не удалось кликнуть на кнопку 'Сформировать шаблон'")
                if driver:
                    driver.quit()
                return None
            
            # Ждем формирования шаблона - проверяем что появился индикатор или изменилось состояние
            print("[INFO] Ожидаю формирования шаблона...")
            time.sleep(3)
            
            # Проверяем что формирование началось
            formation_started = False
            max_formation_wait = 30
            waited_formation = 0
            
            try:
                # Сохраняем начальное состояние кнопки "Скачать шаблон" (если есть)
                initial_download_button_state = None
                download_buttons_initial = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скачать') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'шаблон')]")
                for btn in download_buttons_initial:
                    if btn.is_displayed():
                        initial_download_button_state = btn.is_enabled()
                        break
                
                # Ищем признаки начала формирования
                while waited_formation < max_formation_wait and not formation_started:
                    time.sleep(1)
                    waited_formation += 1
                    
                    # Проверяем есть ли элементы с текстом "формирование", "загрузка" и т.д.
                    loading_indicators = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'формирова') or contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'загрузк') or contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'подождит')]")
                    if loading_indicators and any(elem.is_displayed() for elem in loading_indicators):
                        print("[DEBUG] Обнаружен индикатор формирования/загрузки - формирование началось")
                        formation_started = True
                        break
                    
                    # Проверяем изменение состояния кнопки "Скачать шаблон"
                    download_buttons = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'скачать') and contains(translate(text(), 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'), 'шаблон')]")
                    for btn in download_buttons:
                        if btn.is_displayed():
                            current_state = btn.is_enabled()
                            # Если кнопка стала доступна (была недоступна, стала доступна)
                            if current_state and (initial_download_button_state is False or initial_download_button_state is None):
                                print("[DEBUG] Кнопка 'Скачать шаблон' стала доступна - шаблон готов")
                                formation_started = True
                                break
                    
                    if waited_formation % 5 == 0:
                        print(f"[DEBUG] Ожидание формирования... ({waited_formation}/{max_formation_wait} сек)")
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке формирования: {e}")
            
            if formation_started:
                print("[OK] Формирование шаблона началось, ожидаю завершения...")
                time.sleep(5)  # Даем время на формирование после обнаружения признаков
            else:
                print("[WARN] Признаки формирования не обнаружены, но продолжаю...")
                time.sleep(8)  # Даем больше времени на всякий случай
            
            print("[OK] Ожидание формирования завершено")
        except Exception as e:
            print(f"[ERROR] Ошибка при клике на 'Сформировать шаблон': {e}")
            import traceback
            traceback.print_exc()
            if driver:
                driver.quit()
            return None
        
        # Шаг 5: Ищем и кликаем на кнопку "Скачать шаблон" (правая кнопка из двух рядом)
        print("[INFO] Шаг 5: Ищу кнопку 'Скачать шаблон' в модальном окне...")
        download_button = None
        max_wait = 30
        waited = 0
        
        while waited < max_wait:
            try:
                # Ищем все кнопки в модальном окне
                all_buttons = driver.find_elements(By.XPATH, "//button | //a | //*[@role='button'] | //*[@type='button'] | //*[contains(@class, 'button')]")
                
                # Ищем кнопку "Скачать шаблон" - должна содержать слова "скачать" и "шаблон"
                for btn in all_buttons:
                    try:
                        if not btn.is_displayed() or not btn.is_enabled():
                            continue
                            
                        text = (btn.text or "").strip().lower()
                        text_normalized = text.replace('\n', ' ').replace('\r', ' ')
                        
                        # Ищем кнопку с текстом "скачать шаблон"
                        if "скачать" in text_normalized and "шаблон" in text_normalized:
                            download_button = btn
                            print(f"[OK] Найдена кнопка 'Скачать шаблон': '{btn.text[:50] if btn.text else 'нет текста'}'")
                            break
                    except:
                        continue
                
                if download_button:
                    break
                    
            except Exception as e:
                print(f"[DEBUG] Ошибка при поиске: {e}")
            
            time.sleep(2)
            waited += 2
            
            if waited % 5 == 0:
                print(f"[INFO] Поиск кнопки 'Скачать шаблон'... ({waited}/{max_wait} сек)")
        
        if not download_button:
            print("[ERROR] Кнопка 'Скачать шаблон' не найдена после формирования")
            print("[DEBUG] Список видимых кнопок для диагностики:")
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button | //a | //*[@role='button'] | //*[@type='button'] | //*[contains(@class, 'button')]")
                for btn in all_buttons[:10]:
                    try:
                        if btn.is_displayed():
                            text = btn.text[:50] if btn.text else "нет текста"
                            enabled = "enabled" if btn.is_enabled() else "disabled"
                            print(f"  - {enabled}: '{text}'")
                    except:
                        pass
            except:
                pass
            if driver:
                driver.quit()
            return None
        
        # Шаг 5.1: Кликаем на кнопку "Скачать шаблон"
        print("[INFO] Нажимаю кнопку 'Скачать шаблон'...")
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
            time.sleep(0.5)
            # Пробуем обычный клик
            try:
                download_button.click()
                print("[OK] Кнопка 'Скачать шаблон' нажата")
            except Exception as e:
                print(f"[WARN] Обычный клик не сработал: {e}, пробую через JavaScript")
                driver.execute_script("arguments[0].click();", download_button)
                print("[OK] Кнопка 'Скачать шаблон' нажата (через JavaScript)")
            
            time.sleep(3)  # Ждем начала скачивания
        except Exception as e:
            print(f"[ERROR] Ошибка при клике на 'Скачать шаблон': {e}")
            import traceback
            traceback.print_exc()
            if driver:
                driver.quit()
            return None
        
        # Ждем завершения скачивания
        print("[INFO] Ожидаю завершения скачивания...")
        max_wait_file = 60
        waited_file = 0
        start_time = time.time()
        
        # Запоминаем время начала для поиска файлов созданных после этого момента
        initial_time = time.time()
        
        # Запоминаем существующие файлы перед скачиванием
        initial_files = set(Path(download_dir).glob("*.xlsx"))
        initial_files_mtime = {f: os.path.getmtime(f) for f in initial_files}
        print(f"[DEBUG] Существующие файлы перед скачиванием: {len(initial_files)}")
        
        # Также проверяем стандартную директорию Downloads
        downloads_dir = Path.home() / "Downloads"
        if downloads_dir.exists():
            initial_downloads = set(downloads_dir.glob("*.xlsx"))
            initial_downloads_mtime = {f: os.path.getmtime(f) for f in initial_downloads}
            print(f"[DEBUG] Файлы в Downloads: {len(initial_downloads)}")
        else:
            initial_downloads = set()
            initial_downloads_mtime = {}
        
        while waited_file < max_wait_file:
            time.sleep(1)
            waited_file += 1
            current_time = time.time()
            
            # Проверяем целевое директорию - ищем файлы созданные после начала скачивания
            current_files = list(Path(download_dir).glob("*.xlsx"))
            
            for file_path in current_files:
                file_mtime = os.path.getmtime(file_path)
                file_age = current_time - file_mtime
                
                # Файл создан после начала скачивания (с запасом 5 секунд на задержку)
                if file_mtime >= initial_time - 5:
                    # Проверяем что файл не изменяется (скачивание завершено)
                    if file_age >= 2:
                        file_size = file_path.stat().st_size
                        if file_size > 1024:
                            # Проверяем что имя файла похоже на шаблон WB
                            if "шаблон" in file_path.name.lower() or "wb" in file_path.name.lower() or file_path.name.lower().startswith("шаблон"):
                                print(f"[OK] Файл скачан: {file_path.name} ({file_size} bytes)")
                                if driver:
                                    driver.quit()
                                return str(file_path)
            
            # Проверяем Downloads
            if downloads_dir.exists():
                current_downloads = list(downloads_dir.glob("*.xlsx"))
                for file_path in current_downloads:
                    file_mtime = os.path.getmtime(file_path)
                    file_age = current_time - file_mtime
                    
                    # Файл создан после начала скачивания
                    if file_mtime >= initial_time - 5:
                        if file_age >= 2:
                            file_size = file_path.stat().st_size
                            if file_size > 1024:
                                # Проверяем что имя файла похоже на шаблон WB
                                if "шаблон" in file_path.name.lower() or "wb" in file_path.name.lower() or file_path.name.lower().startswith("шаблон"):
                                    print(f"[OK] Файл найден в Downloads: {file_path.name} ({file_size} bytes)")
                                    # Копируем в целевую директорию
                                    import shutil
                                    target_file = Path(download_dir) / file_path.name
                                    shutil.copy2(file_path, target_file)
                                    print(f"[OK] Файл скопирован в целевую директорию: {target_file}")
                                    if driver:
                                        driver.quit()
                                    return str(target_file)
            
            if waited_file % 5 == 0:
                print(f"[INFO] Ожидание скачивания... ({waited_file}/{max_wait_file} сек)")
                # Диагностика - показываем самые новые файлы
                all_files = list(Path(download_dir).glob("*.xlsx"))
                if all_files:
                    newest = max(all_files, key=os.path.getmtime)
                    newest_age = time.time() - os.path.getmtime(newest)
                    print(f"[DEBUG] Самый новый файл: {newest.name} (возраст: {newest_age:.1f} сек)")
        
        # Финальная проверка - берем самый новый файл созданный недавно
        print("[DEBUG] Финальная проверка - ищу самый новый файл...")
        all_files = list(Path(download_dir).glob("*.xlsx"))
        if all_files:
            newest = max(all_files, key=os.path.getmtime)
            newest_age = time.time() - os.path.getmtime(newest)
            if newest_age < 120:  # Создан в последние 2 минуты
                file_size = newest.stat().st_size
                if file_size > 1024:
                    print(f"[OK] Найден недавно созданный файл: {newest.name} ({file_size} bytes, возраст: {newest_age:.1f} сек)")
                    if driver:
                        driver.quit()
                    return str(newest)
        
        print("[WARN] Файл не найден после скачивания или скачивание не завершено")
        print(f"[DEBUG] Финальная проверка - файлов .xlsx в директории: {len(list(Path(download_dir).glob('*.xlsx')))}")
        if driver:
            driver.quit()
        return None
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            try:
                driver.quit()
            except:
                pass
        return None

try:
    from update_wb_stocks_prices import download_excel_template_automated, Config
    
    # Принудительно отключаем headless для теста
    Config.HEADLESS_BROWSER = False
    print("=" * 60)
    print("Тест автоматической загрузки Excel шаблона WB")
    print("=" * 60)
    print(f"AUTO_DOWNLOAD_EXCEL: {Config.AUTO_DOWNLOAD_EXCEL}")
    print(f"HEADLESS_BROWSER: {Config.HEADLESS_BROWSER} (принудительно false для теста)")
    print(f"TARGET_DIR: {Config.TARGET_DIR}")
    print("=" * 60)
    print()
    
    if not Config.AUTO_DOWNLOAD_EXCEL:
        print("[WARN] AUTO_DOWNLOAD_EXCEL отключен в .env")
        print("Добавьте в .env: AUTO_DOWNLOAD_EXCEL=true")
        sys.exit(1)
    
    print("[INFO] Начинаю загрузку Excel шаблона...")
    print()
    
    # Проверяем наличие драйверов
    try:
        from selenium import webdriver
        print("[INFO] Selenium импортирован успешно")
        
        # Пробуем создать драйвер (без запуска браузера)
        try:
            from selenium.webdriver.chrome.options import Options
            print("[INFO] Chrome options доступны")
        except:
            print("[WARN] Chrome options недоступны")
            
        try:
            from selenium.webdriver.edge.options import Options as EdgeOptions
            print("[INFO] Edge options доступны")
        except:
            print("[WARN] Edge options недоступны")
    except Exception as e:
        print(f"[ERROR] Проблема с Selenium: {e}")
        sys.exit(1)
    
    print()
    print("[INFO] Использую автономную функцию для скачивания...")
    print("[INFO] Скрипт будет работать автоматически с сохраненными cookies")
    print()
    
    try:
        # Используем автономную функцию вместо общей
        result = download_excel_only()
    except KeyboardInterrupt:
        print("\n[ERROR] Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Исключение: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n[INFO] download_excel_template_automated() завершился")
    
    if result:
        print()
        print("=" * 60)
        print(f"[SUCCESS] Файл успешно скачан: {result}")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("[FAILED] Не удалось скачать файл")
        print("=" * 60)
        
except ImportError as e:
    print(f"[ERROR] Ошибка импорта: {e}")
    print("Убедитесь, что все зависимости установлены:")
    print("  py -m pip install selenium requests python-dotenv")
except Exception as e:
    print(f"[ERROR] Произошла ошибка: {e}")
    import traceback
    traceback.print_exc()

