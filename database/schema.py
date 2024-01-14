from typing import Optional, Annotated
from fastapi_camelcase import CamelModel
from fastapi import Depends


class Course(CamelModel):
    course_code: str
    course_name: str
    credit: int
    description: str
    location: str


class Options(CamelModel):
    option_name: str


class EngineeringDiscipline(CamelModel):
    discipline_name: str




