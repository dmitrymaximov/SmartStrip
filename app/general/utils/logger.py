import logging


def setup_logger(name: str = "SmartStrip", level: int = logging.DEBUG) -> logging.Logger:
    new_logger = logging.getLogger(name)
    new_logger.setLevel(level)

    if not new_logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        new_logger.addHandler(ch)

    return new_logger


logger = setup_logger()
