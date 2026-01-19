import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


# создания и настройки логов
def setup_logger(name: str, log_file: str, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = RotatingFileHandler(
        LOG_DIR / log_file,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


app_logger = setup_logger("app", "app.log")

error_logger = setup_logger("errors", "errors.log", logging.ERROR)
