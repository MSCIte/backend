import sqlite3

import models
from database import SessionLocal
from sqlalchemy.orm import Session
    
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
            course_name = row[3]
            description = row[4]
            requirements_description = row[5]
            # parsed_requirements = requirements_dict.get(requirements_description, '')
            course = models.Course(course_code=course_code, course_name=course_name, description=description)
            db.add(course)
            if i % 1000 == 0:
                db.commit()
                print("committed ", str(i), " entries to the db")

db = SessionLocal() 
add_data_to_db(db)

