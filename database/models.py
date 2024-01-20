from typing import Optional, Annotated
from fastapi import Depends
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqladmin import Admin, ModelView
from database.database import Base

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
    course_name = Column(String, unique=False, index=True)
    credit = Column(Integer, unique=False, index=True)
    description = Column(String, index=True)
    location = Column(String, unique=True, index=True)
    prerequisites = relationship(
        "Course",
        secondary="course_prerequisites",
        primaryjoin="Course.id==course_prerequisites.c.course_id",
        secondaryjoin="Course.id==course_prerequisites.c.prerequisite_id",
        backref="prerequisite_of",
    )

    antirequisites = relationship(
        "Course",
        secondary="course_antirequisites",
        primaryjoin="Course.id==course_antirequisites.c.course_id",
        secondaryjoin="Course.id==course_antirequisites.c.antirequisite_id",
        backref="antirequisite_of",
    )

    corequisites = relationship(
        "Course",
        secondary="course_corequisites",
        primaryjoin="Course.id==course_corequisites.c.course_id",
        secondaryjoin="Course.id==course_corequisites.c.corequisite_id",
        backref="corequisite_of",
    )


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
