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
    slate = "slate"
    rose = "rose"


class TagSchema(CamelModel):
    code: str  # e.g. "te", "mand"
    color: ColorsEnum  # e.g. "red", "green"
    short_name: str  # e.g. "TE", "Mand."
    long_name: str  # e.g. "Technical Elective", "Mandatory"


class CourseWithTagsSchema(CourseSchema):
    tags: list[TagSchema] = []


class Config:
    from_attributes = True


class OptionRequirement(CamelModel):
    courses: list[str]
    number_of_courses: int
    name: str


class OptionsSchema(CamelModel):
    option_name: str
    requirements: list[OptionRequirement]

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


class CanTakeCourseQuery(CamelModel):
    course_code: str
    course_codes_taken: list[str]

    class Config:
        from_attributes = True


class CanTakeCourseBatch(CamelModel):
    can_take_course_codes: list[CanTakeCourseQuery]

    class Config:
        from_attributes = True


class DegreeMissingIn(CamelModel):
    course_codes_taken: list[str]
    year: str

    class Config:
        from_attributes = True


class RequirementsResult(CamelModel):
    result: bool
    message: str

    class Config:
        from_attributes = True


class RequirementsResults(CamelModel):
    results: list[RequirementsResult]

    class Config:
        from_attributes = True


class AdditionalReqCount(CamelModel):
    completed: str
    total: str
    tag: TagSchema


# class DegreeMissingReqs(CamelModel):
#     mandatory_courses: list[str]
#     number_of_mandatory_courses: int
#     additional_reqs: dict[str, AdditionalReqCount]

class DegreeMissingReqs(CamelModel):
    mandatory_courses: list[str]
    number_of_mandatory_courses: int
    additional_reqs: dict[str, AdditionalReqCount]
    tag: TagSchema


class DegreeRequirement(CamelModel):
    courses: list[str]
    number_of_courses: int


class DegreeReqs(CamelModel):
    mandatory_courses: list[str]
    additional_reqs: dict[str, DegreeRequirement]


class MissingList(CamelModel):
    list_name: str
    courses: dict[str, bool]
    total_course_to_complete: int
    tag: TagSchema


class MissingReqs(CamelModel):
    lists: list[MissingList]
