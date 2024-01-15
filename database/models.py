from typing import Optional, Annotated
from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

import database


course_prerequisites = Table('course_prerequisites', database.Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('prerequisite_id', Integer, ForeignKey('courses.id'))
)

course_antirequisites = Table('course_antirequisites', database.Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('antirequisite_id', Integer, ForeignKey('courses.id'))
)

course_corequisites = Table('course_corequisites', database.Base.metadata,
   Column('course_id', Integer, ForeignKey('courses.id')),
   Column('corequisite_id', Integer, ForeignKey('courses.id'))
)

class Course(database.Base):
    __allow_unmapped__ = True
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code: Column(String, unique=True, index=True)
    course_name: Column(String, unique=True, index=True)
    credit: Column(Integer, unique=False, index=True)
    description: Column(String, index=True)
    location: Column(String, unique=True, index=True)
    prerequisites = relationship("Course", secondary="course_prerequisites")
    antirequisites = relationship("Course", secondary="course_antirequisites")
    corequisites = relationship("Course", secondary="course_corequisites")


class Options(database.Base):
    __allow_unmapped__ = True
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    option_name: Column(String, index=True)


class EngineeringDiscipline(database.Base):
    __allow_unmapped__ = True
    __tablename__ = 'engineering_discipline'
    id = Column(Integer, primary_key=True)
    discipline_name: Column(String, unique=True, index=True)
