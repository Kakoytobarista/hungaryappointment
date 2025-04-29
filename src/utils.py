import random
from dataclasses import dataclass
from typing import Optional

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


@dataclass
class ProxyConfig:
    enabled: bool = False
    proxy_string: Optional[str] = None
    docker: bool = False


def build_chrome_options(docker: bool) -> Options:
    chrome_options = Options()
    if docker:
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-software-rasterizer')
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.plugins": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)
    return chrome_options


def build_proxy_options(proxy_string: str) -> dict:
    user_info, host_port = proxy_string.split('@')
    username, password = user_info.split(':')
    host, port = host_port.split(':')

    proxy_url = f"http://{username}:{password}@{host}:{port}"
    return {
        "proxy": {
            "http": proxy_url,
            "https": proxy_url,
            "no_proxy": "localhost,127.0.0.1"
        }
    }


def check_proxy(config: ProxyConfig):
    try:
        options = build_chrome_options(config.docker)
        service = Service(
            "/usr/lib/chromium-browser/chromedriver" if config.docker else ChromeDriverManager().install()
        )

        seleniumwire_options = build_proxy_options(config.proxy_string) if config.enabled and config.proxy_string else None

        driver = webdriver.Chrome(
            service=service,
            options=options,
            seleniumwire_options=seleniumwire_options
        )

        driver.get('https://konzinfoidopont.mfa.gov.hu/')
        driver.maximize_window()
        ip_not_banned = MainPage(driver).find_element(xpath=MainPage.CHANGE_LANGUAGE_BUTTON)

        if ip_not_banned:
            return driver
        else:
            driver.quit()
            return False

    except Exception as e:
        logger.info(f"Ошибка с прокси {config.proxy_string}: {e}")
        return False