"""
Конфигурация логирования для сервиса расписания.
Логирует все действия с экспортом в файл и консоль.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# Создаём директорию для логов
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Имя файла лога с датой
log_filename = LOG_DIR / f"schedule_{datetime.now().strftime('%Y-%m-%d')}.log"


def setup_logging():
    """Настройить логирование для всего модуля schedule"""
    
    # Создаём основной логгер
    logger = logging.getLogger("schedule")
    logger.setLevel(logging.DEBUG)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # === ЛОГИРОВАНИЕ В ФАЙЛ ===
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5  # Хранить 5 файлов
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # === ЛОГИРОВАНИЕ В КОНСОЛЬ ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # === ОТДЕЛЬНЫЙ ЛОГГЕР ДЛЯ ОШИБОК ===
    error_log_file = LOG_DIR / "schedule_errors.log"
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info("🚀 Логирование инициализировано")
    logger.info(f"📁 Логи сохраняются в: {LOG_DIR}")
    
    return logger


# Инициализируем при импорте
logger = setup_logging()

# Логирование для каждого модуля
def get_logger(name: str) -> logging.Logger:
    """Получить логгер для конкретного модуля"""
    return logging.getLogger(f"schedule.{name}")
