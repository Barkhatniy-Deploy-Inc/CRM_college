from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from services.calendar_service import generate_calendar_for_user
from dependencies import get_current_user

router = APIRouter(prefix="/calendar", tags=["🗓️ Расписание"])

@router.get("/me.ics")
async def get_my_calendar(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    calendar_content = await generate_calendar_for_user(user.id, db)
    return Response(content=calendar_content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=my_schedule.ics"})
