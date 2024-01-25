from fastapi_camelcase import CamelModel


class CourseSchema(CamelModel):
    course_code: str
    course_name: str
    credit: int
    description: str
    location: str

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


class CoursesTakenBody(CamelModel):
    course_codes_taken: list[str]

    class Config:
        from_attributes = True


class RequirementsResults(CamelModel):
    result: bool
    message: str

    class Config:
        from_attributes = True
