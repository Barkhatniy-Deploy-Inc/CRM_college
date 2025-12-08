from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, Course, Participant, ClassSlot, UserResponse, ParticipantStatus
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


async def get_course_participants(course_id: int, db: Session = Depends(get_db)) -> List[UserResponse]:
    """Получение участников курса"""
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Курс не найден")

    participants = db.query(User).join(Participant).join(ClassSlot).filter(ClassSlot.course_id == course_id).distinct().all()
    return participants


async def add_participant_to_course(course_id: int, user_id: int, db: Session = Depends(get_db)) -> Dict:
    """Добавление существующего участника к курсу с регистрацией на все занятия"""
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Курс не найден")
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    slots = db.query(ClassSlot).filter(ClassSlot.course_id == course_id).all()
    added_count = 0
    for slot in slots:
        participant = db.query(Participant).filter(Participant.class_slot_id == slot.id, Participant.user_id == user_id).first()
        if not participant:
            new_participant = Participant(class_slot_id=slot.id, user_id=user_id, status=ParticipantStatus.REGISTERED)
            db.add(new_participant)
            added_count += 1
    db.commit()

    return {
        "message": f"Участник добавлен к {added_count} занятиям курса.",
        "user_id": user_id,
        "slots_added": added_count
    }


async def remove_participant_from_course(course_id: int, user_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Удаление участника из всех занятий курса"""
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(status_code=404, detail="Курс не найден")

    slots = db.query(ClassSlot.id).filter(ClassSlot.course_id == course_id).subquery()
    deleted_count = db.query(Participant).filter(Participant.user_id == user_id, Participant.class_slot_id.in_(slots)).delete(synchronize_session=False)
    db.commit()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Участник не найден в этом курсе или уже был удален.")

    return {"message": f"Участник удален с {deleted_count} занятий курса."}
