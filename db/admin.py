from sqladmin import ModelView

from .models import OptionsModel, CourseModel


class OptionsAdmin(ModelView, model=OptionsModel):
    column_list = [OptionsModel.id, OptionsModel.option_name]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Option"
    name_plural = "Options"
    icon = "fa-solid fa-cog"
    category = "accounts"


class CourseAdmin(ModelView, model=CourseModel):
    column_list = [CourseModel.id, CourseModel.course_name, CourseModel.course_code, CourseModel.credit,
                   CourseModel.location,
                   CourseModel.description, CourseModel.antirequisites, CourseModel.corequisites,
                   CourseModel.prerequisites]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Course"
    name_plural = "Courses"
    icon = "fa-solid fa-book"
    category = "courses"


# class CoursePrerequisitesAdmin(ModelView, model=course_prerequisites):
#     column_list = [course_prerequisites.  .id, course_prerequisites.course_id, course_prerequisites.prerequisite_id]
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#     name = "Course Prerequisite"
#     name_plural = "Course Prerequisites"
#     icon = "fa-solid fa-book"
#     category = "courses"
#
#
# class CourseCorequisitesAdmin(ModelView, model=course_corequisites):
#     column_list = [course_corequisites.id, course_corequisites.course_id, course_corequisites.corequisite_id]
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#     name = "Course Corequisite"
#     name_plural = "Course Corequisites"
#     icon = "fa-solid fa-book"
#     category = "courses"
#
#
# class CourseAntirequisitesAdmin(ModelView, model=course_antirequisites):
#     column_list = [course_antirequisites.id, course_antirequisites.course_id, course_antirequisites.antirequisite_id]
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True
#     name = "Course Antirequisite"
#     name_plural = "Course Antirequisites"
#     icon = "fa-solid fa-book"
#     category = "courses"


admin_views = [OptionsAdmin, CourseAdmin]
