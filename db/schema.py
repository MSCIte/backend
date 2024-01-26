from enum import Enum

from fastapi_camelcase import CamelModel


class CourseSchema(CamelModel):
    course_code: str
    course_name: str
    credit: int | None = -1000
    description: str = ''
    location: str | None = ''
    prerequisites: str | None = ''
    antirequisites: str | None = ''
    corequisites: str | None = ''


class ColorsEnum(str, Enum):
    red = "red"
    green = "green"
    orange = "orange"
    yellow = "yellow"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    indigo = "indigo"
    gray = "gray"


class TagSchema(CamelModel):
    code: str  # e.g. "te", "mand"
    color: ColorsEnum = ColorsEnum.red  # e.g. "red", "green"
    short_name: str  # e.g. "TE", "Mand."
    long_name: str  # e.g. "Technical Elective", "Mandatory"


class CourseWithTagsSchema(CourseSchema):
    tags: list[TagSchema] = []


class Config:
    from_attributes = True


class OptionsSchema(CamelModel):
    option_name: str
    course_codes: str
    number_of_courses: int
    additional_requirements: str
    link: str
    year: str

    class Config:
        from_attributes = True


class EngineeringDiscipline(CamelModel):
    discipline_name: str
    course_codes: list[str]
    number_of_courses: int
    credits_required: float
    additional_requirements: str
    link: str
    year: str

    class Config:
        from_attributes = True


class PrereqSchema(CamelModel):
    logic: str
    courses: str
    min_level: str

    class Config:
        from_attributes = True


class CoursesTakenIn(CamelModel):
    course_codes_taken: list[str]

    class Config:
        from_attributes = True


class RequirementsResults(CamelModel):
    result: bool
    message: str

    class Config:
        from_attributes = True
