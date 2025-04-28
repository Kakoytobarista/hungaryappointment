import random

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

from src.logger import logger
from src.parsing import MainPage


def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines() if line.strip()]
    return proxies

def get_random_proxy(proxies):
    return random.choice(proxies)

def check_proxy(proxy_string, docker=False):
    try:
        user_info, host_port = proxy_string.split('@')
        username, password = user_info.split(':')
        host, port = host_port.split(':')

        proxy_url = f"http://{username}:{password}@{host}:{port}"

        seleniumwire_options = {
            "proxy": {
                "http": proxy_url,
                "https": proxy_url,
                "no_proxy": "localhost,127.0.0.1"
            }
        }

        chrome_options = Options()
        if docker:
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            service = Service("/usr/lib/chromium-browser/chromedriver")
        else:
            service = Service(ChromeDriverManager().install())

        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless')  # Отключаем UI
        chrome_options.add_argument('--disable-gpu')  # Отключаем GPU, если нужно
        chrome_options.add_argument('--no-sandbox')  # Для безопасности
        chrome_options.add_argument('--disable-software-rasterizer')
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Отключаем изображения
            "profile.managed_default_content_settings.plugins": 1,  # Отключаем плагины
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options,
            seleniumwire_options=seleniumwire_options
        )

        driver.get('https://konzinfoidopont.mfa.gov.hu/')
        driver.maximize_window()
        ip_not_banned = MainPage(driver).find_element(xpath=MainPage.CHANGE_LANGUAGE_BUTTON)

        if driver.current_url == 'https://konzinfoidopont.mfa.gov.hu/' and ip_not_banned:
            return driver
        else:
            driver.quit()
            return False
    except Exception as e:
        logger.info(f"Ошибка с прокси {proxy_string}: {e}")
        return False
