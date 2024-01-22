from typing import Optional, Annotated
from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base


class Course(Base):
    __allow_unmapped__ = True
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String, unique=False, index=True)
    credit = Column(Integer, unique=False, index=True)
    description = Column(String, index=True)
    location = Column(String, unique=True, index=True)
    requirements_description = Column(String, unique=False)
    prerequisites = Column(String, unique=False, index=True)
    antirequisites = Column(String, unique=False, index=True)
    corequisites = Column(String, unique=False, index=True)



class Options(Base):
    __allow_unmapped__ = True
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    option_name = Column(String, index=True)


class EngineeringDiscipline(Base):
    __allow_unmapped__ = True
    __tablename__ = 'engineering_discipline'
    id = Column(Integer, primary_key=True)
    discipline_name = Column(String, unique=True, index=True)

class Prerequisite(Base):
    __allow_unmapped__ = True
    __tablename__ = 'prerequisites'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    logic = Column('logic', String, unique=False, index=True)
    courses =Column('courses', String, unique=False, index=True)
    min_level = Column('min_level', String, unique=False, index=True)
    

class Antirequisite(Base):
    __allow_unmapped__ = True
    __tablename__ = 'antirequisites'
    id = Column(Integer, primary_key=True)
    course_id = Column('course_id', Integer, ForeignKey('courses.id'))
    courses = Column('courses', String, unique=False, index=True)
    extra_info = Column('extra_info', String, unique=False)

