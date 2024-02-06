import csv
import os
import re
from pathlib import Path
from db.database import SessionLocal
from db.models import EngineeringDisciplineModel

program_names = {
    "AE": "architectual_engineering",
    "ELE": "electrical_engineering",
    "CHE": "chemical_engineering",
    "ENVE": "environmental_engineering",
    "COMPE": "computer_engineering",
    "CIVE": "civil_engineering",
    "ARCHPPENG": "architecture",
    "GEOE": "geological_engineering",
    "SE": "software_engineering",
    "SYDE": "systems_design_engineering",
    "MGTE": "management_engineering",
    "NE": "nanotechnology_engineering",
    "MECTR": "mechatronics_engineering",
    "ME": "mechanical_engineering",
    "BIOMEDE": "biomedical_engineering"
}

link_map = {
   "nanotechnology_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Nanotechnology-Engineering",
   "geological_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Geological-Engineering",
   "environmental_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Environmental-Engineering",
   "biomedical_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Biomedical-Engineering",
   "electrical_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Electrical-Engineering",
   "architectual_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Architectural-Engineering",
   "systems_design_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Systems-Design-Engineering",
   "management_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Management-Engineering",
   "mechatronics_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Mechatronics-Engineering",
   "software_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Software-Engineering",
   "civil_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Civil-Engineering",
   "mechanical_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Mechanical-Engineering",
   "computer_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Computer-Engineering",
   "chemical_engineering" : "https://ugradcalendar.uwaterloo.ca/page/ENG-Chemical-Engineering",
   "architecture": "https://ugradcalendar.uwaterloo.ca/page/ENG-Honours-Bachelor-of-Architectural-Studies",
}

db = SessionLocal()

class EngineeringDiscipline:
    def __init__(self):
        self.eng_id = ""
        self.plan = {}
        self.lists = {}
        
    pass


def get_files(db):
    root_dir = "plan_data"
    for path, folders, files in os.walk(root_dir):
        if path.endswith("degree_requirements"):
            for file in files:
                file_name = path + "\\" + file
                parse_csv(db, file_name)


def write_to_db(db, plans, lists, program_name, year):
    # pass
    for term, plan in plans.items():
        if "courses" in plan:
            for course in plan["courses"]:
                entry = EngineeringDisciplineModel(
                                discipline_name=program_name, 
                                course_codes=course, 
                                number_of_courses=1,
                                link=link_map[program_name],
                                year=year,
                                term=term
                            )
                db.add(entry)
        if "lists" in plan:
            for list in plan["lists"]:
                count = lists[list]["count"]
                if count != 0:
                    if "courses" in lists[list]:
                        courses = lists[list]["courses"]
                        print(courses)
                        entry = EngineeringDisciplineModel(
                                        discipline_name=program_name, 
                                        course_codes=", ".join(courses), 
                                        number_of_courses=count,
                                        link=link_map[program_name],
                                        year=year,
                                        term=term
                                    )
                        db.add(entry)
    db.commit()


def flatten_lists(lists):
    for list in lists.values():
        if "lists" in list:
            for sublist in list["lists"]:
                print(list)
                if sublist in lists and "courses" in lists[sublist]:
                    list["courses"] = list.get("courses", []) + lists[sublist]["courses"]
    return lists


def parse_csv(db, file):
    program_shorthand = re.search(r'[A-Z]+', file).group()
    year = re.search(r'\d+', file).group()
    program_name = program_names[program_shorthand]

    plan = {}
    lists = {}

    discipline = EngineeringDiscipline()
    
    with open(file) as file:
        reader_obj = csv.reader(file) 
        for row in reader_obj:
            type = row[0] if row[0] else type
            name = row[1] if row[1] else name
            calendar = row[2] if row[2] else calendar
            term = row[3] if row[3] else term
            category = row[4] if row[4] else category
            course_ref = row[5]

            if type == "plan":
                if not term in plan:
                    plan[term] = {}
                if category == "list":
                    if not "lists" in plan[term]:
                        plan[term]["lists"] = set()
                    plan[term]["lists"].add(course_ref)

                    if not course_ref in lists:
                        lists[course_ref] = {"count": 1}
                    else:
                        lists[course_ref]["count"] += 1
                else:
                    if not "courses" in plan[term]:
                        plan[term]["courses"] = [category + course_ref]
                    else:
                        plan[term]["courses"].append(category + course_ref)

            elif type == "list":
                if not name in lists:
                    lists[name] = {"count": 0}
                
                if category == "list":
                    if not "lists" in lists[name]:
                        lists[name]["lists"] = [course_ref]
                    else:
                        lists[name]["lists"].append(course_ref)
                else:
                    if not "courses" in lists[name]:
                        lists[name]["courses"] = [category + course_ref]
                    else:
                        lists[name]["courses"].append(category + course_ref) 
        # print(plan)
        lists = flatten_lists(lists)
        # print(lists)
    write_to_db(db, plan, lists, program_name, year)    



                

            
# ECE 
# {
#     "1A": 
#         {
#             "courses": ["MSCI100", "MSCI123"],
#             "lists": ["mgte_te", "mgte_te"]
#         }
    
# }

# {
#     "eng_cseA":  
#         {
#             "courses": ["MSCI100", "MSCI123"],
#             "lists": ["mgte_teOther"]
#             "count": 2
#         }
# }

            

get_files(db)