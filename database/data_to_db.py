import sqlite3
import re
import os
import spacy
import csv
import json

import models
import schema 

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
#         elif re.findall('^[A-Z]+', split):
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

# Examples
# examples = [
#     "Actuarial Science Masters Students",
#     "Antireq: AE 121, BME 121, CS 115, 137, 138, 145, CIVE 121, ECE 150, ME 101, MSCI 121, PHYS 236, SYDE 121",
#     "Antireq: AFM 231/LS 283, ECE 290; (For Mathematics students only) BUS 231W, CIVE 491, ENVS 201, GENE 411, ME 401, MTHEL 100",
#     "Coreq: CHEM 120. Antireq: CHEM 121L",
#     "Pre/Co-req: ECE 650 or 750 Tpc 26, or instructor consent. Antireq: ECE 355, ECE 451, CS 445, CS 645, SE 463, ECE 452, CS 446, CS 646, SE 464",
#     "Prereq/coreq: ECE 650 or 750 Tpc 26 or instructor consent. Antireq: CS 447, 647, ECE 453, SE 465",
#     "Prereq: ((MATH 106 with a grade of at least 70% or MATH 136 or 146) and (MATH 135 with a grade of at least 60% or MATH 145)) or level at least 2A Software Engineering; Honours Mathematics students only. Antireq: CO 220, MATH 229, 249",
#     "Prereq: (CHEM 233 or 237), 360; Antireq: CHEM 482"
# ]

# Parse and print results
# for example in examples:
#     result = normalize_reqs_str(example)
#     print(result)
    

# def clean():
#     with sqlite3.connect('./data/db.sqlite') as con:
#         cur = con.cursor()
#         cur.execute('SELECT * FROM courses LIMIT 1000')
#         columns = [column[0] for column in cur.description]
#         for row in cur:
#             row_dict = dict(zip(columns, row))
#             req_desc = clean_requirements_description(row_dict.get('requirementsDescription', None))
#             print(row_dict.get('requirementsDescription', None))
#             print(req_desc)

# clean()
# clean_requirements_description("Prereq: AFM362, 363. Antireq: AFM 415 taken fall 2016. Coreq: yeet.")

def build_requirements_dict():
    requirements_dict = {}
    with open('./data/parsed_requirements.tsv','r') as tsv:
        for line in csv.reader(tsv, delimiter='\t'):
            requirements_dict[line[0]] = eval(line[1])
    return requirements_dict
    
def add_data_to_db():
    requirements_dict = build_requirements_dict()
    with sqlite3.connect('./data/db.sqlite') as con:
        cur = con.cursor()

        cur.execute(
            """
            SELECT subjectCode, catalogNumber, title, description, requirementsDescription
            FROM courses
            """
        )
        for row in cur:
            course_code = row[0] + row[1]
            course_name = row[2]
            description = row[3]
            requirements_description = row[4]
            course = models.Course(course_code=course_code, course_name=course_name, description=description)
            print(course)

add_data_to_db()