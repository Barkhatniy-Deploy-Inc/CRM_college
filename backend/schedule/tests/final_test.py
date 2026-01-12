#!/usr/bin/env python3
"""Финальный тест парсера"""

from core.parser import parse_excel_schedule
from pathlib import Path

schedule_path = Path('РАСПИСАНИЕ')
xlsx_files = sorted([f for f in schedule_path.glob('*.xlsx') if not f.name.startswith('~')])

print('=' * 80)
print('ФИНАЛЬНЫЙ ТЕСТ ПАРСЕРА')
print('=' * 80)

results = []
for idx, xlsx_file in enumerate(xlsx_files[:3], 1):
    file_path = str(xlsx_file)
    try:
        entries = parse_excel_schedule(file_path)
        groups = set(e['group_name'] for e in entries)
        results.append({
            'file': xlsx_file.name,
            'entries': len(entries),
            'groups': len(groups),
            'status': 'OK'
        })
        print(f'{idx}. {xlsx_file.name[:30]:30} -> {len(entries):3} занятий, {len(groups):2} групп OK')
    except Exception as e:
        results.append({
            'file': xlsx_file.name,
            'status': f'ERROR: {e}'
        })
        print(f'{idx}. {xlsx_file.name[:30]:30} -> ERROR')

print()
print(f'Всего файлов протестировано: {len(results)} из {len(xlsx_files)}')
all_ok = all(r['status'] == 'OK' for r in results)
if all_ok:
    print('Результат: УСПЕХ')
else:
    print('Результат: ОШИБКА')
