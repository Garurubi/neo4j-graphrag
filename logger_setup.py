import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name:str, log_level=logging.INFO) -> logging.Logger:
    filename = f'./log/{datetime.now().strftime("%Y%m%d")}_{name}.log'
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y%m%d %H:%M:%S')
    handler = RotatingFileHandler(filename, maxBytes=1024 * 1024 * 10, backupCount=60, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger