import os
import time
from datetime import datetime
import requests

from src.logger import logger
from src.parsing import MainPage
from src.utils import get_random_proxy, load_proxies, check_proxy, ProxyConfig


def get_public_ip() -> str:
    try:
        response = requests.get('https://api.ipify.org?format=text', timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Не удалось получить публичный IP: {e}")
        return "Неизвестен"

def main(use_proxy: bool = False):
    logger.info(f'RUN AT {datetime.now()}')
    logger.info(f"Публичный IP: {get_public_ip()}")

    if use_proxy:
        proxy_list = load_proxies(os.path.abspath('proxies.txt'))
        while True:
            proxy_string = get_random_proxy(proxy_list)
            config = ProxyConfig(enabled=True, proxy_string=proxy_string, docker=True)
            driver = check_proxy(config)
            if driver:
                logger.info(f"Прокси {proxy_string} работает!")
                break
            logger.info(f"Ошибка с прокси {proxy_string}, пробуем снова...")
            time.sleep(2)
    else:
        config = ProxyConfig(enabled=False, docker=True)
        driver = check_proxy(config)

    if not driver:
        logger.error("Не удалось запустить драйвер.")
        return

    main_page = MainPage(driver)

    main_page.click_change_language_button()
    main_page.click_english_button()

    # Выбираем консульство
    select_consulate_modal = main_page.click_select_consulate_modal_button()
    main_page = select_consulate_modal.select_target_embassy()

    # Выбираем тип визы
    select_type_modal = main_page.click_select_type_of_application_modal_button()
    main_page = select_type_modal.select_target_embassy()

    # Заполняем форму
    random_name = "Aslan Gurbanov"
    random_birth_date = "30/10/1997"
    random_phone = f"+381616328012"
    random_email = f"heydevaslan@gmail.com"
    random_citizenship = "Russian Federation"
    random_passport = f"55 1373394"

    main_page.fill_name_input(random_name)
    main_page.fill_date_of_birth_input(random_birth_date)
    main_page.fill_phone_number_input(random_phone)
    main_page.fill_email_address_input(random_email)
    main_page.fill_re_email_address_input(random_email)
    main_page.fill_citizenship_input(random_citizenship)
    main_page.fill_passport_number_input(random_passport)

    # Кликаем чекбоксы
    main_page.click_i_have_read_policy_checkbox()
    main_page.click_personal_data_checkbox()

    # Нажимаем "Select date"
    main_page.click_select_appointment_button()
    main_page.is_available_appointment_found()
    driver.quit()


logger.info("START SCRIPT:")
main()
