from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import GroupResponse, GroupCreate, GroupUpdate, User
from api.groups_api import get_groups, create_group, get_group, update_group, delete_group
from dependencies import get_current_user
from fastapi_cache.decorator import cache
import json
from services.websocket_manager import manager

# Явный полный путь
router = APIRouter(prefix="/api/schedule/groups", tags=["👥 Группы"])

@router.get("/", response_model=List[GroupResponse])
@cache(expire=60)
async def get_groups_ep(name: Optional[str] = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return await get_groups(db, name, limit, offset)

@router.post("/", response_model=GroupResponse)
async def create_group_ep(data: GroupCreate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = await create_group(data, db)
    await manager.broadcast(json.dumps({"type": "group_created", "data": json.loads(GroupResponse.from_orm(group).model_dump_json())}))
    return group

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group_ep(group_id: int, db: Session = Depends(get_db)):
    return await get_group(group_id, db)

@router.put("/{group_id}", response_model=GroupResponse)
async def update_group_ep(group_id: int, data: GroupUpdate, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = await update_group(group_id, data, db)
    await manager.broadcast(json.dumps({"type": "group_updated", "data": json.loads(GroupResponse.from_orm(group).model_dump_json())}))
    return group

@router.delete("/{group_id}")
async def delete_group_ep(group_id: int, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_group(group_id, db)
    await manager.broadcast(json.dumps({"type": "group_deleted", "data": {"id": group_id}}))
    return {"message": "Группа успешно удалена"}
