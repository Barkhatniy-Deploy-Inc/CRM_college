from pydantic import BaseModel
from typing import Optional, List


# ========== СХЕМЫ ДЛЯ СПРАВОЧНИКОВ (чтение из databaseforbros.db) ==========

# Схема для группы
class GroupResponse(BaseModel):
    primary_key: int
    curator_group: Optional[str]
    group_name: Optional[str]

    class Config:
        from_attributes = True


# Схема для предмета
class LessonResponse(BaseModel):
    primary_key: int
    name_lesson: str

    class Config:
        from_attributes = True


# Схема для типа урока
class LessonTypeResponse(BaseModel):
    primary_key: int
    lesson_type: str

    class Config:
        from_attributes = True


# Схема для преподавателя
class TeacherResponse(BaseModel):
    primary_key: int
    full_name: str

    class Config:
        from_attributes = True


# Схема для знаний и умений
class SkillsKnowledgeResponse(BaseModel):
    primary_key: int
    skill: Optional[str]
    knowledge: Optional[str]

    class Config:
        from_attributes = True


# ========== СХЕМЫ ДЛЯ ЭТАПОВ УРОКА ==========

# Схема для этапа урока (используется внутри техкарты)
class TechCardStageData(BaseModel):
    nomer_etapa: int  # Номер этапа
    nazvanie_etapa: str  # Название этапа
    cel_etapa: Optional[str] = None  # Цель этапа
    dlitelnost: Optional[str] = None  # Длительность
    deyatelnost_prepod: Optional[str] = None  # Деятельность преподавателя
    deyatelnost_obuch: Optional[str] = None  # Деятельность обучающихся
    formiruemye_kompetencii: Optional[str] = None  # Формируемые компетенции


# Схема для ответа с этапом урока (включает id из БД)
class TechCardStageResponse(TechCardStageData):
    id: int
    tech_card_id: int

    class Config:
        from_attributes = True


# ========== СХЕМЫ ДЛЯ ТЕХНОЛОГИЧЕСКОЙ КАРТЫ ==========

# Схема для сохранения/обновления техкарты
class TechCardUpdate(BaseModel):
    # ID из справочников
    group_id: Optional[int] = None
    lesson_id: Optional[int] = None
    teacher_id: Optional[int] = None
    lesson_type_id: Optional[int] = None

    # Данные, вводимые вручную
    tema: str  # Тема занятия (обязательно)
    nomer_zanyatiya: Optional[str] = None
    ped_tech: Optional[str] = None
    cel_zanyatiya: Optional[str] = None

    # Задачи
    zadachi_obuch: Optional[str] = None
    zadachi_razv: Optional[str] = None
    zadachi_vosp: Optional[str] = None

    prognoz_result: Optional[str] = None
    oborudovanie: Optional[str] = None
    istochniki: Optional[str] = None

    # Список этапов урока
    stages: List[TechCardStageData] = []


# Схема для ответа с техкартой (полные данные)
class TechCardResponse(BaseModel):
    id: int
    group_id: Optional[int]
    lesson_id: Optional[int]
    teacher_id: Optional[int]
    lesson_type_id: Optional[int]
    tema: str
    nomer_zanyatiya: Optional[str]
    ped_tech: Optional[str]
    cel_zanyatiya: Optional[str]
    zadachi_obuch: Optional[str]
    zadachi_razv: Optional[str]
    zadachi_vosp: Optional[str]
    prognoz_result: Optional[str]
    oborudovanie: Optional[str]
    istochniki: Optional[str]
    stages: List[TechCardStageResponse] = []

    class Config:
        from_attributes = True
