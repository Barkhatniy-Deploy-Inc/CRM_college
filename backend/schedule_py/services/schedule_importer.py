"""
Сервис для сохранения данных расписания в базу данных.
Преобразует результаты парсера в модели БД и сохраняет их.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models import Group, Auditorium, ClassSlot, SlotStatus
from core.parser import parse_excel_schedule

logger = logging.getLogger(__name__)


class ScheduleImporter:
    """Сервис для импорта расписания из Excel файлов в БД"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def import_schedule(self, file_path: str) -> Dict:
        """
        Импортирует расписание из Excel файла в БД.
        
        Возвращает словарь с статистикой:
        {
            'status': 'success' | 'error',
            'message': str,
            'groups_created': int,
            'groups_updated': int,
            'auditoriums_created': int,
            'slots_created': int,
            'slots_updated': int,
            'errors': List[str]
        }
        """
        stats = {
            'status': 'success',
            'message': '',
            'groups_created': 0,
            'groups_updated': 0,
            'auditoriums_created': 0,
            'slots_created': 0,
            'slots_updated': 0,
            'errors': []
        }
        
        try:
            # Парсим Excel файл
            logger.info(f"Начало импорта расписания из {file_path}")
            entries = parse_excel_schedule(file_path)
            
            if not entries:
                stats['status'] = 'error'
                stats['message'] = 'Файл расписания пуст или не содержит данных'
                logger.error(stats['message'])
                return stats
            
            logger.info(f"Спарсено {len(entries)} записей")
            
            # Обрабатываем каждую запись
            for entry in entries:
                try:
                    # Сохраняем группу
                    group = self._get_or_create_group(entry['group_name'])
                    if group and group.id is None:
                        stats['groups_created'] += 1
                    else:
                        stats['groups_updated'] += 1
                    
                    # Сохраняем аудиторию
                    auditorium = None
                    if entry['auditorium']:
                        auditorium = self._get_or_create_auditorium(entry['auditorium'])
                        if auditorium and auditorium.id is None:
                            stats['auditoriums_created'] += 1
                    
                    # Преобразуем дату и время
                    slot_date = self._parse_date(entry['date'])
                    start_time, end_time = self._parse_time_slot(entry['time_slot'], slot_date)
                    
                    if slot_date is None or start_time is None or end_time is None:
                        error_msg = f"Не удалось парсить дату/время для {entry['group_name']}: {entry['date']} {entry['time_slot']}"
                        stats['errors'].append(error_msg)
                        logger.warning(error_msg)
                        continue
                    
                    # Создаём или обновляем слот
                    slot_created = self._create_or_update_class_slot(
                        group=group,
                        auditorium=auditorium,
                        entry=entry,
                        start_time=start_time,
                        end_time=end_time
                    )
                    
                    if slot_created:
                        stats['slots_created'] += 1
                    else:
                        stats['slots_updated'] += 1
                        
                except Exception as e:
                    error_msg = f"Ошибка при обработке записи {entry.get('group_name', 'N/A')}: {str(e)}"
                    stats['errors'].append(error_msg)
                    logger.error(error_msg, exc_info=True)
                    continue
            
            # Коммитим все изменения
            self.db.commit()
            
            stats['message'] = (
                f"Импорт завершён успешно. "
                f"Групп создано: {stats['groups_created']}, "
                f"Слотов создано: {stats['slots_created']}, "
                f"Ошибок: {len(stats['errors'])}"
            )
            logger.info(stats['message'])
            
        except Exception as e:
            stats['status'] = 'error'
            stats['message'] = f"Ошибка при импорте расписания: {str(e)}"
            stats['errors'].append(stats['message'])
            logger.error(stats['message'], exc_info=True)
            self.db.rollback()
        
        return stats
    
    def _get_or_create_group(self, group_name: str) -> Group:
        """Получает или создаёт группу по названию"""
        try:
            group = self.db.query(Group).filter(Group.name == group_name).first()
            
            if not group:
                group = Group(name=group_name, description=f"Группа {group_name}")
                self.db.add(group)
                self.db.flush()  # Получаем ID
                logger.debug(f"Создана новая группа: {group_name}")
            
            return group
            
        except Exception as e:
            logger.error(f"Ошибка при работе с группой {group_name}: {e}")
            raise
    
    def _get_or_create_auditorium(self, auditorium_name: str) -> Optional[Auditorium]:
        """Получает или создаёт аудиторию по названию"""
        try:
            auditorium = self.db.query(Auditorium).filter(
                Auditorium.name == auditorium_name
            ).first()
            
            if not auditorium:
                auditorium = Auditorium(
                    name=auditorium_name,
                    capacity=None,
                    description=f"Аудитория {auditorium_name}"
                )
                self.db.add(auditorium)
                self.db.flush()
                logger.debug(f"Создана новая аудитория: {auditorium_name}")
            
            return auditorium
            
        except Exception as e:
            logger.error(f"Ошибка при работе с аудиторией {auditorium_name}: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Преобразует строку даты 'ДД.MM.ГГГГ' в datetime"""
        try:
            # Формат: "01.09.2025"
            return datetime.strptime(date_str, "%d.%m.%Y")
        except (ValueError, TypeError) as e:
            logger.error(f"Ошибка при парсинге даты '{date_str}': {e}")
            return None
    
    def _parse_time_slot(self, time_slot: str, base_date: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Преобразует строку времени 'ЧЧ:ММ-ЧЧ:ММ' в start_time и end_time
        base_date используется для установки даты
        """
        try:
            # Формат: "09:40-10:40"
            parts = time_slot.split('-')
            if len(parts) != 2:
                raise ValueError(f"Неверный формат времени: {time_slot}")
            
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            start_time_obj = datetime.strptime(start_str, "%H:%M").time()
            end_time_obj = datetime.strptime(end_str, "%H:%M").time()
            
            # Объединяем дату и время
            start_time = datetime.combine(base_date.date(), start_time_obj)
            end_time = datetime.combine(base_date.date(), end_time_obj)
            
            return start_time, end_time
            
        except (ValueError, TypeError) as e:
            logger.error(f"Ошибка при парсинге времени '{time_slot}': {e}")
            return None, None
    
    def _create_or_update_class_slot(
        self,
        group: Group,
        auditorium: Optional[Auditorium],
        entry: Dict,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """
        Создаёт или обновляет слот занятия.
        Возвращает True если был создан новый, False если обновлён
        """
        try:
            # Проверяем, существует ли уже такой слот
            existing_slot = self.db.query(ClassSlot).filter(
                ClassSlot.group_id == group.id,
                ClassSlot.start_time == start_time,
                ClassSlot.end_time == end_time,
                ClassSlot.title == entry['subject']
            ).first()
            
            if existing_slot:
                # Обновляем существующий слот
                existing_slot.instructor = entry['teacher']
                if auditorium:
                    existing_slot.auditorium_id = auditorium.id
                logger.debug(f"Обновлён слот: {entry['subject']} для группы {group.name}")
                return False
            else:
                # Создаём новый слот
                new_slot = ClassSlot(
                    title=entry['subject'],
                    start_time=start_time,
                    end_time=end_time,
                    instructor=entry['teacher'],
                    status=SlotStatus.SCHEDULED,
                    group_id=group.id,
                    auditorium_id=auditorium.id if auditorium else None
                )
                self.db.add(new_slot)
                logger.debug(f"Создан новый слот: {entry['subject']} для группы {group.name}")
                return True
                
        except IntegrityError as e:
            logger.warning(f"Ошибка целостности при создании слота: {e}")
            self.db.rollback()
            return False
        except Exception as e:
            logger.error(f"Ошибка при создании/обновлении слота: {e}")
            raise
    
    def clear_schedule(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        """
        Удаляет старое расписание (опционально в диапазоне дат).
        Используется перед загрузкой нового расписания.
        """
        try:
            if date_from and date_to:
                # Удаляем слоты в указанном диапазоне дат
                self.db.query(ClassSlot).filter(
                    ClassSlot.start_time >= date_from,
                    ClassSlot.start_time <= date_to
                ).delete()
                logger.info(f"Удалено расписание с {date_from} по {date_to}")
            else:
                # Удаляем только будущие слоты
                now = datetime.now()
                self.db.query(ClassSlot).filter(
                    ClassSlot.start_time >= now
                ).delete()
                logger.info("Удалено расписание на будущие даты")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Ошибка при удалении расписания: {e}")
            self.db.rollback()
            raise
