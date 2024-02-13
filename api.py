import functools
from collections import defaultdict
from functools import lru_cache

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from db.models import EngineeringDisciplineModel, OptionsModel, EngineeringDisciplineModel, CourseModel
from db.database import SessionLocal
from db.schema import OptionsSchema, OptionRequirement, CoursesTakenIn, DegreeMissingReqs, AdditionalReqCount, \
    DegreeReqs, DegreeRequirement, CourseWithTagsSchema, TagSchema
import re

db = SessionLocal()


def clean_courses(courses):
    res = []
    for course in courses:
        res.append(course.strip())
    return res


def get_all_degrees(db: Session):
    degree_map = {degree.discipline_name.lower().replace(' ', '_'): degree.discipline_name for degree in
                  db.query(EngineeringDisciplineModel.discipline_name).distinct()}
    return degree_map


def is_degree_exist_for_year(degree_name: str, year: str, db: Session):
    return db.query(
        db.query(func.count())
        .filter(
            and_(
                EngineeringDisciplineModel.discipline_name == degree_name,
                EngineeringDisciplineModel.year == year
            )
        )
        .scalar()
    ).scalar() > 0


# add logic to select most recent year
def get_degree_reqs(degree_name: str, year: str, db: Session):
    degree_map = get_all_degrees(db)
    degree_formatted_name = degree_map[degree_name]

    if (
            db.query(
                db.query(func.count())
                        .filter(
                    and_(
                        EngineeringDisciplineModel.discipline_name == degree_formatted_name,
                        EngineeringDisciplineModel.year == year
                    )
                )
                        .scalar()
            ).scalar() > 0
    ):
        rows = [{"courses": row.course_codes.split(","), "number_of_courses": row.number_of_courses, "term": row.term}
                for row in
                db.query(EngineeringDisciplineModel)
                .where(and_(EngineeringDisciplineModel.discipline_name == degree_formatted_name,
                            EngineeringDisciplineModel.year == year))
                .all()]
    else:
        latest_year = (
            db.query(func.max(EngineeringDisciplineModel.year))
            .filter(EngineeringDisciplineModel.discipline_name == degree_formatted_name)
            .scalar()
        )
        rows = [{"courses": row.course_codes.split(","), "number_of_courses": row.number_of_courses, "term": row.term}
                for row in
                db.query(EngineeringDisciplineModel)
                .where(and_(EngineeringDisciplineModel.discipline_name == degree_formatted_name,
                            EngineeringDisciplineModel.year == latest_year))
                .all()]

    requirements = DegreeReqs(mandatory_courses=[], additional_reqs={})

    for row in rows:
        if row["term"] != "MLSTN" and row["term"] != "PDENG" and row["term"] != "WKRPT" and row["term"] != "PD":
            courses = clean_courses(row["courses"])
            if len(courses) > 1:
                add_req_dict = DegreeRequirement(courses=[], number_of_courses=row["number_of_courses"])
                add_req_dict.courses = courses
                requirements.additional_reqs[row["term"]] = add_req_dict
            else:
                requirements.mandatory_courses += courses

    return requirements


def populate_courses_tags(degree_name: str, year: str, courses: list[CourseWithTagsSchema]):
    for course in courses:
        populate_course_tags(degree_name=degree_name, year=year, course=course)


@lru_cache()
def populate_course_tags(degree_name: str, year: str, course: CourseWithTagsSchema) -> None:
    print("Attempting to populate tag for ", course.course_code)
    tags = get_degree_tags(degree_name=degree_name, degree_year=year)
    print("== degree tags", tags)
    # EngineeringDisciplines table has no space in course codes, other tables do
    course_code_no_space = course.course_code.replace(" ", "")
    course_tags = tags[course_code_no_space] if course_code_no_space in tags else ['ELEC']
    course.tags = [tag_name_to_object(tag_name) for tag_name in course_tags]
    return


def tag_name_to_object(tag_name: str) -> TagSchema:
    # blue = mandatory major requirement
    # red = TE
    # yellow = other requirement
    # purple = option requirement
    # green = elective
    name_to_schema = {
        "1A": TagSchema(code='1A', color='blue', short_name='1A', long_name='1A'),
        "1B": TagSchema(code='1B', color='blue', short_name='1B', long_name='1B'),
        "2A": TagSchema(code='2A', color='blue', short_name='2A', long_name='2A'),
        "2B": TagSchema(code='2B', color='blue', short_name='2B', long_name='2B'),
        "3A": TagSchema(code='3A', color='blue', short_name='3A', long_name='3A'),
        "3B": TagSchema(code='3B', color='blue', short_name='3B', long_name='3B'),
        "4A": TagSchema(code='4A', color='blue', short_name='4A', long_name='4A'),
        "4B": TagSchema(code='4B', color='blue', short_name='4B', long_name='4B'),
        "ATE": TagSchema(code='ATE', color='red', short_name='ATE', long_name='ATE'),
        "CSE": TagSchema(code='CSE', color='yellow', short_name='CSE', long_name='Complimentary Studies Elective'),
        "ELEC": TagSchema(code='ELEC', color='green', short_name='ELEC', long_name='Elective'),
        "ETHICS": TagSchema(code='ETHICS', color='yellow', short_name='ETHICS', long_name='Ethics'),
        "LE": TagSchema(code='LE', color='yellow', short_name='LE', long_name='Linkage Electives'),
        "MLSTN": TagSchema(code='MLSTN', color='green', short_name='MLSTN', long_name='Milestone'),
        "NSE": TagSchema(code='NSE', color='yellow', short_name='NSE', long_name='Natural Science Elective'),
        "PD": TagSchema(code='PD', color='yellow', short_name='PD', long_name='Professional Development'),
        "PDENG": TagSchema(code='PDENG', color='yellow', short_name='PDENG', long_name='Professional Development'),
        "PRACTICE": TagSchema(code='PRACTICE', color='yellow', short_name='PRACTICE', long_name='Practice'),
        "TE": TagSchema(code='TE', color='red', short_name='TE', long_name='Technical Elective'),
        "WKRPT": TagSchema(code='WKRPT', color='yellow', short_name='WKRPT', long_name='Work Report'),
        "WKTRM": TagSchema(code='WKTRM', color='yellow', short_name='WKTRM', long_name='Work Term'),
        "WTREF": TagSchema(code='WTREF', color='yellow', short_name='WTREF', long_name='Work Term Reflection'),
    }

    return name_to_schema[tag_name]


@functools.cache  # This should never change so we can indefinitely cache it
def get_degree_tags(degree_name: str, degree_year: str):
    # TODO: Implement logic that takes into account the case that 2015 and 2017 are published, but one requests for
    #  2016 (it should return 2015 but currently returns 2017)
    if is_degree_exist_for_year(degree_name, degree_year, db):
        tags = (
            db.query(EngineeringDisciplineModel.discipline_name,
                     EngineeringDisciplineModel.course_codes,
                     EngineeringDisciplineModel.term).filter(
                and_(
                    EngineeringDisciplineModel.discipline_name == degree_name,
                    EngineeringDisciplineModel.year == str(degree_year)
                )
            )).all()
    else:
        latest_year = (
            db.query(func.max(EngineeringDisciplineModel.year))
            .filter(EngineeringDisciplineModel.discipline_name == degree_name)
            .scalar()
        )
        tags = (
            db.query(EngineeringDisciplineModel.discipline_name,
                     EngineeringDisciplineModel.course_codes,
                     EngineeringDisciplineModel.term).filter(
                and_(
                    EngineeringDisciplineModel.discipline_name == degree_name,
                    EngineeringDisciplineModel.year == str(latest_year)
                )
            )).all()

    # [('management_engineering', 'CHE102', '1A'), ('management_engineering', 'MSCI100', '1A'),
    #  ('management_engineering', 'MATH115', '1A'), ('management_engineering', 'CHE102', '1A'),
    #  ('management_engineering', 'MSCI100', '1A'), ('management_engineering', 'MATH115', '1A'),
    #  ('management_engineering', 'MATH116', '1A'), ('management_engineering', 'PHYS115', '1A')]

    # Reduce the tags by course code
    tags_dict = defaultdict(set)
    for tags_tuple in tags:
        for course_code in tags_tuple[1].split(","):
            tags_dict[course_code].add(tags_tuple[2])
    return tags_dict


def search_and_populate_courses(q: str, offset: int, degree_year: int, page_size: int, degree_name: str) -> list[
    CourseWithTagsSchema]:
    courses = (db.query(CourseModel).order_by(
        (CourseModel.course_code + " " + CourseModel.course_name).op("<->")(q).asc(),
    ).offset(offset).limit(page_size)).all()

    print("pre-populate", courses)
    populate_courses_tags(degree_name=degree_name, year=degree_year, courses=courses)
    print("post-populate", courses)
    return courses


def get_degree_missing_reqs(degree_id: str, courses_taken: CoursesTakenIn, year: str, db: Session) -> DegreeMissingReqs:
    if (
            db.query(
                db.query(func.count())
                        .filter(
                    and_(
                        EngineeringDisciplineModel.discipline_name == degree_id,
                        EngineeringDisciplineModel.year == year
                    )
                )
                        .scalar()
            ).scalar() > 0
    ):
        reqs = (
            db.query(EngineeringDisciplineModel)
            .where(
                and_(EngineeringDisciplineModel.discipline_name == degree_id, EngineeringDisciplineModel.year == year))
            .all()
        )
    else:
        latest_year = (
            db.query(func.max(EngineeringDisciplineModel.year))
            .filter(EngineeringDisciplineModel.discipline_name == degree_id)
            .scalar()
        )
        reqs = (
            db.query(EngineeringDisciplineModel)
            .where(and_(EngineeringDisciplineModel.discipline_name == degree_id,
                        EngineeringDisciplineModel.year == latest_year))
            .all()
        )

    missing_courses = DegreeMissingReqs(mandatory_courses=[], additional_reqs={})

    for req in reqs:
        if req.term != "MLSTN" and req.term != "PDENG" and req.term != "WKRPT" and req.term != "PD":
            if "," in req.course_codes:
                temp_dict = {}
                course_codes = req.course_codes.split(",")
                count = 0
                for course_code in course_codes:
                    temp_dict[course_code] = 0

                for course_taken in courses_taken.course_codes_taken:
                    if course_taken in temp_dict:
                        count += 1

                if re.match(r'^\d[A-Z]$', req.term):
                    missing_courses.mandatory_courses.append("(" + req.course_codes + ")")
                else:
                    if req.term not in missing_courses.additional_reqs:
                        missing_courses.additional_reqs[req.term] = AdditionalReqCount(completed=str(count),
                                                                                       total=str(req.number_of_courses))
                    else:
                        missing_courses.additional_reqs[req.term].completed = str(
                            int(missing_courses.additional_reqs[req.term].completed) + count)
                        missing_courses.additional_reqs[req.term].total = str(
                            int(missing_courses.additional_reqs[req.term].total) + int(req.number_of_courses))

            else:
                if req.course_codes not in courses_taken:
                    if re.match(r'^\d[A-Z]$', req.term):
                        missing_courses.mandatory_courses.append(req.course_codes)
                    else:
                        missing_courses.additional_reqs[req.term] = AdditionalReqCount(completed="0", total="1")
    return missing_courses


def get_options_reqs(option_id: str, year: str, db: Session) -> OptionsSchema:
    rows = [{"courses": row.course_codes.split(","), "number_of_courses": row.number_of_courses} for row in
            db.query(OptionsModel)
            .filter(and_(OptionsModel.option_name == option_id, OptionsModel.year == year)).all()]
    res: OptionsSchema = {
        "option_name": str(option_id),  # Convert option_id to str if needed
        "requirements": [],
    }

    for row in rows:
        courses = clean_courses(row["courses"])
        course_map = {"courses": courses, "number_of_courses": row["number_of_courses"]}
        res["requirements"].append(OptionRequirement(**course_map))

    return res


def find_missing_requirements(course_list, requirements):
    missing_requirements = []
    for requirement in requirements:
        courses_met = set(requirement.courses).intersection(course_list.course_codes_taken)
        if len(courses_met) < requirement.number_of_courses:
            missing_courses = set(requirement.courses) - courses_met
            missing_requirement = {
                "courses": list(missing_courses),
                "numberOfCourses": requirement.number_of_courses - len(courses_met)
            }
            missing_requirements.append(missing_requirement)

    return missing_requirements


def get_option_missing_reqs(option_id: str, year: str, courses_taken: CoursesTakenIn) -> list[OptionRequirement]:
    data = get_options_reqs(option_id, year, db)
    missing_requirements: list[OptionRequirement] = find_missing_requirements(courses_taken, data["requirements"])

    if not missing_requirements:
        print("YAY all requirements met")
    else:
        print("MISSING REQUIREMENTS:", missing_requirements)

    return missing_requirements

# get_degree_missing_reqs("software_engineering", ["CS137", "ECE105", "MATH115", "MATH119", "CS241", "ECE313"], "2023")
# get_options_reqs("management_sciences_option", db)

# courseCodesTaken = ["CHE102", "MSCI100", "MATH115", "MATH116", "PHYS115", "MSCI 211", "MSCI 331", "MSCI 442"]
# get_option_missing_reqs(option_id="management_sciences_option", courses_taken=courseCodesTaken, year="2023")

# get_degree_reqs("systems_design_engineering", "2023", db)
