from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import requests
import json
from dotenv import load_dotenv

from starlette.responses import JSONResponse

from src.database.database import Database
from src.schemas.schemas import User, CreateUser, BadResponse, GoodResponse, VerifyRequest, VacancyId
from src.security.JWT import check_access_jwt, check_refresh_jwt, create_jwt
from src.utils.utils import generate_verify_code, send_register_email, get_hash, validate_password

app = FastAPI()
print('start')

load_dotenv()

path = 'localhost'
if 'MY_PATH' in os.environ:
    path = os.environ["MY_PATH"]

URL = os.getenv('DB_URL')
print(URL)
database = Database(URL)


@app.post("/auth/login")
def login(user: User):
    user_db = database.get_user(user.login)
    if user_db is not None:
        if validate_password(user.password, user_db.password):
            access = create_jwt(user_db.id, user_db.login)
            refresh = create_jwt(user_db.id, user_db.login, 14*24*60)
            content = {
                'login': user_db.login,
                'email': user_db.email,
                'verify': True,
                'resultCode': 1000
            }
            response = add_cookie(content, refresh, access)
            return response
        return BadResponse(2)
    return BadResponse(1)


@app.post("/auth/registration")
def register(user: CreateUser):
    if database.get_user(user.login) is not None:
        return BadResponse(1)
    elif not database.check_email(user.email):
        return BadResponse(2)
    else:
        verifyCode = generate_verify_code()
        result = send_register_email(message=verifyCode, receiver=user.email)
        if result == 0:
            database.create_user(login=user.login, email=user.email, password=user.password)
            hashcode = get_hash(str(verifyCode) + user.email)
            return {
                'hash': hashcode,
                'resultCode': 100
            }
        else:
            return BadResponse(3)


@app.post("/auth/registration/verify")
def verify_registration(request: VerifyRequest):
    hashcode = get_hash(str(request.code) + request.email)
    a1 = get_hash(str(request.code) + request.email)
    if hashcode == request.hashcode:
        database.verify_email(request.email)
        return GoodResponse(101)
    else:
        return BadResponse(4)


@app.get('/auth')
def auth(user_by_access: dict = Depends(check_access_jwt),
         user_by_refresh: dict = Depends(check_refresh_jwt)):
    if user_by_access:
        user = database.get_user(user_by_access['login'])
        if not user:
            return BadResponse(5)
        content = {
            "login": user.login,
            "email": user.email,
            "verify": user.verify,
        }
        return content
    elif user_by_refresh:
        user = database.get_user(user_by_refresh['login'])
        content = {
            "login": user.login,
            "email": user.email,
            "verify": user.verify,
        }
        response = add_cookie(content, create_jwt(user.id, user.login, 14*24*60), create_jwt(user.id, user.login))
        return response
    else:
        return BadResponse(5)


@app.delete('/auth/logout')
def logout():
    response = add_cookie({"resultCode": 0}, "", "")
    return response


@app.get("/vacancies/search")
def vacancies_search(request: Request, user: dict = Depends(check_access_jwt)):
    query_params = request.query_params
    path = 'https://api.hh.ru/vacancies?'
    for key in query_params:
        if query_params[key] is not None and query_params[key] != "":
            path += f'&{key}={query_params[key]}'
    r = requests.get(path)
    response = json.loads(r.text)

    vacancies = []
    if user is not None:
        vacancies = database.get_favorite_vacancies_id(user['login'])
        for i in range(0, len(vacancies)):
            vacancies[i] = vacancies[i][0]

    for i in response['items']:
        i['isFavorite'] = False
        if int(i['id']) in vacancies:
            i['isFavorite'] = True
        employer_id = None
        if 'id' in i['employer']:
            employer_id = i['employer']['id']
            database.create_employer(i['employer']['id'], i['employer']['name'])
        database.create_schedule(i['schedule']['id'], i['schedule']['name'])
        database.create_experience(i['experience']['id'], i['experience']['name'])
        database.create_area(i['area']['id'], i['area']['name'])
        salary_from = None if i['salary'] is None else i['salary']['to']
        salary_to = None if i['salary'] is None else i['salary']['from']
        database.create_short_vacancy(id=i['id'], name=i['name'], salary_from=salary_from,
                                      salary_to=salary_to, employer=employer_id,
                                      experience=i['experience']['id'],
                                      schedule=i['schedule']['id'], area=i['area']['id'])
    return response


@app.get("/vacancies")
def get_vacancies(id: int):
    r = requests.get(f"https://api.hh.ru/vacancies/{id}")
    vacancy = json.loads(r.text)
    database.create_employment(id=vacancy['employment']['id'], name=vacancy['employment']['name'])
    database.create_vacancy_descr(id=vacancy['id'], description=vacancy['description'],
                                  alternate_url=vacancy['alternate_url'], employment=vacancy['employment']['id'])
    for skill in vacancy['key_skills']:
        database.create_skill(name=skill['name'], vacancy_id=vacancy['id'])
    return vacancy


@app.put('/vacancies/addFavorite')
def add_favorite_vacancy(vacancy: VacancyId, user_by_access: dict = Depends(check_access_jwt)):
    if user_by_access is not None:
        database.add_favorite_vacancy(user_login=user_by_access['login'], vacancy_id=vacancy.vacancy_id)
        return GoodResponse(103)
    return BadResponse(6)


@app.put('/vacancies/deleteFavorite')
def delete_favorite_vacancy(vacancy: VacancyId, user_by_access: dict = Depends(check_access_jwt)):
    if user_by_access is not None:
        database.delete_favorite_vacancy(user_by_access['login'], vacancy.vacancy_id)
        return GoodResponse(103)
    else:
        return BadResponse(6)


@app.get('/vacancies/favorite')
def get_favorite_vacancies(user_by_access: dict = Depends(check_access_jwt)):
    if user_by_access is not None:
        vacancies = database.get_favorite_vacancies(user_by_access['login'])
        vacancies_response = []
        for pair, vacancy, area, employer, schedule, experience in vacancies:
            experience = experience.to_schema()
            schedule = schedule.to_schema()
            area = area.to_schema()
            employer = employer.to_schema()
            vacancy = vacancy.to_schema(experience, schedule, area, employer, True)
            vacancies_response.append(vacancy)
        response = {
            'items': vacancies_response,
            'found': len(vacancies_response),
            'resultCode': 103
        }
        return response
    return BadResponse(6)


def add_cookie(content, refresh, access):
    response = JSONResponse(content=content)
    response.set_cookie(key="access_token", value=access)
    response.set_cookie(key="refresh_token", value=refresh)
    return response


origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app")
