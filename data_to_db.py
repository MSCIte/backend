import sqlite3

from db.models import Course, Prerequisite, Antirequisite
from db.database import SessionLocal
from sqlalchemy.orm import Session
from course_parsing.requirements import load_prereqs



def add_data_to_db(db: Session):
    with sqlite3.connect('./data/db.sqlite') as con:
        cur = con.cursor()
        cur.execute(
            """
            WITH RankedCourses AS (
            SELECT
                subjectCode,
                catalogNumber,
                termCode,
                title, 
                description, 
                requirementsDescription,
                ROW_NUMBER() OVER (PARTITION BY subjectCode, catalogNumber ORDER BY termCode DESC) AS rn
            FROM courses
            )
            SELECT *
            FROM RankedCourses
            WHERE rn = 1;
            """
        )

        for i, row in enumerate(cur):
            course_code = row[0] + row[1]
            if row[1][0] == '6' or row[1][0] == '7':
                # We hate grad students
                continue
            course_name = row[3]
            description = row[4]
            requirements_description = row[5]
            course = Course(course_code=course_code, course_name=course_name, description=description, requirements_description=requirements_description)
            if requirements_description:
                if i == 1903:
                    print("==LMAO",course_code)
                parsed_prereqs = load_prereqs(requirements_description)
                print(i, parsed_prereqs)
            prereq_courses = []
            antireq_courses = []
            # db.add(course)
            # if i % 1000 == 0:
            #     db.commit()
            #     print("committed ", str(i), " entries to the db")

            # prereq = Prereqs()
db = SessionLocal() 
add_data_to_db(db)

