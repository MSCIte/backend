from typing import Optional, Annotated
from fastapi import Depends
import database
from pydantic import BaseModel


class Course(BaseModel):
    course_code: str
    course_name: str
    credit: int
    description: str
    location: str

    class Config:
        from_attributes = True


class Options(BaseModel):
    option_name: str

    class Config:
        from_attributes = True


class EngineeringDiscipline(BaseModel):
    discipline_name: str

    class Config:
        from_attributes = True




