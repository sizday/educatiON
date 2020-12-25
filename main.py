from fastapi import FastAPI
from preload.config import db_pass, db_user, host, db_name
from database.database import db, DBCommands
from database.models import Auth, MakeFollower, Registration, Lesson, Subject, Mark, Photo

app = FastAPI()


@app.get("/user/profile/{user_id}")
async def get_user(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    user = await dbc.get_user(user_id)
    return user


@app.get("/user/lesson/{user_id}")
async def get_lessons_by_user(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    lessons = await dbc.get_lessons_by_user(user_id)
    return lessons


@app.get("/user/evaluation/{user_id}")
async def get_evaluations_by_user(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    evaluations = await dbc.get_evaluations_by_user(user_id)
    return evaluations


@app.get("/teacher/evaluation/{user_id}")
async def get_evaluations_by_teacher(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    evaluations = await dbc.get_evaluations_by_teacher(user_id)
    return evaluations


@app.get("/teacher/lesson/{user_id}")
async def get_lessons_by_teacher(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    lessons = await dbc.get_lessons_by_teacher(user_id)
    return lessons


@app.get("/teacher/subject/{user_id}")
async def get_subject_by_teacher(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    subject = await dbc.get_subject_by_teacher(user_id)
    return subject


@app.get("/teacher/is_teacher/{user_id}")
async def is_teacher(user_id: int):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    result = await dbc.is_teacher(user_id)
    return result


@app.get("/user/authorisation/")
async def authorisation(params: Auth):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    result = await dbc.authorisation(params.email, params.password)
    return result


@app.post("/user/make_follower/")
async def make_follower(params: MakeFollower):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.make_follower(params.user_id, params.subject_id)


@app.post("/user/create/")
async def create_user(params: Registration):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.create_user(params.name, params.surname, params.email,
                          params.password, params.birthday, params.is_teacher)


@app.post("/teacher/create/lesson")
async def create_lesson(params: Lesson):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.create_lesson(params.user_id, params.title, params.description,
                            params.date, params.check_file)


@app.post("/teacher/create/subject")
async def create_subject(params: Subject):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.create_subject(params.user_id, params.title, params.type_checking)


@app.post("/user/update/mark")
async def update_mark(params: Mark):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.update_mark(params.user_id, params.lesson_id, params.file)


@app.post("/user/update/photo")
async def update_photo(params: Photo):
    dbc = DBCommands()
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/{db_name}')
    await dbc.update_photo(params.user_id, params.photo)
