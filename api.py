import functools
from collections import defaultdict
from functools import lru_cache

from sqlalchemy.orm import Session
from sqlalchemy import and_, case, desc, func, or_, text
from db.models import EngineeringDisciplineModel, OptionsModel, EngineeringDisciplineModel, CourseModel
from db.database import SessionLocal
from db.schema import MissingList, MissingReqs, OptionsSchema, OptionRequirement, CoursesTakenIn, DegreeMissingReqs, \
    AdditionalReqCount, \
    DegreeReqs, DegreeRequirement, CourseWithTagsSchema, TagSchema
import re

db = SessionLocal()


def clean_courses(courses):
    res = []
    for course in courses:
        res.append(course.strip())
    return res


def get_all_degrees(db: Session = None) -> dict[str, str]:
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


def is_option_exist_for_year(option_name: str, year: str, db: Session):
    return db.query(
        db.query(func.count())
        .filter(
            and_(
                OptionsModel.option_name == option_name,
                OptionsModel.year == year
            )
        )
        .scalar()
    ).scalar() > 0


def merge_dicts(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            print("BITCH")
            result[key] = result[key].union(value)
        else:
            result[key] = value
    return result

# add logic to select most recent year
def get_degree_reqs(degree_name: str, year: str, db: Session) -> DegreeReqs:
    degree_map = get_all_degrees(db=db)
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


# def populate_courses_tags(degree_name: str, degree_year: str, courses: list[CourseWithTagsSchema], db: Session, option_name: str = "", option_year: str = "") -> None:
#     """
#     Mutates the courses list to include tags
#     """
#     for course in courses:
#         populate_course_tags(degree_name=degree_name, degree_year=degree_year, course=course, db=db, option_name=option_name, option_year=option_year)


# @lru_cache()
def populate_courses_tags(courses: list[CourseWithTagsSchema], courses_tag_dict: dict[str, set[str]]) -> None:
    """
    Mutates the course object to include tags
    """
    for course in courses:
        tags = courses_tag_dict[course.course_code]
        course.tags = []
        for tag in tags:
            course.tags.append(tag_name_to_object(tag))
        



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
        'SCE': TagSchema(code='SCE', color='yellow', short_name='SCE', long_name='Science Elective'),
        "elective": TagSchema(code='elective', color='purple', short_name='elective', long_name='Elective'),
        "organizational_studies": TagSchema(code='organizational_studies', color='orange', short_name='organizational_studies', long_name='Organizational Studies'),
        "eng_econ": TagSchema(code='eng_econ', color='yellow', short_name='pink', long_name='Engineering Economics'),
        "opti_1": TagSchema(code='opti_1', color='yellow', short_name='indigo', long_name='Optimization'),
    }

    return name_to_schema[tag_name]


@functools.cache  # This should never change so we can indefinitely cache it
def get_degree_tags(degree_name: str, degree_year: str, db: Session) -> dict[str, set[str]]:
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
        for course_code in tags_tuple[1].split(", "):
            tags_dict[course_code].add(tags_tuple[2])
    return tags_dict


@functools.cache  # This should never change so we can indefinitely cache it
def get_option_tags(option_name: str, option_year: str, db: Session) -> dict[str, set[str]]:
    if is_option_exist_for_year(option_name, option_year, db):
        tags = (
            db.query(OptionsModel.option_name,
                     OptionsModel.course_codes,
                     OptionsModel.name).filter(
                and_(
                    OptionsModel.option_name == option_name,
                    OptionsModel.year == str(option_year)
                )
            )).all()
    else:
        latest_year = (
            db.query(func.max(OptionsModel.year))
            .filter(OptionsModel.option_name == option_name)
            .scalar()
        )
        tags = (
            db.query(OptionsModel.option_name,
                     OptionsModel.course_codes,
                     OptionsModel.name).filter(
                and_(
                    OptionsModel.option_name == option_name,
                    OptionsModel.year == str(latest_year)
                )
            )).all()

    # [('management_engineering', 'CHE102', '1A'), ('management_engineering', 'MSCI100', '1A'),
    #  ('management_engineering', 'MATH115', '1A'), ('management_engineering', 'CHE102', '1A'),
    #  ('management_engineering', 'MSCI100', '1A'), ('management_engineering', 'MATH115', '1A'),
    #  ('management_engineering', 'MATH116', '1A'), ('management_engineering', 'PHYS115', '1A')]

    # Reduce the tags by course code
    tags_dict = defaultdict(set)
    for tags_tuple in tags:
        for course_code in tags_tuple[1].split(", "):
            tags_dict[course_code].add(tags_tuple[2])
    return tags_dict


def search_and_populate_courses(q: str, offset: int, degree_year: int, page_size: int, degree_name: str, db: Session) -> \
        (list)[CourseWithTagsSchema]:
    q = q.replace(" ", "")
    courses = (
    db.query(CourseModel)
    .filter(
        or_(
            CourseModel.course_code.ilike(f'%{q}%'),
            CourseModel.course_name.ilike(f'%{q}%'),
            text("similarity(course_code, :query) > 0.19").params(query=q),
            text("similarity(course_name, :query) > 0.19").params(query=q)
        )
    )
    .order_by(
        desc(text("similarity(course_code, :query)")).params(query=q), 
        CourseModel.course_code,
        desc(text("similarity(course_name, :query)")).params(query=q),
        CourseModel.course_name
        
    )
    .offset(offset)
    .limit(page_size)
    ).all()

    populate_courses_tags_search(degree_name=degree_name, year=str(degree_year), courses=courses, db=db)
    return courses

def populate_courses_tags_search(degree_name: str, year: str, courses: list[CourseWithTagsSchema], db: Session) -> None:
    """
    Mutates the course object to include tags
    """
    for course in courses:
        tags = get_degree_tags(degree_name=degree_name, degree_year=year, db=db)
        # EngineeringDisciplines table has no space in course codes, other tables do
        course_code_no_space = course.course_code.replace(" ", "")
        course_tags = tags[course_code_no_space] if course_code_no_space in tags else ['ELEC']
        course.tags = [tag_name_to_object(tag_name) for tag_name in course_tags]


def get_degree_missing_reqs(degree_id: str, courses_taken: list[str], year: str, db: Session) -> DegreeMissingReqs:
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

    missing_courses = DegreeMissingReqs(mandatory_courses=[], number_of_mandatory_courses=0, additional_reqs={})

    mandatory_course_count = 0
    for req in reqs:
        if re.match(r'^\d[A-Z]$', req.term):
            mandatory_course_count += 1

    missing_courses.number_of_mandatory_courses = mandatory_course_count

    for req in reqs:
        req_long_name = tag_name_to_object(req.term).long_name
        if req.term != "MLSTN" and req.term != "PDENG" and req.term != "WKRPT" and req.term != "PD":
            if "," in req.course_codes:
                temp_dict = {}
                course_codes = req.course_codes.split(",")
                count = 0
                for course_code in course_codes:
                    temp_dict[course_code] = 0

                for course_taken in courses_taken:
                    if course_taken in temp_dict:
                        if re.match(r'^\d[A-Z]$', req.term):
                            course_codes.remove(course_taken)
                        count += 1

                if re.match(r'^\d[A-Z]$', req.term):
                    course_codes = ", ".join(course_codes)
                    missing_courses.mandatory_courses.append("(" + course_codes + ")")
                else:
                    if req.term not in missing_courses.additional_reqs:
                        missing_courses.additional_reqs[req_long_name] = AdditionalReqCount(completed=str(count),
                                                                                       total=str(req.number_of_courses))
                    else:
                        missing_courses.additional_reqs[req_long_name].completed = str(
                            int(missing_courses.additional_reqs[req_long_name].completed) + count)
                        missing_courses.additional_reqs[req_long_name].total = str(
                            int(missing_courses.additional_reqs[req_long_name].total) + int(req.number_of_courses))

            else:
                if req.course_codes not in courses_taken:
                    if re.match(r'^\d[A-Z]$', req.term):
                        missing_courses.mandatory_courses.append(req.course_codes)
                    else:
                        missing_courses.additional_reqs[req_long_name] = AdditionalReqCount(completed="0", total="1")
    return missing_courses


def get_options_reqs(option_id: str, year: str, db: Session) -> OptionsSchema:
    rows = [{"courses": row.course_codes.split(","), "number_of_courses": row.number_of_courses, "name": row.name} for
            row in
            db.query(OptionsModel).filter(and_(OptionsModel.option_name == option_id, OptionsModel.year == year)).all()]
    res: OptionsSchema = {
        "option_name": str(option_id),  # Convert option_id to str if needed
        "requirements": [],
    }

    print('== rows', rows)

    for row in rows:
        courses = clean_courses(row["courses"])
        course_map = {"courses": courses, "number_of_courses": row["number_of_courses"], "name": row['name']}
        res["requirements"].append(OptionRequirement(**course_map))

    print("==wtf is this", res)

    return res


def find_missing_requirements(course_list: list[str], requirements):
    missing_requirements = MissingReqs(lists=[])

    for requirement in requirements:
        courses_dict = {}

        # For each course in requirement that is in course_list, add to dictionary and assign value of True else False
        for course in requirement.courses:
            courses_dict[course] = course in course_list

        # Calculate the total number of courses needed to complete the requirements
        total_courses_to_complete = requirement.number_of_courses

        # Create the MissingList instance for the current requirement
        missing_requirement = MissingList(
            list_name=requirement.name,
            courses=courses_dict,
            totalCourseToComplete=total_courses_to_complete
        )

        missing_requirements.lists.append(missing_requirement)

    return missing_requirements


def get_option_missing_reqs(option_id: str, year: str, courses_taken: CoursesTakenIn, db: Session) -> MissingReqs:
    # get the requirements for the option
    data = get_options_reqs(option_id, year, db)
    # find the missing requirements
    missing_requirements: MissingReqs = find_missing_requirements(courses_taken, data["requirements"])

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
