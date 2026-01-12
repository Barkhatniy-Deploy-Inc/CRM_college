# 🧪 Автотесты расписания

## 📋 Обзор

Полный набор автотестов для сервиса экспорта расписания с поддержкой:
- ✅ Тестирование фильтрации по преподавателю
- ✅ Тестирование фильтрации по аудитории  
- ✅ Тестирование фильтрации по названию предмета
- ✅ Тестирование комбинированной фильтрации
- ✅ Тестирование экспорта в XLSX
- ✅ Тестирование экспорта в PDF
- ✅ Тестирование обработки дат
- ✅ Тестирование утилит

---

## 🚀 Запуск тестов

### Установка зависимостей
```bash
pip install pytest pytest-cov
```

### Запуск всех тестов
```bash
pytest tests/test_schedule_exporter.py -v
```

### Запуск конкретного класса тестов
```bash
# Тесты фильтрации по преподавателю
pytest tests/test_schedule_exporter.py::TestFilterByInstructor -v

# Тесты экспорта в XLSX
pytest tests/test_schedule_exporter.py::TestXLSXExport -v

# Тесты экспорта в PDF
pytest tests/test_schedule_exporter.py::TestPDFExport -v
```

### Запуск конкретного теста
```bash
pytest tests/test_schedule_exporter.py::TestFilterByInstructor::test_filter_by_instructor_ivanov -v
```

### Запуск с покрытием кода (coverage)
```bash
pytest tests/test_schedule_exporter.py --cov=services.schedule_exporter --cov=api.export_api --cov-report=html
```

---

## 📊 Структура тестов

### TestFilterByInstructor
Тесты фильтрации по преподавателю:
- `test_filter_by_instructor_ivanov` - получить занятия конкретного преподавателя
- `test_filter_by_instructor_petrov` - фильтрация для другого преподавателя
- `test_filter_by_instructor_partial_match` - частичное совпадение (case-insensitive)

### TestFilterByAuditorium
Тесты фильтрации по аудитории:
- `test_filter_by_auditorium_single` - фильтр по одной аудитории
- `test_filter_by_multiple_auditoriums` - фильтр по нескольким аудиториям

### TestFilterByTitle
Тесты фильтрации по названию предмета:
- `test_filter_by_title_exact` - точное совпадение
- `test_filter_by_title_partial` - частичное совпадение
- `test_filter_by_title_case_insensitive` - игнорирование регистра

### TestCombinedFilters
Тесты комбинированной фильтрации:
- `test_filter_by_instructor_and_title` - по преподавателю И названию
- `test_filter_by_instructor_and_auditorium` - по преподавателю И аудитории
- `test_filter_by_group_and_instructor` - по группе И преподавателю
- `test_filter_by_all_criteria` - фильтрация по всем критериям сразу

### TestXLSXExport
Тесты экспорта в XLSX:
- `test_export_xlsx_basic` - базовый экспорт
- `test_export_xlsx_with_filter` - экспорт с фильтром
- `test_export_xlsx_with_separate_courses` - экспорт с разделением по курсам
- `test_export_xlsx_with_stats` - экспорт с добавлением статистики
- `test_export_xlsx_empty_result` - обработка пустого результата

### TestPDFExport
Тесты экспорта в PDF:
- `test_export_pdf_basic` - базовый экспорт
- `test_export_pdf_single_group` - экспорт одной группы
- `test_export_pdf_with_filter` - экспорт с фильтром
- `test_export_pdf_empty_result` - обработка пустого результата

### TestDateRangeHandling
Тесты обработки дат:
- `test_date_range_single_date` - с конкретной датой
- `test_date_range_with_interval` - с диапазоном дат
- `test_date_range_default` - дефолтный диапазон (текущая неделя)

### TestCourseExtraction
Тесты извлечения номера курса:
- `test_extract_course_number` - корректное извлечение из названия группы

---

## 📝 Пример вывода

```
tests/test_schedule_exporter.py::TestFilterByInstructor::test_filter_by_instructor_ivanov PASSED
tests/test_schedule_exporter.py::TestFilterByInstructor::test_filter_by_instructor_petrov PASSED
tests/test_schedule_exporter.py::TestFilterByAuditorium::test_filter_by_auditorium_single PASSED
tests/test_schedule_exporter.py::TestXLSXExport::test_export_xlsx_basic PASSED
tests/test_schedule_exporter.py::TestPDFExport::test_export_pdf_basic PASSED

======================== 27 passed in 2.34s ========================
```

---

## 🔍 Логирование

### Включено логирование всех действий:

#### В консоль (INFO уровень):
```
INFO  | 📊 API запрос: экспорт XLSX
INFO  | 🚀 НАЧАЛО ЭКСПОРТА В XLSX
INFO  | 🔍 Начало поиска занятий с параметрами:
INFO  | ✅ Найдено 10 занятий
INFO  | 📊 Распределено по 3 группам
INFO  | ✅ ЭКСПОРТ В XLSX ЗАВЕРШЁН УСПЕШНО
```

#### В файл (DEBUG уровень + ошибки):
- `backend/schedule/logs/schedule_YYYY-MM-DD.log` - основной лог
- `backend/schedule/logs/schedule_errors.log` - только ошибки

### Структура логов:
```
2025-12-11 14:23:45 | schedule.main | INFO     | 🚀 Логирование инициализировано
2025-12-11 14:23:46 | schedule.export_api | INFO     | 📊 API запрос: экспорт XLSX
2025-12-11 14:23:46 | schedule.services.schedule_exporter | INFO     | 🚀 НАЧАЛО ЭКСПОРТА В XLSX
2025-12-11 14:23:46 | schedule.services.schedule_exporter | INFO     | 🔍 Начало поиска занятий с параметрами:
2025-12-11 14:23:46 | schedule.services.schedule_exporter | DEBUG    | 📅 Диапазон дат: 01.09.2025 - 07.09.2025
2025-12-11 14:23:46 | schedule.services.schedule_exporter | INFO     | ✅ Найдено 15 занятий
2025-12-11 14:23:47 | schedule.services.schedule_exporter | INFO     | ✅ ЭКСПОРТ В XLSX ЗАВЕРШЁН УСПЕШНО
```

---

## 🎯 Примеры использования в коде

### Получить логгер в своём модуле:
```python
from core.logging_config import get_logger

logger = get_logger("my_module")

logger.info("Обычная информация")
logger.debug("Отладочная информация")
logger.warning("Предупреждение")
logger.error("Ошибка", exc_info=True)
```

### Обернуть функцию логированием:
```python
def expensive_operation():
    logger.info("🚀 Начало операции")
    try:
        # код
        logger.info("✅ Операция завершена")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
        raise
```

---

## 💡 Рекомендации

1. **Регулярно запускайте тесты** перед коммитом
2. **Проверяйте логи** при возникновении проблем
3. **Добавляйте тесты** для новых фич
4. **Используйте fixtures** для переиспользования данных в тестах

---

## 🐛 Troubleshooting

### Тесты не находят БД модели
```bash
# Убедитесь что импортированы все модели
from database.models import *
```

### Тесты не находят fixtures
```bash
# Добавьте conftest.py в папку tests с fixtures
# или добавьте --override-ini addopts=-p в pytest.ini
```

### Лог файлы не создаются
```bash
# Убедитесь что папка logs существует
mkdir -p backend/schedule/logs
```
