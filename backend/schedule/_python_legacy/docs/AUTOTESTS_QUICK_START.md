# ✅ Автотесты и Логирование - Краткая инструкция

## 🧪 Запуск автотестов

### Установка pytest
```bash
pip install pytest
```

### Запуск всех тестов
```bash
cd backend/schedule
pytest tests/test_schedule_exporter.py -v
```

### Примеры команд
```bash
# Только фильтрация по преподавателю
pytest tests/test_schedule_exporter.py::TestFilterByInstructor -v

# Только тесты XLSX
pytest tests/test_schedule_exporter.py::TestXLSXExport -v

# С отчетом о покрытии кода
pytest tests/test_schedule_exporter.py --cov=services.schedule_exporter -v
```

---

## 📊 Логирование

Логирование **автоматически включено** при запуске сервера.

### Где видеть логи?

**В консоли:**
```
INFO  | 🚀 НАЧАЛО ЭКСПОРТА В XLSX
INFO  | 🔍 Начало поиска занятий с параметрами:
INFO  | ✅ Найдено 15 занятий
INFO  | ✅ ЭКСПОРТ В XLSX ЗАВЕРШЁН УСПЕШНО
```

**В файлах:**
- Основные логи: `backend/schedule/logs/schedule_YYYY-MM-DD.log`
- Ошибки: `backend/schedule/logs/schedule_errors.log`

### Уровни логирования

| Уровень | Где видно | Пример |
|---------|-----------|---------|
| `DEBUG` | Только файл | 📅 Диапазон дат: 01.09.2025 |
| `INFO` | Консоль + Файл | ✅ Найдено 15 занятий |
| `WARNING` | Консоль + Файл | ⚠️ По фильтрам не найдено |
| `ERROR` | Консоль + Файл + Файл ошибок | ❌ Критическая ошибка |

---

## 🔍 Что логируется?

**Запуск сервиса:**
```
✨ Инициализирован ScheduleExporter
📁 Логи сохраняются в: backend/schedule/logs
```

**Экспорт:**
```
🚀 НАЧАЛО ЭКСПОРТА В XLSX
🔍 Начало поиска занятий с параметрами:
   - Дата: 01.09.2025 - 07.09.2025
   - Преподаватель: Иванов
   - Предмет: Математика
✅ Найдено 5 занятий
📊 Распределено по 2 группам
📊 Добавляется лист со статистикой
✅ ЭКСПОРТ В XLSX ЗАВЕРШЁН УСПЕШНО
```

**API запросы:**
```
📊 API запрос: экспорт XLSX
   Параметры: date_from=01.09.2025, date_to=07.09.2025
   Фильтры: instructor=Иванов, title=Математика
✅ XLSX файл готов: расписание_01.09.2025_до_07.09.2025.xlsx
```

---

## 📂 Структура файлов

```
backend/schedule/
├── tests/
│   └── test_schedule_exporter.py    ← Все автотесты (27 тестов)
├── core/
│   └── logging_config.py             ← Конфиг логирования
├── services/
│   └── schedule_exporter.py          ← Логирование добавлено
├── api/
│   └── export_api.py                 ← Логирование добавлено
├── logs/                             ← Будут созданы автоматически
│   ├── schedule_YYYY-MM-DD.log
│   └── schedule_errors.log
├── pytest.ini                        ← Конфиг для тестов
├── TESTING_GUIDE.md                  ← Полная документация тестов
└── main.py                           ← Инициализирует логирование
```

---

## 💡 Примеры использования

### Вызвать API с логированием
```bash
# XLSX экспорт
curl "http://localhost:8000/api/schedule/export/xlsx?instructor=Иванов&separate_courses=true"

# PDF экспорт
curl "http://localhost:8000/api/schedule/export/pdf?title_search=математика&single_date=03.09.2025"
```

### В консоли увидите:
```
INFO  | 📊 API запрос: экспорт XLSX
INFO  | 🚀 НАЧАЛО ЭКСПОРТА В XLSX
INFO  | 🔍 Начало поиска занятий с параметрами:
INFO  | ✅ Найдено 5 занятий
INFO  | ✅ XLSX файл готов: расписание.xlsx
```

---

## 🚀 Быстрый старт

1. **Запустить сервер** (логирование автоматически включится):
```bash
cd backend/schedule
uvicorn main:app --reload
```

2. **Запустить тесты** (в другом терминале):
```bash
pytest tests/test_schedule_exporter.py -v
```

3. **Проверить логи** (в папке `logs/`):
```bash
tail -f backend/schedule/logs/schedule_*.log
```

4. **Тестировать API**:
```bash
curl "http://localhost:8000/api/schedule/export/xlsx"
```

---

## 🎯 Что было добавлено?

✅ **27 автотестов** для проверки всей функциональности
- 3 теста фильтрации по преподавателю
- 2 теста фильтрации по аудитории
- 3 теста фильтрации по названию
- 4 теста комбинированной фильтрации
- 5 тестов XLSX экспорта
- 4 теста PDF экспорта
- 3 теста обработки дат
- 1 тест извлечения курса

✅ **Полное логирование** с иконками и структурой
- На консоль (INFO+)
- В файл (DEBUG+)
- В отдельный файл ошибок (ERROR+)

✅ **Документация**
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - полная инструкция
