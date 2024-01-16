from typing import Optional, Annotated
from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base


course_prerequisites = Table('course_prerequisites', Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('prerequisite_id', Integer, ForeignKey('courses.id'))
)

course_antirequisites = Table('course_antirequisites', Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('antirequisite_id', Integer, ForeignKey('courses.id'))
)

course_corequisites = Table('course_corequisites', Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('corequisite_id', Integer, ForeignKey('courses.id'))
)

class Course(Base):
    __allow_unmapped__ = True
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code = Column(String, unique=True, index=True)
    course_name = Column(String, unique=True, index=True)
    credit = Column(Integer, unique=False, index=True)
    description = Column(String, index=True)
    location = Column(String, unique=True, index=True)
    prerequisites = relationship("Course", secondary="course_prerequisites")
    antirequisites = relationship("Course", secondary="course_antirequisites")
    corequisites = relationship("Course", secondary="course_corequisites")


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
