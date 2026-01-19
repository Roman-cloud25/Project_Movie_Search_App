import time
from functools import wraps
from utils.logger import app_logger, error_logger


# декоратор для автоматического логирования времени и результата
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        start_time = time.time()

        app_logger.info(f"ВЫЗОВ ФУНКЦИИ: {func.__name__}")

        try:
            result = func(*args, **kwargs)

            duration = round(time.time() - start_time, 4)
            app_logger.info(f"ЗАВЕРШЕНО: {func.__name__} за {duration} сек.")

            return result
        except Exception as exc:

            error_logger.exception(f"ОШИБКА В {func.__name__}: {exc}")
            raise

    return wrapper
