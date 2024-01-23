from fastapi_camelcase import CamelModel


class Course(CamelModel):
    course_code: str
    course_name: str
    credit: int
    description: str
    location: str

    class Config:
        from_attributes = True


class Options(CamelModel):
    option_name: str

    class Config:
        from_attributes = True


class EngineeringDiscipline(CamelModel):
    discipline_name: str

    class Config:
        from_attributes = True


class Prerequisite(CamelModel): 
    logic: str
    courses: str
    min_level: str

    class Config:
        from_attributes = True



class CoursesTakenBody(CamelModel):
    course_codes_taken: list[str]

    class Config:
        from_attributes = True