# backend/routers/techcard_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import httpx
from database.models_techcard import TechCard, TechCardStage
from database.schemas import TechCardUpdate, TechCardResponse
from database.dependencies import get_techcard_db
from utils.docx_generator import generate_techcard_docx

# ✅ СНАЧАЛА создаём роутер (это ОБЯЗАТЕЛЬНО должно быть ДО декораторов!)
router = APIRouter(
    prefix="/api/techcards",
    tags=["Технологические карты"]
)

SCHEDULE_API_URL = "http://schedule:8000/api/schedule"


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


@router.put("/{techcard_id}", response_model=TechCardResponse)
async def update_techcard(
        techcard_id: int,
        techcard_data: TechCardUpdate,
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

        # Если есть lesson_id, получаем данные из сервиса расписания
        if techcard_data.lesson_id:
            lesson_data = await get_lesson_data(techcard_data.lesson_id)
            db_card.tema = lesson_data.get("title", db_card.tema)
            db_card.teacher_id = lesson_data.get("instructor", db_card.teacher_id)
            # Другие поля можно будет добавить по аналогии

        # Обновляем остальные данные из запроса
        db_card.group_id = techcard_data.group_id
        db_card.lesson_id = techcard_data.lesson_id
        db_card.lesson_type_id = techcard_data.lesson_type_id
        db_card.nomer_zanyatiya = techcard_data.nomer_zanyatiya
        db_card.ped_tech = techcard_data.ped_tech
        db_card.cel_zanyatiya = techcard_data.cel_zanyatiya
        db_card.zadachi_obuch = techcard_data.zadachi_obuch
        db_card.zadachi_razv = techcard_data.zadachi_razv
        db_card.zadachi_vosp = techcard_data.zadachi_vosp
        db_card.prognoz_result = techcard_data.prognoz_result
        db_card.oborudovanie = techcard_data.oborudovanie
        db_card.istochniki = techcard_data.istochniki

        db.flush()

        db.query(TechCardStage).filter(
            TechCardStage.tech_card_id == techcard_id
        ).delete(synchronize_session=False)

        db.flush()

        for stage_data in techcard_data.stages:
            stage = TechCardStage(
                tech_card_id=techcard_id,
                nomer_etapa=stage_data.nomer_etapa,
                nazvanie_etapa=stage_data.nazvanie_etapa,
                cel_etapa=stage_data.cel_etapa,
                dlitelnost=stage_data.dlitelnost,
                deyatelnost_prepod=stage_data.deyatelnost_prepod,
                deyatelnost_obuch=stage_data.deyatelnost_obuch,
                formiruemye_kompetencii=stage_data.formiruemye_kompetencii
            )
            db.add(stage)

        db.commit()
        db.refresh(db_card)

        return db_card

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")


@router.get("/download/{techcard_id}")
async def download_techcard(
        techcard_id: int,
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
def get_techcard(techcard_id: int, db: Session = Depends(get_techcard_db)):
    """
    Получает технологическую карту по ID.
    """
    db_card = db.query(TechCard).filter(TechCard.id == techcard_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Технологическая карта не найдена")
    return db_card
