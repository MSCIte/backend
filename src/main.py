import requests
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.schema import CoursesTakenBody, RequirementsResults, CourseSchema
from db.database import SessionLocal
from db.models import CourseModel, PrerequisiteModel, OptionsModel
from sqladmin import Admin
from sqlalchemy.orm import Session

from db import engine
from db.admin import admin_views
from db.database import SessionLocal
from db.models import CourseModel, PrerequisiteModel, OptionsModel
from db.schema import CoursesTakenBody, RequirementsResults
from .validation import can_take_course

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
async def options_reqs(opt_id: int) -> list(CourseSchema):
    pass


@app.get('/option/{opt_id}/missing_reqs')
async def options_missing_reqs(opt_id: int) -> list(CourseSchema):
    pass


@app.get('/degree/{degree_id}/reqs')
def degree_reqs(degree_id: int) -> list(CourseSchema):
    pass

@app.get('/degree/{degree_id}/missing_reqs')
async def degree_missing_reqs(degree_id) -> list(CourseSchema):
    pass

@app.get('/courses/can-take/{course_code}')
async def courses_can_take(course_code: str, courses_taken: CoursesTakenBody, db: Session = Depends(get_db)) -> RequirementsResults:
    can_take = can_take_course(db, courses_taken.course_codes_taken, course_code)
    res = RequirementsResults(result=can_take[0], message=can_take[1])
    return res




@app.get('/courses/search')
async def search_courses(q: str | None = None, offset: int | None = 0) -> list(CourseSchema):
    
    pass

@app.get('/sample-path')
async def sample_path():
    return {
        "lol": "rooined"
    }
    
