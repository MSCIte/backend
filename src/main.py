from typing import Annotated
import requests
from fastapi import FastAPI, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from db.models import CourseModel, EngineeringDisciplineModel, PrerequisiteModel
from db.schema import CourseWithTagsSchema, MissingReqs, OptionsSchema, CoursesTakenIn, OptionRequirement, DegreeMissingReqs, \
    DegreeReqs, DegreeMissingIn, RequirementsResult, SamplePath
from collections import defaultdict
from db.schema import CanTakeCourseBatch, RequirementsResults
from db.database import SessionLocal
from sqladmin import Admin
from sqlalchemy.orm import Session

from db import engine
from db.admin import admin_views
from db.database import SessionLocal
from .validation import can_take_course
from api import get_options_reqs, get_degree_reqs, get_all_degrees, get_degree_missing_reqs, get_option_missing_reqs, \
    get_degree_tags, search_and_populate_courses, populate_courses_tags, get_option_tags, merge_dicts, get_sample_paths

app = FastAPI()

origins = [
    # Prod and deploy previews
    "https://mscite.netlify.app",
    "https://mscite-dev.netlify.app",
    # Local dev
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex='https://.*\.netlify\.app',
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
# done
@app.get('/option/{opt_id}/reqs', response_model=OptionsSchema)
def options_reqs(opt_id: str, year: str, db: Session = Depends(get_db)):
    reqs = get_options_reqs(opt_id, year, db)
    return reqs


# done
@app.post('/option/{opt_id}/missing_reqs', response_model=MissingReqs)
def options_missing_reqs(opt_id: str, degree_missing_in: DegreeMissingIn, db: Session = Depends(get_db)):
    missing_reqs = get_option_missing_reqs(option_id=opt_id, courses_taken=degree_missing_in.course_codes_taken,
                                           year=degree_missing_in.year, db=db)
    return missing_reqs


# done
@app.get('/degree/{degree_name}/reqs', response_model=DegreeReqs)
def degree_reqs(degree_name: str, year: str, db: Session = Depends(get_db)):
    reqs = get_degree_reqs(degree_name, year, db)
    return reqs


# done
@app.get('/degree')
def degrees(db: Session = Depends(get_db)) -> list[str]:
    degree_names = get_all_degrees(db).keys()
    return degree_names


# done
@app.post('/degree/{degree_id}/missing_reqs', response_model=DegreeMissingReqs)
def degree_missing_reqs(degree_id: str, degree_missing_in: DegreeMissingIn = Body(...), db: Session = Depends(get_db)):
    missing_reqs = get_degree_missing_reqs(degree_id=degree_id, courses_taken=degree_missing_in.course_codes_taken,
                                           year=degree_missing_in.year, db=db)
    return missing_reqs


@app.post('/courses/can-take/batch', response_model=RequirementsResults)
def courses_can_take_batch(course_codes_can_take: CanTakeCourseBatch, db: Session = Depends(get_db)):
    res = RequirementsResults(results=[])
    res_dict = []
    for ind, course_input in enumerate(course_codes_can_take.can_take_course_codes):
        can_take = can_take_course(db, course_input.course_codes_taken, course_input.course_code)
        res_dict.append(
            RequirementsResult(result=can_take[0], message=can_take[1], course_code=course_input.course_code,
                               term=course_codes_can_take.can_take_course_codes[ind].term))

    res.results = res_dict
    return res


@app.post('/courses/can-take/{course_code}', response_model=RequirementsResult)
def courses_can_take(course_code: str, courses_taken: CoursesTakenIn, db: Session = Depends(get_db)):
    can_take = can_take_course(db, courses_taken.course_codes_taken, course_code)
    res = RequirementsResult(result=can_take[0], message=can_take[1], course_code=course_code, term=courses_taken.term)
    return res


# done
@app.get('/courses/search', response_model=list[CourseWithTagsSchema])
def search_courses(degree_name: Annotated[str, "The degree name, e.g. 'management_engineering'"],
                   degree_year: Annotated[str, "The year the plan was declared"],
                   option_name: Annotated[str, "The option name, e.g. 'management_engineering'"] = "",
                   option_year: Annotated[str, "The year the plan was declared"] = "",
                   q: str | None = None,
                   offset: Annotated[int | None, Query(title="Number of courses to offset the results from", ge=0)] = 0,
                   page_size: Annotated[int | None, Query(title="Number of results returned", gt=0, le=100)] = 20,
                   tag: str | None = None,
                   db: Session = Depends(get_db)
                   ):
    courses = search_and_populate_courses(q=q, offset=offset, page_size=page_size, degree_name=degree_name,
                                          degree_year=degree_year, db=db, option_name=option_name,
                                          option_year=option_year, tag=tag)

    return courses


@app.get('/courses/tags', response_model=list[CourseWithTagsSchema])
def tags(degree_name: Annotated[str, "The degree name, e.g. 'management_engineering'"],
         degree_year: Annotated[str, "The year the plan was declared"],
         option_name: Annotated[str, "The option name, e.g. 'management_engineering'"] = "",
         option_year: Annotated[str, "The year the plan was declared"] = "",
         db: Session = Depends(get_db)):
    courses_dict = get_degree_tags(degree_name, degree_year, db)
    if option_name and option_year:
        courses_dict = merge_dicts(courses_dict, get_option_tags(option_name, option_year, db))

    course_codes_list = list(courses_dict.keys())

    courses = db.query(CourseModel, PrerequisiteModel.min_level).outerjoin(CourseModel, PrerequisiteModel.course_id == CourseModel.id).filter(CourseModel.course_code.in_(course_codes_list)).all()

    courses_w_tags = populate_courses_tags(courses=courses, courses_tag_dict=courses_dict)
    return courses_w_tags


@app.get('/sample-path/{degree_name}', response_model=list[SamplePath])
def sample_path(degree_name: str, db: Session = Depends(get_db)):
    res = get_sample_paths(degree_name, db)
    print(res)
    return res


# Devops things

# @app.post('/update_server')
# def webhook():
#     repo = git.Repo('~/backend')
#     origin = repo.remotes.origin
#
#     origin.pull()
#
#     return "Updated Python Backend"


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}
