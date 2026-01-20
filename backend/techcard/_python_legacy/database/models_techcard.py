from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BaseTechCard = declarative_base()


# Таблица для хранения технологических карт
class TechCard(BaseTechCard):
    __tablename__ = "tech_cards"

    id = Column(Integer, primary_key=True, index=True)

    # Основные данные из справочников (ID из databaseforbros.db)
    group_id = Column(Integer, nullable=True)  # ID группы
    lesson_id = Column(Integer, nullable=True)  # ID предмета
    teacher_id = Column(Integer, nullable=True)  # ID преподавателя
    lesson_type_id = Column(Integer, nullable=True)  # ID типа урока

    # Данные, которые вводятся вручную
    tema = Column(Text, nullable=False)  # Тема занятия
    nomer_zanyatiya = Column(String, nullable=True)  # Номер занятия по теме

    # Педагогические технологии
    ped_tech = Column(Text, nullable=True)  # Используемые пед. технологии

    # Цель занятия
    cel_zanyatiya = Column(Text, nullable=True)  # Цель занятия

    # Задачи занятия
    zadachi_obuch = Column(Text, nullable=True)  # Обучающие задачи
    zadachi_razv = Column(Text, nullable=True)  # Развивающие задачи
    zadachi_vosp = Column(Text, nullable=True)  # Воспитательные задачи

    # Прогнозируемый результат
    prognoz_result = Column(Text, nullable=True)  # Знания, умения, компетенции

    # Оборудование
    oborudovanie = Column(Text, nullable=True)  # Оборудование

    # Список источников
    istochniki = Column(Text, nullable=True)  # Список использованных источников

    # Связь с этапами урока
    stages = relationship("TechCardStage", back_populates="tech_card")


# Таблица для этапов урока
class TechCardStage(BaseTechCard):
    __tablename__ = "tech_card_stages"

    id = Column(Integer, primary_key=True, index=True)
    tech_card_id = Column(Integer, ForeignKey("tech_cards.id"), nullable=False)  # Связь с техкартой

    nomer_etapa = Column(Integer, nullable=False)  # Номер этапа (1, 2, 3, 4...)
    nazvanie_etapa = Column(String, nullable=False)  # Название этапа (например "Актуализация опорных знаний")

    cel_etapa = Column(Text, nullable=True)  # Цель этапа
    dlitelnost = Column(String, nullable=True)  # Длительность этапа (например "10 мин")

    deyatelnost_prepod = Column(Text, nullable=True)  # Деятельность преподавателя
    deyatelnost_obuch = Column(Text, nullable=True)  # Деятельность обучающихся

    formiruemye_kompetencii = Column(Text, nullable=True)  # Формируемые компетенции

    # Связь обратно с техкартой
    tech_card = relationship("TechCard", back_populates="stages")