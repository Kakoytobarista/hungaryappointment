import requests

from src.logger import logger


class TelegramNotification:
    def __init__(self, chat_id_fail: str = "-4682798986", chat_id_success: str = "-4616950706", token: str = "7948876999:AAEyc9yuUZUJR8KwGmdtKReUAzwGMB-0LN8"):
        self.token = token
        self.chat_id_fail = chat_id_fail
        self.chat_id_success = chat_id_success
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.api_url_photo = f"https://api.telegram.org/bot{self.token}/sendPhoto"

    def send_message(self, message: str, is_appointment_found: bool):
        try:
            payload = {
                "chat_id": self.chat_id_success if is_appointment_found else self.chat_id_fail,
                "text": message
            }
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
            logger.info(f"[ACTION] Message sent to Telegram: {message}")
        except Exception as e:
            logger.info(f"[ERROR] Failed to send message to Telegram: {e}")

    def send_photo(self, photo_path: str, is_appointment_found: bool):
        try:
            with open(photo_path, 'rb') as photo:
                payload = {
                    "chat_id": self.chat_id_success if is_appointment_found else self.chat_id_fail,
                }
                files = {
                    "photo": photo
                }
                response = requests.post(self.api_url_photo, data=payload, files=files)
                response.raise_for_status()
                logger.info(f"[ACTION] Photo sent to Telegram: {photo_path}")
        except Exception as e:
            logger.info(f"[ERROR] Failed to send photo to Telegram: {e}")
