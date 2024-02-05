from typing import Annotated
import requests
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.models import CourseModel
from db.schema import CourseSchema, CourseWithTagsSchema
from db.schema import CoursesTakenIn, RequirementsResults
from db.database import SessionLocal
from sqladmin import Admin
from sqlalchemy.orm import Session

from db import engine
from db.admin import admin_views
from db.database import SessionLocal
from .validation import can_take_course
from .api import get_options_reqs, get_degree_reqs, get_all_degrees

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin dashboard
admin = Admin(app, engine)
for view in admin_views:
    admin.add_view(view)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "Worasdfld"}


@app.get("/query")
def read_item():
    url = 'https://openapi.data.uwaterloo.ca/v3/subjects'
    api_key = '2FEF9C75B2F34CAF91CC3B6DF0D6C6C0'
    header = {'x-api-key': api_key}

    response = requests.get(url, headers=header)
    return response.json()


# --------

@app.get('/option/{opt_id}/reqs')
def options_reqs(opt_id: int, db: Session = Depends(get_db)) -> list[CourseSchema]:
    reqs = get_options_reqs(opt_id, db)
    pass


@app.get('/option/{opt_id}/missing_reqs')
def options_missing_reqs(opt_id: int, db: Session = Depends(get_db)) -> list[CourseSchema]:
    pass


@app.get('/degree/{degree_name}/reqs')
def degree_reqs(degree_name: str, db: Session = Depends(get_db)) -> list[CourseSchema]:
    reqs = get_degree_reqs(degree_name, db)
    pass

@app.get('/degree')
def degrees(db: Session = Depends(get_db)) -> list[str]:
    degrees = get_all_degrees(db).keys()
    return degrees

@app.get('/degree/{degree_id}/missing_reqs')
def degree_missing_reqs(degree_id: str, db: Session = Depends(get_db)) -> list[CourseSchema]:

    pass

@app.get('/courses/can-take/{course_code}')
def courses_can_take(course_code: str, courses_taken: CoursesTakenIn, db: Session = Depends(get_db)) -> RequirementsResults:
    can_take = can_take_course(db, courses_taken.course_codes_taken, course_code)
    res = RequirementsResults(result=can_take[0], message=can_take[1])
    return res

@app.get('/courses/search', response_model=list[CourseWithTagsSchema])
def search_courses(q: str | None = None, offset: Annotated[int | None, "bruh"] = 0, db: Session = Depends(get_db)):
    # https://stackoverflow.com/a/71147604
    def has_numbers(input_string: str) -> bool:
        return any(char.isdigit() for char in input_string)

    if has_numbers(q):
        # Searching for specific course code
        courses = db.query(CourseModel).order_by(
            (CourseModel.course_code + " " + CourseModel.course_name).op("<->")(q).asc(),
        ).offset(offset).limit(100).all()
    else:
        # Searching by course name only
        # Use <-> for performance
        courses = db.query(CourseModel).order_by(
            CourseModel.course_name.op("<->")(q).asc()
        ).offset(offset).limit(100).all()

    return courses

@app.get('/sample-path')
def sample_path():
    return {
        "lol": "rooined"
    }
    
