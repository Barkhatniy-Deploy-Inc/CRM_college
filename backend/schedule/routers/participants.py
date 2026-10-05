from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import UserResponse, AddParticipantRequest, User
from api.participants_api import get_group_participants, add_participant_to_group, remove_participant_from_group
from dependencies import get_current_user
import json
from services.websocket_manager import manager

router = APIRouter(prefix="/api/schedule/participants", tags=["👥 Участники"])

@router.get("/{group_id}/participants", response_model=List[UserResponse])
async def get_group_participants_ep(group_id: int, db: Session = Depends(get_db)):
    return await get_group_participants(group_id, db)

@router.post("/{group_id}/participants")
async def add_group_participant_ep(group_id: int, data: AddParticipantRequest, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = await add_participant_to_group(group_id, data.user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_added", "data": {"group_id": group_id, "user_id": data.user_id}}))
    return result

@router.delete("/{group_id}/participants/{user_id}")
async def remove_group_participant_ep(group_id: int, user_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await remove_participant_from_group(group_id, user_id, db)
    await manager.broadcast(json.dumps({"type": "participant_removed", "data": {"group_id": group_id, "user_id": user_id}}))
    return {"message": "Участник успешно удален из группы"}
