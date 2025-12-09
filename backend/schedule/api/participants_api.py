from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import User, Group, Participant, ClassSlot, UserResponse, ParticipantStatus
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


async def get_group_participants(group_id: int, db: Session) -> List[UserResponse]:
    """Получение участников группы"""
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=404, detail="Группа не найдена")

    participants = db.query(User).join(Participant).join(ClassSlot).filter(ClassSlot.group_id == group_id).distinct().all()
    return participants


async def add_participant_to_group(group_id: int, user_id: int, db: Session) -> Dict:
    """Добавление существующего участника к группе с регистрацией на все занятия"""
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    slots = db.query(ClassSlot).filter(ClassSlot.group_id == group_id).all()
    added_count = 0
    for slot in slots:
        participant = db.query(Participant).filter(Participant.class_slot_id == slot.id, Participant.user_id == user_id).first()
        if not participant:
            new_participant = Participant(class_slot_id=slot.id, user_id=user_id, status=ParticipantStatus.REGISTERED)
            db.add(new_participant)
            added_count += 1
    db.commit()

    return {
        "message": f"Участник добавлен к {added_count} занятиям группы.",
        "user_id": user_id,
        "slots_added": added_count
    }


async def remove_participant_from_group(group_id: int, user_id: int, db: Session) -> Dict[str, str]:
    """Удаление участника из всех занятий группы"""
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=404, detail="Группа не найдена")

    slots = db.query(ClassSlot.id).filter(ClassSlot.group_id == group_id).subquery()
    deleted_count = db.query(Participant).filter(Participant.user_id == user_id, Participant.class_slot_id.in_(slots)).delete(synchronize_session=False)
    db.commit()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Участник не найден в этой группе или уже был удален.")

    return {"message": f"Участник удален с {deleted_count} занятий группы."}
