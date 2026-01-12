#!/usr/bin/env python3
"""
Примеры использования парсера расписания
"""

from core.parser import parse_excel_schedule
from pathlib import Path
from datetime import datetime

# Пример 1: Базовое использование
print("=" * 80)
print("ПРИМЕР 1: Базовое использование парсера")
print("=" * 80)

schedule_path = Path('РАСПИСАНИЕ')
xlsx_files = sorted([f for f in schedule_path.glob('*.xlsx') if not f.name.startswith('~')])

if xlsx_files:
    file_path = str(xlsx_files[0])
    entries = parse_excel_schedule(file_path)
    
    print(f"\nВсего спарсено: {len(entries)} занятий")
    print(f"Примеры первых 5 занятий:\n")
    
    for i, entry in enumerate(entries[:5], 1):
        print(f"{i}. {entry['group_name']} | {entry['date']} {entry['time_slot']}")
        print(f"   Предмет: {entry['subject']}")
        print(f"   Преподаватель: {entry['teacher']}")
        print(f"   Аудитория: {entry['auditorium']}\n")


# Пример 2: Фильтрация по группе
print("\n" + "=" * 80)
print("ПРИМЕР 2: Занятия конкретной группы")
print("=" * 80)

target_group = "ПД-25/9-П"
group_entries = [e for e in entries if e['group_name'] == target_group]

print(f"\nГруппа '{target_group}': {len(group_entries)} занятий")
print(f"Первые 5 занятий:")

for i, entry in enumerate(group_entries[:5], 1):
    print(f"{i}. {entry['date']} {entry['time_slot']} - {entry['subject']} (аудитория {entry['auditorium']})")


# Пример 3: Расписание на конкретную дату
print("\n" + "=" * 80)
print("ПРИМЕР 3: Расписание на конкретную дату")
print("=" * 80)

target_date = "01.09.2025"
date_entries = [e for e in entries if e['date'] == target_date]

print(f"\nДата {target_date}: {len(date_entries)} занятий")
print(f"По группам:")

groups_on_date = {}
for entry in date_entries:
    group = entry['group_name']
    if group not in groups_on_date:
        groups_on_date[group] = []
    groups_on_date[group].append(entry)

for group in sorted(groups_on_date.keys()):
    print(f"\n{group}:")
    for entry in sorted(groups_on_date[group], key=lambda x: x['time_slot']):
        print(f"  {entry['time_slot']} - {entry['subject']} (преп. {entry['teacher']}, аудитория {entry['auditorium']})")


# Пример 4: Расписание преподавателя
print("\n" + "=" * 80)
print("ПРИМЕР 4: Расписание конкретного преподавателя")
print("=" * 80)

target_teacher = "Туманова И.С."
teacher_entries = [e for e in entries if e['teacher'] and target_teacher in e['teacher']]

print(f"\nПреподаватель '{target_teacher}': {len(teacher_entries)} занятий")
print(f"Первые 10 занятий:")

for i, entry in enumerate(sorted(teacher_entries, key=lambda x: (x['date'], x['time_slot']))[:10], 1):
    print(f"{i}. {entry['date']} {entry['time_slot']} - {entry['subject']} (группа {entry['group_name']}, аудитория {entry['auditorium']})")


# Пример 5: Групповое расписание
print("\n" + "=" * 80)
print("ПРИМЕР 5: Полное расписание группы по дням")
print("=" * 80)

target_group = "СД-25/9-П"
group_entries = [e for e in entries if e['group_name'] == target_group]

# Группируем по дням
schedule_by_day = {}
for entry in group_entries:
    day = entry['day_of_week']
    date = entry['date']
    if day not in schedule_by_day:
        schedule_by_day[day] = {}
    if date not in schedule_by_day[day]:
        schedule_by_day[day][date] = []
    schedule_by_day[day][date].append(entry)

day_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

print(f"\nГруппа '{target_group}':\n")
for day_num in sorted(schedule_by_day.keys()):
    print(f"{day_names[day_num - 1]}:")
    dates_on_day = schedule_by_day[day_num]
    for date in sorted(dates_on_day.keys()):
        print(f"  {date}:")
        for entry in sorted(dates_on_day[date], key=lambda x: x['time_slot']):
            print(f"    {entry['time_slot']} - {entry['subject']} (аудитория {entry['auditorium']})")


# Пример 6: Статистика
print("\n" + "=" * 80)
print("ПРИМЕР 6: Статистика расписания")
print("=" * 80)

# Количество занятий по группам
groups_stats = {}
for entry in entries:
    group = entry['group_name']
    groups_stats[group] = groups_stats.get(group, 0) + 1

print(f"\nВсего занятий: {len(entries)}")
print(f"Всего групп: {len(groups_stats)}")

# Среднее количество занятий на группу
avg_lessons = len(entries) / len(groups_stats)
print(f"Среднее занятий на группу: {avg_lessons:.1f}")

# Количество преподавателей (уникальные)
teachers = set()
for entry in entries:
    if entry['teacher']:
        teachers.add(entry['teacher'])

print(f"Преподавателей (уникальных): {len(teachers)}")

# Количество аудиторий (уникальные)
auditoriums = set()
for entry in entries:
    if entry['auditorium']:
        auditoriums.add(str(entry['auditorium']))

print(f"Аудиторий (уникальных): {len(auditoriums)}")

# Временные слоты
time_slots = set()
for entry in entries:
    time_slots.add(entry['time_slot'])

print(f"Временных слотов (уникальные): {len(sorted(time_slots))}")
print(f"Временные слоты: {', '.join(sorted(time_slots))}")

print("\n" + "=" * 80)
