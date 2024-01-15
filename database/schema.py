from typing import Optional, Annotated
from fastapi_camelcase import CamelModel
from fastapi import Depends
from .database import Base
from sqlalchemy.orm import Mapped


class Course(Base):
    course_code: Mapped[str]
    course_name: Mapped[str]
    credit: Mapped[int]
    description: Mapped[str]
    location: Mapped[str]


class Options(Base):
    option_name: Mapped[str]


class EngineeringDiscipline(Base):
    discipline_name: Mapped[str]




