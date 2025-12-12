# Анализ таблиц tech_card_db

## Проблемы со структурой схемы

Заявленная схема для базы tech_card_db содержит следующие таблицы:

1. `lesson_type`
   - primary_key
   - lesson_type
   - name_teacher

2. `primary_key` (таблица с названием первичного ключа?)
   - full_name
   - lesson_topic

3. `lesson`
   - topic
   - group_name

4. `primary_key` (еще одна таблица с таким названием?)
   - curator_id
   - curator_group

5. `group_name` (таблица с названием поля?)
   - learning_outcomes

6. `primary_key` (третья таблица с таким названием?)
   - lesson
   - skill
   - know

7. `pk_and_ok`
   - primary_key
   - lesson
   - prof_comp
   - general_comp

8. `skills_and_knowledge`
   - primary_key
   - lesson
   - skill
   - knowledge

9. `lesson` (еще одна таблица с таким названием?)
   - primary_key
   - name_lesson
   - Teacher
   - Group_name
   - type_lesson

## Проблемы с заявленной схемой:

1. **Нарушение принципов проектирования БД:**
   - Несколько таблиц имеют одинаковые названия (`primary_key`, `lesson`)
   - Названия таблиц и полей не соответствуют стандартам (использование `primary_key` как имени таблицы)
   - Отсутствует четкая иерархия и связи между таблицами

2. **Непонятная семантика:**
   - Назначение многих таблиц неясно из названий
   - Некоторые поля дублируются в разных таблицах
   - Непонятно, как таблицы связаны между собой

## Рекомендуемая структура:

На основе файла `/workspace/backend/techcard/database/models_techcard.py` предлагается следующая нормализованная структура:

```sql
-- Таблица для хранения основных данных технологической карты
CREATE TABLE tech_cards (
    id SERIAL PRIMARY KEY,
    group_id INTEGER,                    -- ID группы
    lesson_id INTEGER,                   -- ID предмета
    teacher_id INTEGER,                  -- ID преподавателя
    lesson_type_id INTEGER,              -- ID типа урока
    tema TEXT NOT NULL,                  -- Тема занятия
    nomer_zanyatiya VARCHAR(50),         -- Номер занятия по теме
    ped_tech TEXT,                       -- Используемые пед. технологии
    cel_zanyatiya TEXT,                  -- Цель занятия
    zadachi_obuch TEXT,                  -- Обучающие задачи
    zadachi_razv TEXT,                   -- Развивающие задачи
    zadachi_vosp TEXT,                   -- Воспитательные задачи
    prognoz_result TEXT,                 -- Знания, умения, компетенции
    oborudovanie TEXT,                   -- Оборудование
    istochniki TEXT                      -- Список использованных источников
);

-- Таблица для этапов урока
CREATE TABLE tech_card_stages (
    id SERIAL PRIMARY KEY,
    tech_card_id INTEGER NOT NULL REFERENCES tech_cards(id) ON DELETE CASCADE,
    nomer_etapa INTEGER NOT NULL,        -- Номер этапа (1, 2, 3, 4...)
    nazvanie_etapa VARCHAR(255) NOT NULL, -- Название этапа
    cel_etapa TEXT,                      -- Цель этапа
    dlitelnost VARCHAR(50),              -- Длительность этапа
    deyatelnost_prepod TEXT,             -- Деятельность преподавателя
    deyatelnost_obuch TEXT,              -- Деятельность обучающихся
    formiruemye_kompetencii TEXT         -- Формируемые компетенции
);
```

## Преимущества предложенной структуры:

1. **Четкая иерархия:** Основная карта и связанные этапы
2. **Нормализация:** Устранение дублирования данных
3. **Гибкость:** Возможность добавления новых этапов без изменения структуры
4. **Целостность данных:** Явные внешние ключи обеспечивают ссылочную целостность
5. **Логическая организация:** Каждая таблица имеет понятное назначение

## Рекомендации:

1. Использовать предложенную структуру как эталонную
2. Если заявленная схема была получена из реальной БД, то она требует рефакторинга
3. Обновить документацию и код в соответствии с нормализованной структурой