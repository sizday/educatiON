from datetime import datetime
from time import mktime
import asyncio
from gino import Gino
from sqlalchemy import sql, Column, Integer, String, Sequence, Boolean, ForeignKey, Binary
from preload.config import db_pass, db_user, host, db_name
from database.models import SubjectByUser
# from testing.pictures import compare_picture
from testing.test import open_file
from testing.program import compare_files

db = Gino()


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_seq'), primary_key=True)
    name = Column(String(200))
    surname = Column(String(200))
    email = Column(String(200))
    password = Column(String(200))
    birthday = Column(Integer)
    avatar = Column(Binary, default=None)
    is_teacher = Column(Boolean)
    query: sql.Select


class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = Column(Integer, Sequence('lesson_seq'), primary_key=True)
    subject = Column(ForeignKey('subject.id'))
    title = Column(String(200))
    description = Column(String(200))
    date = Column(Integer)
    check_file = Column(Binary)
    query: sql.Select


class Subject(db.Model):
    __tablename__ = 'subject'
    id = Column(Integer, Sequence('subject_seq'), primary_key=True)
    title = Column(String(200))
    type_checking = Column(String(200))
    user = Column(ForeignKey('user.id'))
    query: sql.Select


class Follower(db.Model):
    __tablename__ = 'follower'
    id = Column(Integer, Sequence('follower.seq'), primary_key=True)
    user = Column(ForeignKey('user.id'))
    subject = Column(ForeignKey('subject.id'))


class Evaluation(db.Model):
    __tablename__ = 'evaluation'
    id = Column(Integer, Sequence('evaluation.seq'), primary_key=True)
    user = Column(ForeignKey('user.id'))
    mark = Column(Integer, default=None)
    lesson = Column(ForeignKey('lesson.id'))
    query: sql.Select


class DBCommands:

    # profile
    async def get_user(self, user_id) -> User:
        user = await User.query.where(User.id == user_id).gino.first()
        return user

    async def get_subject_by_user(self, user_id) -> SubjectByUser:
        follower = await Follower.query.where(Follower.user == user_id).gino.first()
        subject = await Subject.query.where(Subject.id == follower.subject).gino.first()
        evaluations = await Evaluation.query.where(Evaluation.user == user_id).gino.all()
        count_pass_less = count_less = 0
        for num, evaluation in enumerate(evaluations):
            if evaluation.mark is not None:
                count_pass_less += 1
            count_less += 1
        subject_by_user = SubjectByUser(subject_title=subject.title,
                                        count_passed_lessons=count_pass_less,
                                        count_lessons=count_less)
        return subject_by_user

    async def update_photo(self, user_id, photo):
        current_user = await self.get_user(user_id)
        await current_user.update(avatar=photo).apply()

    # registration
    async def create_user(self, name, surname, email, password, birthday, is_teacher=False):
        new_user = User()
        new_user.name = name
        new_user.surname = surname
        new_user.email = email
        new_user.password = password
        new_user.birthday = birthday
        new_user.is_teacher = is_teacher
        await new_user.create()
        return new_user

    # authorisation
    async def authorisation(self, email, password):
        user = await User.query.where((User.email == email) & (User.password == password)).gino.first()
        if user:
            return user

    # user
    async def get_lessons_by_user(self, user_id):
        follower = await Follower.query.where(Follower.user == user_id).gino.first()
        if follower is not None:
            subject = await Subject.query.where(Subject.id == follower.subject).gino.first()
            lessons = await Lesson.query.where(Lesson.subject == subject.id).gino.all()
            return lessons

    async def get_evaluations_by_user(self, user_id):
        evaluation = await Evaluation.query.where(Evaluation.user == user_id).gino.all()
        return evaluation

    # teacher
    async def is_teacher(self, user_id):
        user = await self.get_user(user_id)
        return user.is_teacher

    async def get_lesson_by_id(self, lesson_id) -> User:
        lesson = await Lesson.query.where(Lesson.id == lesson_id).gino.first()
        return lesson

    async def get_subject_by_teacher(self, user_id):
        if await self.is_teacher(user_id):
            subject = await Subject.query.where(Subject.user == user_id).gino.first()
            return subject

    async def get_lessons_by_teacher(self, user_id):
        if await self.is_teacher(user_id):
            subject = await self.get_subject_by_teacher(user_id)
            lessons = await Lesson.query.where(Lesson.subject == subject.id).gino.all()
            return lessons

    async def create_lesson(self, user_id, title, description, date, check_file=None):
        if await self.is_teacher(user_id):
            subject = await self.get_subject_by_teacher(user_id)
            new_lesson = Lesson()
            new_lesson.subject = subject.id
            new_lesson.title = title
            new_lesson.description = description
            new_lesson.date = date
            new_lesson.check_file = check_file
            await new_lesson.create()
            followers = await Follower.query.where(Follower.subject == subject.id).gino.all()
            for num, follower in enumerate(followers):
                new_evaluation = Evaluation(user=follower.user, lesson=new_lesson.id)
                await new_evaluation.create()

    async def create_subject(self, user_id, title, type_checking):
        if await self.is_teacher(user_id):
            new_subject = Subject()
            new_subject.user = user_id
            new_subject.title = title
            new_subject.type_checking = type_checking
            await new_subject.create()

    async def get_evaluations_by_teacher(self, user_id):
        if await self.is_teacher(user_id):
            lessons = await self.get_lessons_by_teacher(user_id)
            evaluation = [await Evaluation.query.where(Evaluation.lesson == lesson.id).gino.all()
                          for num, lesson in enumerate(lessons)]
            return evaluation

    async def make_follower(self, user_id, subject_id):
        new_follower = Follower(user=user_id, subject=subject_id)
        await new_follower.create()
        lessons = await Lesson.query.where(Lesson.subject == subject_id).gino.all()
        for num, lesson in enumerate(lessons):
            new_evaluation = Evaluation(user=user_id, lesson=lesson.id)
            await new_evaluation.create()

    # testing
    async def update_mark(self, user_id, lesson_id, file):
        lesson = await Lesson.query.where(Lesson.id == lesson_id).gino.first()
        subject = await Subject.query.where(Subject.id == lesson.subject).gino.first()
        if subject.type_checking == 'py':
            mark = compare_files(lesson.check_file, file)
        # elif subject.type_checking == 'img':
            # mark = compare_picture(lesson.check_file, file)
        elif subject.type_checking == 'test':
            mark = open_file(lesson.check_file, file)
        else:
            mark = None
        evaluation = await Evaluation.query.where((Evaluation.user == user_id) & (Evaluation.lesson == lesson_id)).gino.first()
        await evaluation.update(mark=mark).apply()
        return mark


async def create_db():
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    # await db.gino.drop_all()
    await db.gino.create_all()
    dbc = DBCommands()
    """
    await dbc.create_user('Denis', 'Sizov', 'dsizov1999@mail.ru', 'dionis0799', mktime(datetime(1999, 7, 19).timetuple()),
                          is_teacher=True)
    await dbc.create_user('Andrey', 'Kim', 'kummu-97@mail.ru', 'andrey', mktime(datetime(1997, 7, 8).timetuple()),
                          is_teacher=True)
    await dbc.create_user('Лаптева', 'Надежда', 'test1@mail.ru', 'qwerty', mktime(datetime(2010, 1, 1).timetuple()))
    await dbc.create_user('Дружинин', 'Владимир', 'test2@mail.ru', 'qwerty', mktime(datetime(2010, 1, 1).timetuple()))
    await dbc.create_user('Анисимов', 'Сергей', 'test3@mail.ru', 'qwerty', mktime(datetime(2010, 1, 1).timetuple()))
    await dbc.create_subject(1, 'Python', 'test')
    # await dbc.create_subject(2, 'UI/UX', 'img')
    await dbc.make_follower(3, 1)
    await dbc.make_follower(4, 1)
    await dbc.make_follower(5, 1)
    file_text = open('../files/test_original.txt', 'rb').read()
    file_py = open('../files/program_original.txt', 'rb').read()
    await dbc.create_lesson(1, 'Loop FOR', 'Learning cycle with counter', mktime(datetime(2020, 12, 1).timetuple()), file_text)
    await dbc.create_lesson(1, 'Loop WHILE', 'Learning cycle with condition', mktime(datetime(2020, 12, 9).timetuple()), file_text)
    await dbc.create_lesson(1, 'IF ELSE', 'Conditional operations', mktime(datetime(2020, 12, 15).timetuple()), file_text)
    await dbc.create_lesson(1, 'Lambda-function', 'Learning functions using a variable lambda', mktime(datetime(2020, 12, 15).timetuple()), file_text)
    """

asyncio.get_event_loop().run_until_complete(create_db())
