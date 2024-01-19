import logging

from config import log_settings


def configure_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(log_settings.log_level)

    file_handler = logging.FileHandler(filename=log_settings.log_filename)
    stream_handler = logging.StreamHandler()

    file_handler.setLevel(log_settings.log_level)
    stream_handler.setLevel(log_settings.log_level)

    formatter = logging.Formatter(fmt=log_settings.log_format)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
