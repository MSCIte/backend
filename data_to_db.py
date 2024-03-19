import sqlite3

from db.models import CourseModel, PrerequisiteModel, AntirequisiteModel, EngineeringDisciplineModel
from db.database import SessionLocal
from sqlalchemy.orm import Session
from course_parsing.requirements import load_prereqs, load_antireqs
import re


def add_courses_to_db(db: Session):
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
            # print("lmao", True if db.query(CourseModel).where(CourseModel.course_code == course_code) else False,  db.query(CourseModel).where(CourseModel.course_code == course_code))
            if  db.query(CourseModel).where(CourseModel.course_code == course_code).first():
                print("skipped ", course_code, ". Already in db")
                continue
            course = CourseModel(course_code=course_code, course_name=course_name, description=description,
                                 requirements_description=requirements_description)
            db.add(course)
            db.flush()
            if requirements_description:
                if row[1][0] == '6' or row[1][0] == '7':
                    # ignoring grad degree courses for now
                    continue

                index = requirements_description.find('Antireq: ')
                if index >= 0:
                    prereqs_string = requirements_description[0:index]
                    antireqs_string = requirements_description[index:]

                    parsed_antireqs = load_antireqs(antireqs_string)
                    antireq = AntirequisiteModel(course_id=course.id, courses=parsed_antireqs["courses"],
                                                 extra_info=parsed_antireqs["extra_info"])
                    # print(antireq.courses)
                    db.add(antireq)
                else:
                    prereqs_string = requirements_description

                parsed_prereqs = load_prereqs(prereqs_string)
                prereq = PrerequisiteModel(course_id=course.id, logic=parsed_prereqs['logic'],
                                           courses=parsed_prereqs['courses'])
                # print(prereq.courses)
                db.add(prereq)

            if i % 1000 == 0:
                db.commit()
                print("committed ", str(i), " entries to the db")
        # Commit everything else 
        db.commit()
        print("committed ", str(i), " entries to the db")


def add_degrees_to_db(db: Session):
    with sqlite3.connect('uwpath.db') as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT 
            program_name, 
            course_codes, 
            number_of_courses, 
            additional_requirements,
            link, 
            year 
            FROM requirements
            """
        )

        for row in cur:
            discipline_name = row[0]
            course_codes = row[1]
            number_of_courses = row[2]
            additional_requirements = row[3]
            link = row[4]
            year = row[5]
            discipline = EngineeringDisciplineModel(
                discipline_name=discipline_name,
                course_codes=course_codes,
                number_of_courses=number_of_courses,
                additional_requirements=additional_requirements,
                link=link,
                year=year
            )
            db.add(discipline)

        db.commit()


def term_to_prereq_table(db: Session):
    prereqs = db.query(PrerequisiteModel, CourseModel.course_code).join(CourseModel, PrerequisiteModel.course_id == CourseModel.id).all()
    print("finished querying from psql")
    for i, prereq in enumerate(prereqs):
        course_code_split = re.split(r'(?<=[A-Z])(?=\d)', prereq[1], 1)
        subject_code = course_code_split[0]
        catalog_number = course_code_split[1]
        print(subject_code, catalog_number)
        with sqlite3.connect('./data/db.sqlite') as con:
            cur = con.cursor()
            cur.execute(
                """
                WITH RankedCourses AS (
                SELECT
                    requirementsDescription,
                    ROW_NUMBER() OVER (PARTITION BY subjectCode, catalogNumber ORDER BY termCode DESC) AS rn
                FROM courses
                WHERE subjectCode = ? AND catalogNumber = ?
                )
                SELECT *
                FROM RankedCourses
                WHERE rn = 1;
                """,
                (subject_code, catalog_number)
            )

            for row in cur:
                requirements_description = row[0]
                matches = re.findall(r'\b(?:L|l)evel at least\b.*?(?:\.|$)', requirements_description)
                if matches:
                    match = matches[0]
                    terms = re.findall(r'\b\d+[A-Z]\b', match)
                    sorted_terms= sorted(terms, key=lambda x: (x[0], x[1]), reverse=True)
                    min_level = [sorted_terms[0], match]
                    print(min_level)
                    prereq[0].min_level = min_level
            if i % 500 == 0:
                db.commit()
    db.commit()             


db = SessionLocal()
# add_degrees_to_db(db)
# add_courses_to_db(db)
term_to_prereq_table(db)
