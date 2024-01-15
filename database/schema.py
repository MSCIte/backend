from typing import Optional, Annotated
from fastapi import Depends
import database
from sqlalchemy.orm import Mapped


class Course(database.Base):
    course_code: Mapped[str]
    course_name: Mapped[str]
    credit: Mapped[int]
    description: Mapped[str]
    location: Mapped[str]


class Options(database.Base):
    option_name: Mapped[str]


class EngineeringDiscipline(database.Base):
    discipline_name: Mapped[str]




