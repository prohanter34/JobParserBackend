from pydantic import BaseModel


class User(BaseModel):
    login: str
    password: str


class CreateUser(BaseModel):
    login: str
    password: str
    email: str


class GoodResponse(BaseModel):

    resultCode: int = 0

    def __init__(self, code, **data):
        super().__init__(**data)
        self.resultCode = code


# 100 - verify email sends
# 101 - verify success
# 102 - refresh tokens, send request again
# 103 - operation success


class BadResponse(BaseModel):

    resultCode: int = 1

    def __init__(self, code, **data):
        super().__init__(**data)
        self.resultCode = code

# 1 - login is not in db or login already register
# 2 - uncorrected password or email already register
# 3 - bad email
# 4 - uncorrected verify code
# 5 - old refresh token
# 6 - old access token
# 66 - all bad
# 11 - need wait
# 10 - no money
# 12 - code does not exist


class VerifyRequest(BaseModel):
    code: int
    hashcode: str
    email: str


class SearchArgs(BaseModel):
    area: int | None
    employment: str | None
    schedule: str | None
    only_with_salary: bool | None
    salary: int | None


class VacancyId(BaseModel):
    vacancy_id: int


class ExperienceSchema(BaseModel):
    id: str
    name: str


class ScheduleSchema(BaseModel):
    id: str
    name: str


class EmployerSchema(BaseModel):
    id: int
    name: str


class AreaSchema(BaseModel):
    id: int
    name: str


class VacancySchema(BaseModel):
    id: int
    name: str
    isFavorite: bool
    salary_from: int | None
    salary_to: int | None
    area: AreaSchema | None
    employer: EmployerSchema | None
    schedule: ScheduleSchema | None
    experience: ExperienceSchema | None
