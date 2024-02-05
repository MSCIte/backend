import csv
import os
import re
from pathlib import Path

course_names = {
    "AE": "architecture",
    "ELE": "electrical_engineering",
    "CHE": "chemical_engineering",
    "ENVE": "environmental_engineering",
    "COMPE": "computer_engineering",
    "CIVE": "civil_engineering",
    "ARCHPPENG": "architectual_engineering",
    "GEOE": "geological_engineering",
    "SE": "software_engineering",
    "SYDE": "systems_design_engineering",
    "MGTE": "maangement_sciences_and_engineering",
    "NE": "nanotechnology_engineering",
    "MECTR": "mechatronics_engineering",
    "ME": "mechanical_engineering",
    "BIOMEDE": "biomedical_engineering"
}

class EngineeringDiscipline:
    def __init__(self):
        self.eng_id = ""
        self.plan = {}
        self.lists = {}
        
    pass

def get_files():
    root_dir = "plan_data"
    for path, folders, files in os.walk(root_dir):
        if path.endswith("degree_requirements"):
            for file in files:
                file_name = path + "\\" + file
                parse_csv(file_name)


def parse_csv(file):
    program_shorthand = re.search(r'[A-Z]+', file).group()
    year = re.search(r'\d+', file).group()

    plan = {}
    lists = {}

    discipline = EngineeringDiscipline()
    
    with open(file) as file:
        reader_obj = csv.reader(file) 
        for row in reader_obj:
            type = row[0] if row[0] else type
            name = row[1] if row[1] else name
            calendar = row[2] if row[2] else calendar
            term = row[3] if row[0] else term
            category = row[4] if row[4] else category
            course_ref = row[5] if row[5] else course_ref
            
            if name in course_names:
                discipline.eng_id = name

            if type == "plan":
                if not term in plan:
                    plan[term] = {}
                if category == "list":
                    if not "lists" in plan[term]:
                        plan[term]["lists"] = [course_ref]
                    else:
                        plan[term]["lists"].append(course_ref)
                else:
                    if not "courses" in plan[term]:
                        plan[term]["courses"] = [category + course_ref]
                    else:
                        plan[term]["courses"].append(category + course_ref)
        print(plan)
            
            # elif type == "list":
        
    discipline.plan = plan       

                

            

# {
#     "1A": 
#         {
#             "courses": ["MSCI100", "MSCI123"],
#             "lists": ["eng_cseA", ]
#         }
    
# }

# {
#     "eng_cseA":  
#         {
#             "courses": ["MSCI100", "MSCI123"],
#             "lists": ["mgte_teOther"]
#         }


# }

            

get_files()