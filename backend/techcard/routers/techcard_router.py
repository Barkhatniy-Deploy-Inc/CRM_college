# backend/routers/techcard_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import httpx
import os
from database.models_techcard import TechCard, TechCardStage
from database.schemas import TechCardUpdate, TechCardResponse
from database.dependencies import get_techcard_db
from auth import get_current_user
from utils.docx_generator import generate_techcard_docx

# ✅ СНАЧАЛА создаём роутер (это ОБЯЗАТЕЛЬНО должно быть ДО декораторов!)
router = APIRouter(
    prefix="/api/techcards",
    tags=["Технологические карты"]
)

SCHEDULE_SERVICE_URL = os.getenv("SCHEDULE_SERVICE_URL", "http://schedule:8000").rstrip("/")
SCHEDULE_API_URL = f"{SCHEDULE_SERVICE_URL}/api/schedule"


async def get_lesson_data(lesson_id: int):
    """Получает данные о занятии из сервиса расписания."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SCHEDULE_API_URL}/{lesson_id}")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Сервис расписания недоступен: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка от сервиса расписания: {e.response.text}")


def _apply_techcard_data(db_card: TechCard, data: TechCardUpdate) -> None:
    """Переносит поля запроса в ORM-модель техкарты."""
    db_card.group_id = data.group_id
    db_card.lesson_id = data.lesson_id
    db_card.teacher_id = data.teacher_id
    db_card.lesson_type_id = data.lesson_type_id
    db_card.tema = data.tema
    db_card.nomer_zanyatiya = data.nomer_zanyatiya
    db_card.ped_tech = data.ped_tech
    db_card.cel_zanyatiya = data.cel_zanyatiya
    db_card.zadachi_obuch = data.zadachi_obuch
    db_card.zadachi_razv = data.zadachi_razv
    db_card.zadachi_vosp = data.zadachi_vosp
    db_card.prognoz_result = data.prognoz_result
    db_card.oborudovanie = data.oborudovanie
    db_card.istochniki = data.istochniki


def _replace_stages(db: Session, techcard_id: int, stages) -> None:
    """Полностью заменяет этапы урока для техкарты."""
    db.query(TechCardStage).filter(
        TechCardStage.tech_card_id == techcard_id
    ).delete(synchronize_session=False)
    db.flush()

    for stage_data in stages:
        db.add(TechCardStage(
            tech_card_id=techcard_id,
            nomer_etapa=stage_data.nomer_etapa,
            nazvanie_etapa=stage_data.nazvanie_etapa,
            cel_etapa=stage_data.cel_etapa,
            dlitelnost=stage_data.dlitelnost,
            deyatelnost_prepod=stage_data.deyatelnost_prepod,
            deyatelnost_obuch=stage_data.deyatelnost_obuch,
            formiruemye_kompetencii=stage_data.formiruemye_kompetencii
        ))


@router.get("", response_model=List[TechCardResponse])
def list_techcards(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_techcard_db)
):
    """Список технологических карт с пагинацией."""
    return db.query(TechCard).order_by(TechCard.id.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=TechCardResponse, status_code=201)
async def create_techcard(
    techcard_data: TechCardUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_techcard_db)
):
    """Создание технологической карты. ID назначает сервер."""
    db_card = TechCard()
    _apply_techcard_data(db_card, techcard_data)

    # Автозаполнение из расписания, если указан lesson_id
    if techcard_data.lesson_id:
        lesson_data = await get_lesson_data(techcard_data.lesson_id)
        db_card.tema = lesson_data.get("title", db_card.tema)
        db_card.teacher_id = lesson_data.get("instructor_id", db_card.teacher_id)

    db.add(db_card)
    db.flush()
    _replace_stages(db, db_card.id, techcard_data.stages)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.put("/{techcard_id}", response_model=TechCardResponse)
async def update_techcard(
        techcard_id: int,
        techcard_data: TechCardUpdate,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_techcard_db)
):
    """
    Обновляет существующую технологическую карту или создаёт новую.
    Если указан lesson_id, данные из расписания будут использованы для автозаполнения.
    """
    try:
        db_card = db.query(TechCard).filter(TechCard.id == techcard_id).first()

        if not db_card:
            db_card = TechCard(id=techcard_id)
            db.add(db_card)
            db.flush()

        _apply_techcard_data(db_card, techcard_data)

        # Автозаполнение из расписания, если указан lesson_id
        if techcard_data.lesson_id:
            lesson_data = await get_lesson_data(techcard_data.lesson_id)
            db_card.tema = lesson_data.get("title", db_card.tema)
            db_card.teacher_id = lesson_data.get("instructor_id", db_card.teacher_id)

        db.flush()
        _replace_stages(db, techcard_id, techcard_data.stages)
        db.commit()
        db.refresh(db_card)

        return db_card

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")


@router.get("/download/{techcard_id}")
async def download_techcard(
        techcard_id: int,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_techcard_db)
):
    """
    Генерирует .docx файл из данных технологической карты и отдаёт его для скачивания.
    """
    db_card = db.query(TechCard).filter(TechCard.id == techcard_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Технологическая карта не найдена")

    # Преобразуем модель в словарь для генератора
    card_data = {
        "tema": db_card.tema,
        "nomer_zanyatiya": db_card.nomer_zanyatiya,
        "cel_zanyatiya": db_card.cel_zanyatiya,
        "zadachi_obuch": db_card.zadachi_obuch,
        "zadachi_razv": db_card.zadachi_razv,
        "zadachi_vosp": db_card.zadachi_vosp,
        "ped_tech": db_card.ped_tech,
        "prognoz_result": db_card.prognoz_result,
        "oborudovanie": db_card.oborudovanie,
        "istochniki": db_card.istochniki,
        "stages": [
            {
                "nomer_etapa": s.nomer_etapa,
                "nazvanie_etapa": s.nazvanie_etapa,
                "dlitelnost": s.dlitelnost,
                "deyatelnost_prepod": s.deyatelnost_prepod,
                "deyatelnost_obuch": s.deyatelnost_obuch
            } for s in db_card.stages
        ]
    }

    try:
        file_stream = generate_techcard_docx(card_data)
        filename = f"Techcard_{techcard_id}.docx"

        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации файла: {str(e)}")


@router.get("/{techcard_id}", response_model=TechCardResponse)
def get_techcard(
    techcard_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_techcard_db)
):
    """
    Получает технологическую карту по ID.
    """
    db_card = db.query(TechCard).filter(TechCard.id == techcard_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Технологическая карта не найдена")
    return db_card
