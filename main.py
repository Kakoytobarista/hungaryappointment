import os
import time

from src.logger import logger
from src.parsing import MainPage
from src.utils import get_random_proxy, load_proxies, check_proxy


def main():
    proxies_path = os.path.abspath('proxies.txt')
    proxy_list = load_proxies(proxies_path)

    while True:
        proxy_string = get_random_proxy(proxy_list)
        driver = check_proxy(proxy_string)
        if driver:
            logger.info(f"Прокси {proxy_string} работает!")
            break
        else:
            logger.info(f"Ошибка с прокси {proxy_string}, пробуем снова...")
            time.sleep(2)

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
    appointments_available = main_page.is_available_appointment_found()
    driver.quit()
    time.sleep(5 * 60)


logger.info("START SCRIPT:")
main()
