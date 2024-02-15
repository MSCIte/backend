from db.models import CourseModel, PrerequisiteModel
from db.database import SessionLocal


db = SessionLocal()


def remove_space_from_courses():
    # query all rows from CourseModel but just the course_code column
    courses = db.query(CourseModel.course_code).all()
    print(courses)
    for course in courses:
        # remove space from the course_code
        new_course_code = course[0].replace(" ", "")
        print("Old course code: ", course[0]), print("New course code: ", new_course_code)
        # update the course_code in the database
        db.query(CourseModel).where(CourseModel.course_code == course[0]).update({CourseModel.course_code: new_course_code})

    # commit the changes
    db.commit()


def remove_space_from_prereqs():
    courses = db.query(PrerequisiteModel).all()
    print(courses)
    for course in courses:
        courses_list = course.courses
        new_course_list = []
        for c in courses_list:
            # remove space from the course_code
            new_course_code = c.replace(" ", "")
            # update the course_code in the database
            new_course_list.append(new_course_code)
        db.query(PrerequisiteModel).where(PrerequisiteModel.course_id == course.course_id).update({PrerequisiteModel.courses: new_course_list})

    # commit the changes
    db.commit()

remove_space_from_prereqs()
# remove_space_from_courses()