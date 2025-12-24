"""
Примеры использования логирования в модулях schedule.
"""

# === ПРИМЕР 1: Получить логгер в своем модуле ===

from core.logging_config import get_logger

logger = get_logger("my_service")  # Будет "schedule.my_service"

def my_function():
    logger.info("Начало выполнения функции")
    try:
        # Твой код
        logger.debug("Промежуточное состояние")
        logger.info("Успешно завершено")
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        raise


# === ПРИМЕР 2: Логирование параметров запроса ===

from fastapi import Query

async def export_data(
    instructor: str = Query(None),
    auditorium_ids: List[int] = Query(None)
):
    logger = get_logger("export_api")
    
    logger.info("📊 API запрос получен")
    logger.info(f"   Преподаватель: {instructor}")
    logger.info(f"   Аудитории: {auditorium_ids}")
    
    # Обработка
    logger.info("✅ Запрос обработан успешно")


# === ПРИМЕР 3: Логирование прогресса обработки ===

def process_large_dataset(items):
    logger = get_logger("data_processor")
    
    logger.info(f"🚀 Начало обработки {len(items)} элементов")
    
    processed = 0
    for item in items:
        # Обработка
        processed += 1
        
        if processed % 100 == 0:
            logger.debug(f"   Обработано {processed}/{len(items)} элементов")
    
    logger.info(f"✅ Обработка завершена: {processed} элементов")


# === ПРИМЕР 4: Логирование с контекстом ===

def complex_operation(user_id, operation_type):
    logger = get_logger("user_operations")
    
    logger.info(f"[User {user_id}] Начало операции: {operation_type}")
    
    try:
        # Код
        logger.debug(f"[User {user_id}] Шаг 1 завершен")
        logger.debug(f"[User {user_id}] Шаг 2 завершен")
        logger.info(f"[User {user_id}] {operation_type} успешна")
    except Exception as e:
        logger.error(f"[User {user_id}] Ошибка в {operation_type}: {e}")
        raise


# === ПРИМЕР 5: Логирование производительности ===

import time
from functools import wraps

def log_performance(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.debug(f"▶ Начало: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                logger.info(f"✅ {func.__name__} завершена за {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start
                logger.error(f"❌ {func.__name__} ошибка после {elapsed:.2f}s: {e}")
                raise
        return wrapper
    return decorator

# Использование:
@log_performance(get_logger("export"))
def export_to_excel(filename):
    time.sleep(2)  # Имитация работы
    return filename


# === ПРИМЕР 6: Структурированное логирование ===

def handle_export_request(db, **filters):
    logger = get_logger("export_service")
    
    # Логируем запрос
    logger.info("=" * 60)
    logger.info("🚀 НОВЫЙ ЗАПРОС НА ЭКСПОРТ")
    logger.info("=" * 60)
    logger.info(f"Фильтры:")
    for key, value in filters.items():
        logger.info(f"   - {key}: {value}")
    
    try:
        # Поиск
        logger.info("🔍 Поиск данных...")
        count = db.query().count()
        logger.info(f"✅ Найдено {count} записей")
        
        # Экспорт
        logger.info("📝 Экспорт в процессе...")
        logger.info("✅ ЭКСПОРТ ЗАВЕРШЁН")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ ОШИБКА: {e}", exc_info=True)
        logger.info("=" * 60)
        raise


# === ПРИМЕР 7: Логирование разных уровней ===

def demonstrate_log_levels():
    logger = get_logger("demo")
    
    logger.debug("📌 DEBUG: Детальная информация для разработчиков")
    logger.info("ℹ️  INFO: Основная информация о ходе работы")
    logger.warning("⚠️  WARNING: Что-то не совсем правильно")
    logger.error("❌ ERROR: Произошла ошибка")
    
    # Для критических ошибок:
    try:
        1 / 0
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)


# === ПРИМЕР 8: Логирование в классе ===

class ExportService:
    def __init__(self):
        self.logger = get_logger("ExportService")
        self.logger.info("✨ Сервис инициализирован")
    
    def export(self, format="xlsx"):
        self.logger.info(f"🚀 Начало экспорта в {format.upper()}")
        try:
            # Логика экспорта
            self.logger.debug(f"📝 Подготовка данных...")
            self.logger.debug(f"📝 Форматирование...")
            self.logger.info(f"✅ Экспорт в {format.upper()} завершён")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка при экспорте: {e}", exc_info=True)
            return False


# === ПРИМЕР 9: Логирование при удалении/архивировании ===

def cleanup_old_exports(days=7):
    logger = get_logger("cleanup")
    
    logger.info(f"🧹 Начало очистки файлов старше {days} дней")
    
    deleted_count = 0
    try:
        # Логика удаления
        deleted_count = 10
        logger.info(f"✅ Удалено {deleted_count} старых файлов")
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке: {e}", exc_info=True)
        raise


# === ПРИМЕР 10: Логирование конфигурации ===

def log_configuration(config):
    logger = get_logger("config")
    
    logger.info("⚙️  Конфигурация сервиса:")
    logger.info(f"   - Окружение: {config.get('environment')}")
    logger.info(f"   - БД: {config.get('database')}")
    logger.info(f"   - Логирование: {config.get('logging_level')}")
    logger.info(f"   - Порт: {config.get('port')}")


# === ИКОНКИ ДЛЯ ИСПОЛЬЗОВАНИЯ ===
"""
✨ - Инициализация
🚀 - Начало операции
🔍 - Поиск/фильтрация
📝 - Обработка/форматирование
📊 - Статистика/результаты
✅ - Успех
⚠️  - Предупреждение
❌ - Ошибка
📁 - Файлы/папки
⚙️  - Конфигурация
📌 - Отладка
ℹ️  - Информация
🧹 - Очистка
📖 - Документация
💾 - Сохранение
📞 - Соединение/API
"""


# === ТИПОВЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ ЛОГИРОВАНИЯ ===

"""
Успешный экспорт:
    🚀 НАЧАЛО ЭКСПОРТА
    🔍 Начало поиска
    ✅ Найдено N элементов
    📝 Форматирование
    ✅ ЭКСПОРТ УСПЕШЕН

Ошибка при экспорте:
    🚀 НАЧАЛО ЭКСПОРТА
    🔍 Начало поиска
    ✅ Найдено N элементов
    📝 Форматирование
    ❌ Ошибка при форматировании: [описание]

Пустой результат:
    🚀 НАЧАЛО ЭКСПОРТА
    🔍 Начало поиска
    ⚠️  По фильтрам ничего не найдено
    ✅ ЭКСПОРТ ЗАВЕРШЕН (пусто)
"""
