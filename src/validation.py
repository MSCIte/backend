import json
import re

from sqlalchemy.orm import Session

from course_parsing.ascii_translator import get_char
from db.database import SessionLocal
from db.models import CourseModel, PrerequisiteModel, AntirequisiteModel

db = SessionLocal()


def level_can_take(logic, course, taken_courses, i):
    if course.endswith("000"):
        print(logic.find(get_char(i)))
        new_string = ""
        for taken in taken_courses:
            course_start = re.match("[A-Z]+ [1-9]", taken).group(0)
            if course_start == course[:-3]:
                new_string += "True and "
        if new_string == "":
            logic = logic.replace(get_char(i) + " ", "False ")
        else:
            logic = logic.replace(get_char(i) + " ", new_string[:-5] + " ")
        print(logic)
    elif course in taken_courses:
        logic = logic.replace(get_char(i) + " ", "True ")
    else:
        logic = logic.replace(get_char(i) + " ", "False ")

    iter = re.finditer("len\\(tuple\\(filter\\(None,\\[ (?:True|False)((?: and True)+)", logic)
    for m in iter:
        start = m.start(0)
        end = m.end(0)
        logic = logic[:start] + logic[start:end].replace(" and", ",") + logic[end:]

    return logic


def can_take_course(db: Session, courses_taken: list[str], course: str):
    course_obj = db.query(CourseModel).where(CourseModel.course_code == course).first()
    prereqs = db.query(PrerequisiteModel).where(PrerequisiteModel.course_id == course_obj.id).first()
    antireqs = db.query(AntirequisiteModel).where(AntirequisiteModel.course_id == course_obj.id).first()
    if antireqs:
        antireq_courses = json.loads(antireqs.courses)
        for antireq in antireq_courses:
            if any((c in antireq) for c in courses_taken):
                return False, "The course has an antirequisite."

    prereq_logic = prereqs.logic
    prereq_courses = json.loads(prereqs.courses)
    for i in range(len(prereq_courses)):
        if prereq_courses[i][0] == "_":
            prereq_logic = level_can_take(prereq_logic, prereq_courses[i][1:], courses_taken, i)
        else:
            prereq_logic = level_can_take(prereq_logic, prereq_courses[i], courses_taken, i)

    try:
        if eval(prereq_logic):
            return True, ""
        else:
            return False, "Prerequisite or corequisite not met."
    except Exception as e:
        # EMAIL(course, self.prereq_courses, self.prereq_logic, list_of_courses_taken, current_term_courses, e)
        # Error Log
        # TODO: Prevent sending multiple emails with the same error in a short amount of time
        error_message = "Error Message: " + str(e) + "."
        error_message += "\n\ncan_take_course({}, {})".format(courses_taken, course)

        # error_message += "\n\nAntireqs: " + str(self.antireqs)
        # error_message += "\n\nPrereq Logic: " + str(self.prereq_logic)
        # error_message += "\n\nPrereq Courses: " + str(self.prereq_courses)
        # error_message += "\n\nCoreq Logic: " + str(self.coreq_logic)
        # error_message += "\n\nCoreq Courses: " + str(self.coreq_courses)
        # error_message += "\n\nOccurred at: " + str(datetime.now()) + " (UTC)"

        # msg = EmailMessage("Error in ValidationCheckAPI/CanTakeCourse",
        #                     error_message,
        #                     settings.EMAIL_HOST_USER,
        #                     [settings.EMAIL_HOST_USER])
        # msg.send()
        return


# print(can_take_course(db, ["LOL 1001", "CS 135"], "ACTSC127"))
