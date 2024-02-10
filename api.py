from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import EngineeringDisciplineModel, OptionsModel, EngineeringDisciplineModel
from db.database import SessionLocal
from db.schema import OptionsSchema, OptionRequirement
import re

db = SessionLocal()

#add logic to select most recent year 
def get_degree_reqs(degree_name: str, year: str, db: Session):
    degree_map = get_all_degrees(db)
    degree_formatted_name = degree_map[degree_name]
    reqs = (
        db.query(EngineeringDisciplineModel)
        .where(and_(EngineeringDisciplineModel.discipline_name == degree_formatted_name, EngineeringDisciplineModel.year == "2022-2023"))
        .all()
    )
    
    # print(reqs)

def get_all_degrees(db: Session):
    degree_map = {degree.discipline_name.lower().replace(' ', '_'): degree.discipline_name for degree in db.query(EngineeringDisciplineModel.discipline_name).distinct()}
    return degree_map


def clean_courses(courses):
    res = []
    for course in courses:
        res.append(course.strip())
    return res


def get_degree_missing_reqs(degree_id: str, courses_taken: list[str], year: str):
    reqs = (
        db.query(EngineeringDisciplineModel)
        .where(and_(EngineeringDisciplineModel.discipline_name == degree_id, EngineeringDisciplineModel.year == year))
        .all()
    )
    
    common_lists = ["CSE", "NSE", "TE"]

    missing_courses = {
        "mandatory_courses": [],
        "additional_reqs": {}
    }
    
    for req in reqs:
        if req.term != "MLSTN" and req.term != "PDENG" and req.term != "WKRPT" and req.term != "PD":
            if "," in req.course_codes:
                temp_dict = {}
                course_codes = req.course_codes.split(",")
                count = 0
                for course_code in course_codes:
                    temp_dict[course_code] = 0

                for course_taken in courses_taken:
                    if course_taken in temp_dict:
                        count += 1

                # if str(count) != req.number_of_courses:
                if req.term in common_lists:
                    if req.term not in missing_courses:
                        missing_courses[req.term] = {}
                    missing_courses[req.term]["completed"] = str(count)
                    missing_courses[req.term]["total"] = req.number_of_courses
                elif re.match(r'^\d[A-Z]$', req.term):
                    missing_courses["mandatory_courses"].append("(" + req.course_codes + ")")
                else:
                    if req.term not in missing_courses["additional_reqs"]:
                        missing_courses["additional_reqs"][req.term] = {}
                        missing_courses["additional_reqs"][req.term]["completed"] = str(count)
                        missing_courses["additional_reqs"][req.term]["total"] = req.number_of_courses
                    else:
                        missing_courses["additional_reqs"][req.term]["completed"] = str(int(missing_courses["additional_reqs"][req.term]["completed"]) + count)
                        missing_courses["additional_reqs"][req.term]["total"] = str(int(missing_courses["additional_reqs"][req.term]["total"]) + int(req.number_of_courses))

            else:
                if req.course_codes not in courses_taken:
                    if re.match(r'^\d[A-Z]$', req.term):
                            missing_courses["mandatory_courses"].append(req.course_codes)
                    else:
                        missing_courses["additional_reqs"][req.term]["completed"] = 0
                        missing_courses["additional_reqs"][req.term]["total"] = 1
    print(missing_courses)
    
    
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

    print(res)
    return res
    
    # for row in rows:
    #     
    #     if row["courses"][0] in ["TE", "CSE", "Communication Elective"]:
    #         if row["courses"][0] == "TE":
    #             te_count += row["number_of_courses"]
    #         elif row["courses"][0] == "CSE":
    #             cse_count += row["number_of_courses"]
    #         else:
    #             ce_count += row["number_of_courses"]

    #     elif row["number_of_courses"] == 1:
    #         res['mandatory_courses'] += courses
    #     else:
    #         spec_req = {
    #             "requirement_type": "CHOOSE_{}_OF_{}".format(row["number_of_courses"], len(row["courses"])),
    #             "required_count": row["number_of_courses"],
    #             "courses_to_choose_from": courses,
    #         }
    #         res['special_requirements'].append(spec_req)

    # res["elective_requirements"].append({
    #             "requirement_type": "TE",
    #             "required_count": te_count,
    # })

    # res["elective_requirements"].append({
    #             "requirement_type": "CSE",
    #             "required_count": cse_count,
    # })

    # res["elective_requirements"].append({
    #             "requirement_type": "Communication Elective",
    #             "required_count": ce_count,
    #         })

def find_missing_requirements(course_list, requirements):
    missing_requirements = []

    for requirement in requirements:
        courses_met = set(requirement.courses).intersection(course_list)
        if len(courses_met) < requirement.number_of_courses:
            missing_courses = set(requirement.courses) - courses_met
            missing_requirement = {
                "courses": list(missing_courses),
                "numberOfCourses": requirement.number_of_courses - len(courses_met)
            }
            missing_requirements.append(missing_requirement)

    return missing_requirements

def get_option_missing_reqs(option_id: str, courses_taken: list[str], year: str) -> list[OptionRequirement]:
    data = get_options_reqs(option_id, year, db)
    missing_requirements: list[OptionRequirement] = find_missing_requirements(courses_taken, data["requirements"])

    if not missing_requirements:
        print("YAY all requirements met")
    else:
        print("MISSING REQUIREMENTS:", missing_requirements)
    
    return missing_requirements

get_degree_missing_reqs("software_engineering", ["CS137", "ECE105", "MATH115", "MATH119", "CS241", "ECE313"], "2023")
# get_options_reqs("management_sciences_option", db)

# courseCodesTaken = ["CHE102", "MSCI100", "MATH115", "MATH116", "PHYS115", "MSCI 211", "MSCI 331", "MSCI 442"]
# get_option_missing_reqs(option_id="management_sciences_option", courses_taken=courseCodesTaken, year="2023")