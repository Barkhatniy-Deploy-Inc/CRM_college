from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Модели для tech_card_db в соответствии с требованиями
class LessonType(Base):
    __tablename__ = "lesson_type"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_type = Column(String)
    name_teacher = Column(String)


class Teacher(Base):
    __tablename__ = "Teacher"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)


class Lesson(Base):
    __tablename__ = "lesson"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    group_name = Column(String)
    teacher_id = Column(Integer, ForeignKey("Teacher.primary_key"))


class CuratorGroup(Base):
    __tablename__ = "curator_group"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, nullable=False)


class LearningOutcome(Base):
    __tablename__ = "learning_outcomes"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    skill = Column(Text)
    know = Column(Text)


class PkAndOk(Base):
    __tablename__ = "pk_and_ok"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    prof_comp = Column(Text)
    general_comp = Column(Text)


class SkillsAndKnowledge(Base):
    __tablename__ = "skills_and_knowledge"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lesson.primary_key"))
    skill = Column(Text)
    knowledge = Column(Text)


class TypeLesson(Base):
    __tablename__ = "type_lesson"
    
    primary_key = Column(Integer, primary_key=True, index=True)
    lesson = Column(String, nullable=False)
