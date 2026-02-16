from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import AuditoriumResponse, AuditoriumCreate, AuditoriumUpdate, User
from api.auditoriums_api import get_auditoriums, create_auditorium, get_auditorium, update_auditorium, delete_auditorium
from dependencies import get_current_user
from fastapi_cache.decorator import cache
import json
from services.websocket_manager import manager

# Явный полный путь
router = APIRouter(prefix="/api/schedule/auditoriums", tags=["🏫 Аудитории"])

@router.get("/", response_model=List[AuditoriumResponse])
@cache(expire=60)
async def get_auditoriums_ep(name: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_auditoriums(db, name, limit, offset)

@router.post("/", response_model=AuditoriumResponse)
async def create_auditorium_ep(data: AuditoriumCreate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auditorium = await create_auditorium(data, db)
    await manager.broadcast(json.dumps({"type": "auditorium_created", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@router.get("/{auditorium_id}", response_model=AuditoriumResponse)
async def get_auditorium_ep(auditorium_id: int, db: Session = Depends(get_db)):
    return await get_auditorium(auditorium_id, db)

@router.put("/{auditorium_id}", response_model=AuditoriumResponse)
async def update_auditorium_ep(auditorium_id: int, data: AuditoriumUpdate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auditorium = await update_auditorium(auditorium_id, data, db)
    await manager.broadcast(json.dumps({"type": "auditorium_updated", "data": json.loads(AuditoriumResponse.from_orm(auditorium).model_dump_json())}))
    return auditorium

@router.delete("/{auditorium_id}")
async def delete_auditorium_ep(auditorium_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_auditorium(auditorium_id, db)
    await manager.broadcast(json.dumps({"type": "auditorium_deleted", "data": {"id": auditorium_id}}))
    return {"message": "Аудитория успешно удалена"}
