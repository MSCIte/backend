from typing import Type

from fastapi import FastAPI, Depends
import requests
from db.schema import CoursesTakenBody
from db.database import SessionLocal
from db.models import CourseModel, PrerequisiteModel, OptionsModel
from sqladmin import Admin
from db import engine
from db.admin import admin_views
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/courses/top")
def get_top_courses(db: Session = Depends(get_db)):
    import random
    courses = db.query(CourseModel).limit(10).all()
    random.shuffle(courses)
    return courses


@app.get("/courses/all")
def courses_all(db: Session = Depends(get_db)):
    return db.query(CourseModel).all()


@app.get("/courses")
def options(db: Session = Depends(get_db)):
    return db.query(OptionsModel).all()


@app.get("/prereqs")
def prereqs(db: Session = Depends(get_db)) -> list[PrerequisiteModel]:
    return db.query(PrerequisiteModel).limit(10).all()


@app.get("/courses")
def courses(db: Session = Depends(get_db)):
    return db.query(CourseModel).all()


@app.post('/can-take/{course}')
def can_take(courses_taken: CoursesTakenBody, course: str, db: Session = Depends(get_db)):
    import random
    print(courses_taken)
    # can_take_course(courses_taken, course)
    return random.choice([True, False])
    # session = SessionLocal()
    # course = session.query(Course).filter(Course.course_id == course_id).first()
    # if course is None:
    #     return {'error': 'course not found'}
    # prereqs = session.query(Prerequisite).filter(Prerequisite.course_id == course_id).all()
    # antireqs = session.query(Antirequisite).filter(Antirequisite.course_id == course_id).all()
    # return {
    #     'course': course.to_dict(),
    #     'prereqs': [prereq.to_dict() for prereq in prereqs],
    #     'antireqs': [antireq.to_dict() for antireq in antireqs]
    # }

# Yoinked from uw flow
# def normalize_reqs_str(str_):
#     """Normalize the prereq string of a course

#     TODO(mack): handle the following special cases:
#         1) "CS/ECE 121"
#     """

#     # Split on non-alphanumeric characters (includes chars we split on)
#     old_splits = re.compile('(\W+)').split(str_)
#     # Newly normalized splits
#     new_splits = []
#     # Last department id encountered as we traverse prereq str
#     last_dep_id = None

#     # Traverse the splits
#     for split in old_splits:
#         new_split = split
#         if last_dep_id and re.findall(r'^[0-9]{3}[a-z]?$', split.lower()):
#             # If there's a previous dep id and this matches the number portion
#             # of a course, check if this is a valid course
#             # NOTE: we're not validating whether the course exists since
#             # we should still normalize to make the output to look consistent,
#             # even when the course does not exist
#             new_split = last_dep_id.upper() + split
#         elif (re.findall('^[A-Z]+', split) and
#               m.Department.objects.with_id(split.lower())):
#             # We check it's uppercase, so we don't have false positives like
#             # "Earth" that was part of "Earth Science student"

#             last_dep_id = split.lower()
#             # Do not include the department id since it will be included
#             # with the course we find
#             new_split = ''

#         new_splits.append(new_split)

#         # We're here if this split matches a department id
#         # Increment idx by 1 more to skip the next non-alphanum character

#     new_str = ''.join(new_splits)
#     # While removing department ids, we could have left redundant spaces
#     # (e.g. "CS 247" => " CS247", so remove them now.
#     return re.sub('\s+', ' ', new_str).strip()
