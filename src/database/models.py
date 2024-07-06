from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.schemas.schemas import VacancySchema, ExperienceSchema, ScheduleSchema, AreaSchema, EmployerSchema


class AbstractModel(DeclarativeBase):
    pass


class UserModel(AbstractModel):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=False)
    login: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    verify: Mapped[bool] = mapped_column()


class FavoriteVacancy(AbstractModel):
    __tablename__ = 'favorite_vacancy'
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id'), primary_key=True)
    user_login: Mapped[int] = mapped_column(ForeignKey('users.login'), primary_key=True)


class SkillsModel(AbstractModel):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    vacancy: Mapped[int] = mapped_column(ForeignKey('vacancy_description.id'))


class ExperienceModel(AbstractModel):
    __tablename__ = 'experience'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def to_schema(self):
        return ExperienceSchema(id=self.id, name=self.name)


class EmploymentModel(AbstractModel):
    __tablename__ = 'employment'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


class AreasModel(AbstractModel):
    __tablename__ = 'areas'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def to_schema(self):
        return AreaSchema(id=self.id, name=self.name)


class ScheduleModel(AbstractModel):
    __tablename__ = 'schedule'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def to_schema(self):
        return ScheduleSchema(id=self.id, name=self.name)


class EmployerModel(AbstractModel):
    __tablename__ = 'employer'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    def to_schema(self):
        return EmployerSchema(id=self.id, name=self.name)


class VacancyModel(AbstractModel):
    __tablename__ = 'vacancy'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    salary_from: Mapped[int | None] = mapped_column(nullable=True)
    salary_to: Mapped[int | None] = mapped_column(nullable=True)
    area: Mapped[int] = mapped_column(ForeignKey('areas.id'), nullable=True)
    employer: Mapped[int] = mapped_column(ForeignKey('employer.id'), nullable=True)
    schedule: Mapped[str] = mapped_column(ForeignKey('schedule.id'), nullable=True)
    experience: Mapped[str] = mapped_column('experience.id', nullable=True)

    def to_schema(
            self, experience: ExperienceSchema, schedule: ScheduleSchema,
            area: AreaSchema, employer: EmployerSchema, is_favorite: bool
    ):
        return VacancySchema(id=self.id, name=self.name, salary_from=self.salary_from, salary_to=self.salary_to,
                      area=area, experience=experience, schedule=schedule, employer=employer, isFavorite=is_favorite)


class VacancyDescription(AbstractModel):
    __tablename__ = 'vacancy_description'
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()
    alternate_url: Mapped[str] = mapped_column()
    employment: Mapped[str] = mapped_column(ForeignKey('employment.id'))
