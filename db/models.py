from typing import Optional, Annotated
from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Float
from sqlalchemy.orm import relationship

from .database import Base


class CourseModel(Base):
    __allow_unmapped__ = True
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String, unique=False, index=True)
    credit = Column(Integer, unique=False, index=True, nullable=True)
    description = Column(String, index=True)
    location = Column(String, unique=True, index=True, nullable=True)
    requirements_description = Column(String, unique=False, nullable=True)
    prerequisites = Column(String, unique=False, index=True, nullable=True)
    antirequisites = Column(String, unique=False, index=True, nullable=True)
    corequisites = Column(String, unique=False, index=True, nullable=True)

    def __str__(self):
        return self.course_code


class OptionsModel(Base):
    __allow_unmapped__ = True
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    option_name = Column(String, index=True)
    course_codes = Column(String, unique=False)
    number_of_courses = Column(Integer, unique=False)
    additional_requirements = Column(String, unique=False)
    name = Column(String, unique=False)
    link = Column(String, unique=False)
    year = Column(String, unique=False)
    name = Column(String, unique=False)


class EngineeringDisciplineModel(Base):
    __allow_unmapped__ = True
    __tablename__ = 'engineering_discipline'
    id = Column(Integer, primary_key=True)
    discipline_name = Column(String, unique=False, index=True)
    course_codes = Column(String, unique=False)
    number_of_courses = Column(Integer, unique=False)
    credits_required = Column(Float, unique=False)
    term = Column(String, unique=False)
    additional_requirements = Column(String, unique=False)
    link = Column(String, unique=False)
    year = Column(String, unique=False)


class PrerequisiteModel(Base):
    __allow_unmapped__ = True
    __tablename__ = 'prerequisites'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    logic = Column('logic', String, unique=False, index=True)
    courses = Column('courses', String, unique=False, index=True)
    min_level = Column('min_level', String, unique=False, index=True)


class AntirequisiteModel(Base):
    __allow_unmapped__ = True
    __tablename__ = 'antirequisites'
    id = Column(Integer, primary_key=True)
    course_id = Column('course_id', Integer, ForeignKey('courses.id'))
    courses = Column('courses', String, unique=False, index=True)
    extra_info = Column('extra_info', String, unique=False)
