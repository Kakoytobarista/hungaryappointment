import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.logger import logger
from src.telegram_notificaion import TelegramNotification


class BaseElementActions:
    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.timeout = timeout

    def wait_for_element_in_center(self, element):
        try:
            WebDriverWait(self.driver, 0.5).until(
                lambda driver: abs(
                    driver.execute_script(
                        "return arguments[0].getBoundingClientRect().top + arguments[0].getBoundingClientRect().height/2 - window.innerHeight/2;",
                        element
                    )
                ) < 10
            )
            logger.info("[ACTION] Element is centered on screen")
        except Exception as e:
            logger.info(f"[WARNING] Element was not perfectly centered: {e}")


    def wait_for_page_load(self):
        try:
            WebDriverWait(self.driver, self.timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            logger.info("[ACTION] Page fully loaded")
        except Exception as e:
            logger.info(f"[ERROR] Page did not load completely within {self.timeout} seconds: {e}")
            raise

    def find_element(self, xpath: str, wait_for: str = 'visible'):
        try:
            if wait_for == 'clickable':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
            elif wait_for == 'present':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            else:
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath))
                )
            return element
        except Exception as e:
            logger.info(f"[ERROR] Failed to find element {xpath} (wait_for={wait_for}): {e}")
            raise

    def click(self, xpath: str):
        try:
            self.wait_for_page_load()
            element = self.find_element(xpath, wait_for='clickable')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            logger.info(f"[ACTION] Scrolled into view: {xpath}")
            self.wait_for_element_in_center(element)

            try:
                element.click()
                logger.info(f"[ACTION] Clicked element normally: {xpath}")
            except Exception as click_exception:
                logger.info(f"[WARNING] Normal click failed, trying JavaScript click for {xpath}: {click_exception}")
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"[ACTION] Clicked element via JavaScript: {xpath}")
        except Exception as e:
            logger.info(f"[ERROR] Failed to click element {xpath}: {e}")
            raise

    def fill(self, xpath: str, value: str):
        try:
            self.wait_for_page_load()
            input_element = self.find_element(xpath, wait_for='present')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            logger.info(f"[ACTION] Scrolled into view: {xpath}")
            self.wait_for_element_in_center(input_element)

            input_element.clear()
            input_element.send_keys(value)
            logger.info(f"[ACTION] Filled element {xpath} with value '{value}'")
        except Exception as e:
            logger.info(f"[ERROR] Failed to fill element {xpath} with value '{value}': {e}")
            raise

class SelectConsulateModal(BaseElementActions):
    ELEMENT = '//h5[contains(normalize-space(text()), "Please select a Consulate")]/../..'
    SUBBOTICA_EMBASSY = '//input[@id="f05149cd-51b4-417d-912b-9b8e1af999b6"]'
    BELGRADE_EMBASSY = '//input[@id="22c5017f-589b-4e30-8347-cc2226fb4572"]'

    def __init__(self, driver):
        super().__init__(driver)

    def select_target_embassy(self, target_embassy: str = SUBBOTICA_EMBASSY):
        if not target_embassy:
            target_embassy = self.SUBBOTICA_EMBASSY
        self.click(self.ELEMENT + target_embassy)
        return MainPage(self.driver)


class SelectTypeOfApplicationModal(BaseElementActions):
    ELEMENT = '//h5[contains(normalize-space(text()), "Applications")]/../..'
    TARGET_TYPE_OF_APPLICATION_VISA_D = '//input[@id="f99c16f2-fc31-49ed-8fd8-e044f6500b14"]'
    TARGET_TYPE_OF_APPLICATION_BELGRADE_VISA_D = '//input[@id="4a8de950-f963-449d-9edd-7840a66f3766"]'
    SAVE_BTN = '//button[@class="btn btn-success"]'

    def __init__(self, driver):
        super().__init__(driver)

    def select_target_embassy(self, target_application_type: str = TARGET_TYPE_OF_APPLICATION_VISA_D):
        if not target_application_type:
            target_application_type = self.TARGET_TYPE_OF_APPLICATION_VISA_D
        self.click(self.ELEMENT + target_application_type)
        self.click(self.ELEMENT + self.SAVE_BTN)
        return MainPage(self.driver)


class MainPage(BaseElementActions):
    SELECT_CONSULATE_MODAL_BTN = '//button[@data-target="#modal2"]'
    SELECT_TYPE_OF_APPLICATION_MODAL_BTN = '//button[@data-target="#modalCases"]'
    CHANGE_LANGUAGE_BUTTON = '//button[@id="langSelector"]'
    ENGLISH_BUTTON = '//a//img[@src="/content/en.png"]'

    NAME_INPUT = '//input[@id="label4"]'
    DATE_OF_BIRTH_INPUT = '//input[@id="birthDate"]'
    PHONE_NUMBER_INPUT = '//input[@id="label9"]'
    EMAIL_ADDRESS_INPUT = '//input[@id="label10"]'
    RE_EMAIL_ADDRESS_INPUT = '//label[contains(text(), "Re-enter the email address")]/..//input'
    CITIZENSHIP_INPUT = '//input[@id="label1000"]'
    PASSPORT_NUMBER_INPUT = '//input[@id="label1001"]'
    RESIDENCE_PERMIT_DATA_INPUT = '//input[@id="label1002"]'
    IHAVE_READ_POLICY_CHECKBOX = '//input[@id="slabel13"]'
    PERSONAL_DATA_CHECKBOX = '//input[@id="label13"]'
    SELECT_APPOINTMENT_BUTTON = '//button[text()="Select date"]'

    NO_AVAILABLE_APPOINTMENTS_FRAME = '//div[contains(text(), "We inform you that there are currently no appointments available. ")]'

    def __init__(self, driver):
        super().__init__(driver)

    def click_select_consulate_modal_button(self):
        logger.info("[ACTION] Clicking on Select Consulate Modal Button")
        self.click(self.SELECT_CONSULATE_MODAL_BTN)
        return SelectConsulateModal(self.driver)

    def click_select_type_of_application_modal_button(self):
        logger.info("[ACTION] Clicking on Select Type of Application Modal Button")
        self.click(self.SELECT_TYPE_OF_APPLICATION_MODAL_BTN)
        return SelectTypeOfApplicationModal(self.driver)

    def click_change_language_button(self):
        logger.info("[ACTION] Clicking on Change Language Button")
        self.click(self.CHANGE_LANGUAGE_BUTTON)

    def click_english_button(self):
        logger.info("[ACTION] Clicking on English Button")
        self.click(self.ENGLISH_BUTTON)

    def click_i_have_read_policy_checkbox(self):
        logger.info("[ACTION] Clicking on 'I have read policy' Checkbox")
        self.click(self.IHAVE_READ_POLICY_CHECKBOX)

    def click_personal_data_checkbox(self):
        logger.info("[ACTION] Clicking on Personal Data Checkbox")
        self.click(self.PERSONAL_DATA_CHECKBOX)

    def click_select_appointment_button(self):
        logger.info("[ACTION] Clicking on Select Appointment Button")
        self.click(self.SELECT_APPOINTMENT_BUTTON)

    def fill_name_input(self, name: str):
        logger.info(f"[ACTION] Filling Name Input with '{name}'")
        self.fill(self.NAME_INPUT, name)

    def fill_date_of_birth_input(self, birth_date: str):
        logger.info(f"[ACTION] Filling Date of Birth Input with '{birth_date}'")
        self.fill(self.DATE_OF_BIRTH_INPUT, birth_date)

    def fill_phone_number_input(self, phone_number: str):
        logger.info(f"[ACTION] Filling Phone Number Input with '{phone_number}'")
        self.fill(self.PHONE_NUMBER_INPUT, phone_number)

    def fill_email_address_input(self, email: str):
        logger.info(f"[ACTION] Filling Email Address Input with '{email}'")
        self.fill(self.EMAIL_ADDRESS_INPUT, email)

    def fill_re_email_address_input(self, re_email: str):
        logger.info(f"[ACTION] Filling Re-Email Address Input with '{re_email}'")
        self.fill(self.RE_EMAIL_ADDRESS_INPUT, re_email)

    def fill_citizenship_input(self, citizenship: str):
        logger.info(f"[ACTION] Filling Citizenship Input with '{citizenship}'")
        self.fill(self.CITIZENSHIP_INPUT, citizenship)

    def fill_passport_number_input(self, passport_number: str):
        logger.info(f"[ACTION] Filling Passport Number Input with '{passport_number}'")
        self.fill(self.PASSPORT_NUMBER_INPUT, passport_number)


    def fill_residence_permit_data_input(self, residence_permit_data: str):
        logger.info(f"[ACTION] Filling Passport Number Input with '{residence_permit_data}'")
        self.fill(self.RESIDENCE_PERMIT_DATA_INPUT, residence_permit_data)

    def _save_screenshot_and_set_tg(self, telegram_bot):
        screenshot_path = f"screenshot_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot_path)
        telegram_bot.send_photo(screenshot_path)
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
            logger.info(f"Screenshot {screenshot_path} deleted.")

    def is_available_appointment_found(self):
        logger.info("[ACTION] Checking if 'No Available Appointments' frame is displayed")
        telegram_bot = TelegramNotification()
        try:
            modal_no_available_appointment = self.find_element(self.NO_AVAILABLE_APPOINTMENTS_FRAME)
            if modal_no_available_appointment.is_displayed():
                TelegramNotification().send_message("AVAILABLE APPOINTMENT IS NOT FOUND")
                self._save_screenshot_and_set_tg(telegram_bot)
                return False
            self._save_screenshot_and_set_tg(telegram_bot)
            return True
        except Exception as e:
            logger.info(f"FOUND APPOINTMENT!: {e}")
            self._save_screenshot_and_set_tg(telegram_bot)
            telegram_bot.send_message(
                "!!!!!HURRY UP PIDR, I FOUND APPOINTMENTS!!!!!\n!!!!!HURRY UP, I FOUND APPOINTMENTS!!!!!"
            )
            return False
