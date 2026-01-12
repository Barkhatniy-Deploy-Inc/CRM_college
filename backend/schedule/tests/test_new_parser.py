#!/usr/bin/env python3
"""Тест нового парсера расписания"""

import sys
import logging
from pathlib import Path
from core.parser import parse_excel_schedule

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Берем первый файл расписания
schedule_path = Path('РАСПИСАНИЕ')
xlsx_files = sorted([f for f in schedule_path.glob('*.xlsx') if not f.name.startswith('~')])

if xlsx_files:
    file_path = str(xlsx_files[0])
    print(f'Тестирую парсер на файле: {xlsx_files[0].name}')
    print('=' * 120)
    
    entries = parse_excel_schedule(file_path)
    
    print(f'\nВсего спарсено занятий: {len(entries)}')
    print()
    
    # Показываем первые 30 занятий
    print('Первые 30 занятий:')
    print('-' * 120)
    for i, entry in enumerate(entries[:30], 1):
        group = entry['group_name'][:12]
        date = entry['date']
        time = entry['time_slot']
        subject = entry['subject'][:40]
        teacher = entry['teacher'][:18] if entry['teacher'] else 'N/A'
        room = entry['auditorium'] or 'N/A'
        print(f'{i:2}. {group:12} | {date:10} | {time:12} | {subject:40} | {teacher:18} | {room}')
    
    # Статистика по группам
    print()
    print('=' * 120)
    print('СТАТИСТИКА ПО ГРУППАМ:')
    groups_stats = {}
    for entry in entries:
        group = entry['group_name']
        groups_stats[group] = groups_stats.get(group, 0) + 1
    
    for group, count in sorted(groups_stats.items()):
        print(f'  {group:15}: {count:3} занятий')
    
    print()
    print('ПРИМЕР ОДНОГО ЗАНЯТИЯ (с полной информацией):')
    print('=' * 120)
    if entries:
        entry = entries[0]
        for key, value in entry.items():
            print(f'  {key:20}: {value}')
else:
    print("Не найдены файлы расписания")
