import logging


def setup_logger(log_file):
    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.INFO)

    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Создание обработчика для записи в файл
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Добавление обработчика к логгеру
    logger.addHandler(file_handler)

    return logger


log_file = "actions.log"
logger = setup_logger(log_file)
