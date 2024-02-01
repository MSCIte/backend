from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import EngineeringDisciplineModel, OptionsModel, EngineeringDisciplineModel
from db.database import SessionLocal

db = SessionLocal()

def get_degree_reqs(degree_name: str, db: Session):
    degree_map = get_all_degrees(db)
    degree_formatted_name = degree_map[degree_name]
    reqs = (
        db.query(EngineeringDisciplineModel)
        .where(and_(EngineeringDisciplineModel.discipline_name == degree_formatted_name, EngineeringDisciplineModel.year == "2022-2023"))
        .all()
    )
    
    print(reqs)

def get_all_degrees(db: Session):
    degree_map = {degree.discipline_name.lower().replace(' ', '_'): degree.discipline_name for degree in db.query(EngineeringDisciplineModel.discipline_name).distinct()}
    return degree_map


def clean_courses(courses):
    res = []
    for course in courses:
        if course.strip() in ["LEC", "TUT"] or course.isdigit():
            continue
        else:
            res.append(course)
    return res

def get_options_reqs(option_id: str, db: Session):
    rows = [{"courses" : row.course_codes.split(","), "number_of_courses" : row.number_of_courses} for row in 
            db.query(EngineeringDisciplineModel)
            .where(and_(EngineeringDisciplineModel.discipline_name == option_id, EngineeringDisciplineModel.year == "2022-2023")).all()]

    testing = db.query(EngineeringDisciplineModel).where(and_(EngineeringDisciplineModel.discipline_name == option_id, EngineeringDisciplineModel.year == "2022-2023")).all()
    print(len(testing))

    for entry in testing:
        print(entry.course_codes)

    res = {
        "discipline": option_id,
        "mandatory_courses": [],
        "special_requirements": [],
        "elective_requirements": [],
    }

    te_count = 0
    cse_count = 0
    ce_count  = 0
    
    for row in rows:
        courses = clean_courses(row["courses"])
        if row["courses"][0] in ["TE", "CSE", "Communication Elective"]:
            if row["courses"][0] == "TE":
                te_count += row["number_of_courses"]
            elif row["courses"][0] == "CSE":
                cse_count += row["number_of_courses"]
            else:
                ce_count += row["number_of_courses"]

        elif row["number_of_courses"] == 1:
            res['mandatory_courses'] += courses
        else:
            spec_req = {
                "requirement_type": "CHOOSE_{}_OF_{}".format(row["number_of_courses"], len(row["courses"])),
                "required_count": row["number_of_courses"],
                "courses_to_choose_from": courses,
            }
            res['special_requirements'].append(spec_req)

    res["elective_requirements"].append({
                "requirement_type": "TE",
                "required_count": te_count,
    })

    res["elective_requirements"].append({
                "requirement_type": "CSE",
                "required_count": cse_count,
    })

    res["elective_requirements"].append({
                "requirement_type": "Communication Elective",
                "required_count": ce_count,
            })

    # print(res)
            


# get_all_degrees(db)
get_options_reqs("Nanotechnology Engineering", db)
# get_degree_reqs("nanotechnology_engineering", db)