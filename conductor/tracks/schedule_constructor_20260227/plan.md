# Implementation Plan: Продвинутый конструктор расписания и Редактор связей [checkpoint: eae2836]

## Phase 1: База данных и Бэкенд (Связи)
- [x] Task: Создание моделей для связей (Teacher-Subject, Subject-Auditorium) in `backend/schedule/database/models.py` [b033b79]
- [x] Task: Создание API эндпоинтов для управления связями в `backend/schedule/api/` [a838217]
- [x] Task: Обновление модели `Schedule` для поддержки локальных замен преподавателя/кабинета [9b0dfd3]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Backend Infrastructure' (Protocol in workflow.md)

## Phase 2: Интерфейс Редактора связей
- [ ] Task: Создание страницы "Редактор связей" во фронтенде
- [ ] Task: Интеграция с API бэкенда (Pinia store)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Relations Editor UI' (Protocol in workflow.md)

## Phase 3: Визуальный Конструктор (Drag & Drop)
- [ ] Task: Реализация базового режима конструктора (замена чекбокса на кнопку)
- [ ] Task: Разработка боковой панели с парами группы и фильтрацией
- [ ] Task: Реализация механики Drag & Drop с привязкой к сетке и опцией "Свободное перемещение"
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Visual Constructor Core' (Protocol in workflow.md)

## Phase 4: Интеллектуальный выбор и Замены
- [ ] Task: Реализация выпадающего списка выбора кабинета с автоподстановкой и ручным вводом
- [ ] Task: Реализация функционала локальной смены преподавателя в сетке
- [ ] Task: Визуальная индикация конфликтов (подсветка красным)
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Advanced UI Logic' (Protocol in workflow.md)

## Phase 5: Экспорт и Финализация
- [ ] Task: Реализация экспорта в XLSX и PDF (обновление сервисов генерации)
- [ ] Task: Финальное тестирование и полировка
- [ ] Task: Conductor - User Manual Verification 'Final Polish' (Protocol in workflow.md)
