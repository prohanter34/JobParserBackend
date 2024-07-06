from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import registry, Session

from src.database.models import AbstractModel, ScheduleModel, ExperienceModel, EmployerModel, VacancyModel, \
    VacancyDescription, EmploymentModel, AreasModel, SkillsModel, UserModel, FavoriteVacancy
from src.utils.utils import hash_password


class Database:

    def __init__(self, URL):
        self.URL = URL
        self.engine = create_engine(self.URL, echo=False)
        self.mapped_registry = registry()
        self.session = Session(self.engine)
        with self.session.begin():
            AbstractModel.metadata.create_all(self.engine)

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()

    def create_user(self, login: str, password: str, email: str):
        res = self.session.execute(select(UserModel.login).where(UserModel.login == login))
        user = res.scalar()
        if user is not None:
            return False
        else:
            res = self.session.execute(select(UserModel.id).order_by(UserModel.id.desc()))
            id = res.scalar()
            print(id)
            if id:
                user = UserModel(id=(id + 1), login=login, email=email, password=hash_password(password).hex(),
                                 verify=False)
            else:
                user = UserModel(id=1, login=login, email=email, password=hash_password(password).hex(), verify=False)
            self.add(user)

    def check_email(self, email):
        res = self.session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar()
        if not user:
            return True
        else:
            return False

    def verify_email(self, email):
        res = self.session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar()
        user.verify = True
        self.session.commit()

    def get_user(self, login):
        res = self.session.execute(select(UserModel).where(UserModel.login == login))
        user = res.scalar()
        return user

    def add_favorite_vacancy(self, user_login: str, vacancy_id: int):
        res = self.session.execute(select(FavoriteVacancy).where(
            FavoriteVacancy.user_login == user_login).where(FavoriteVacancy.vacancy_id == vacancy_id))
        pair = res.scalar()
        if pair is None:
            pair = FavoriteVacancy(user_login=user_login, vacancy_id=vacancy_id)
            self.add(pair)

    def delete_favorite_vacancy(self, user_login: str, vacancy_id: int):
        res = self.session.execute(select(FavoriteVacancy).where(
            FavoriteVacancy.user_login == user_login and FavoriteVacancy.vacancy_id == vacancy_id))
        pair = res.scalar()
        if pair is not None:
            self.session.execute(delete(FavoriteVacancy).where(
                FavoriteVacancy.user_login == user_login).where(FavoriteVacancy.vacancy_id == vacancy_id))
            self.session.commit()

    def get_favorite_vacancies_id(self, user_login):
        res = self.session.execute(select(FavoriteVacancy.vacancy_id).where(FavoriteVacancy.user_login == user_login))
        vacancies = list(res.fetchall())
        return vacancies

    def get_favorite_vacancies(self, user_login):
        res = self.session.query(FavoriteVacancy, VacancyModel, AreasModel, EmployerModel, ScheduleModel, ExperienceModel)\
            .join(VacancyModel, VacancyModel.id == FavoriteVacancy.vacancy_id)\
            .join(EmployerModel, VacancyModel.employer == EmployerModel.id)\
            .join(ScheduleModel, VacancyModel.schedule == ScheduleModel.id)\
            .join(AreasModel, VacancyModel.area == AreasModel.id)\
            .join(ExperienceModel, VacancyModel.experience == ExperienceModel.id)\
            .all()
        return res

    def create_schedule(self, id: str, name: str):
        res = self.session.execute(select(ScheduleModel.id).where(ScheduleModel.id == id))
        schedule = res.scalar()
        if not schedule:
            schedule = ScheduleModel(id=id, name=name)
            self.add(schedule)

    def create_area(self, id: int, name: str):
        res = self.session.execute(select(AreasModel.id).where(AreasModel.id == int(id)))
        area = res.scalar()
        if not area:
            area = AreasModel(id=id, name=name)
            self.add(area)

    def create_experience(self, id: str, name: str):
        res = self.session.execute(select(ExperienceModel.id).where(ExperienceModel.id == id))
        experience = res.scalar()
        if not experience:
            experience = ExperienceModel(id=id, name=name)
            self.add(experience)

    def create_employer(self, id: int, name: str):
        res = self.session.execute(select(EmployerModel.id).where(EmployerModel.id == int(id)))
        employer = res.scalar()
        if not employer:
            employer = EmployerModel(id=id, name=name)
            self.add(employer)

    def create_skill(self, name: str, vacancy_id: int):
        res = self.session.execute(select(SkillsModel.id).where(SkillsModel.vacancy == int(vacancy_id)))
        skills = res.scalar()
        if not skills:
            skill = SkillsModel(name=name, vacancy=vacancy_id)
            self.add(skill)

    def create_employment(self, id: str, name: str):
        res = self.session.execute(select(EmploymentModel.id).where(EmploymentModel.id == id))
        employment = res.scalar()
        if not employment:
            employer = EmploymentModel(id=id, name=name)
            self.add(employer)

    def create_short_vacancy(self, id: int, name: str, salary_from: int, salary_to: int,
                             employer: int, schedule: str, experience: str, area: int):
        res = self.session.execute(select(VacancyModel.id).where(VacancyModel.id == int(id)))
        vacancy = res.scalar()
        if not vacancy:
            vacancy = VacancyModel(id=id, name=name, salary_from=salary_from, salary_to=salary_to,
                                   employer=employer, schedule=schedule, experience=experience, area=area)
            self.add(vacancy)

    def create_vacancy_descr(self, id: int, description: str, alternate_url: str, employment: int):
        res = self.session.execute(select(VacancyDescription.id).where(VacancyDescription.id == int(id)))
        vacancy = res.scalar()
        if not vacancy:
            vacancy = VacancyDescription(id=id, description=description, alternate_url=alternate_url,
                                         employment=employment)
            self.add(vacancy)
