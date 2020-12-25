from pydantic import BaseModel


class Auth(BaseModel):
    email: str
    password: str


class MakeFollower(BaseModel):
    user_id: int
    subject_id: int


class Registration(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    birthday: int
    is_teacher: bool


class Lesson(BaseModel):
    user_id: int
    title: str
    description: str
    date: int
    check_file: bytes


class Subject(BaseModel):
    user_id: int
    title: str
    type_checking: str


class Mark(BaseModel):
    user_id: int
    lesson_id: int
    file: bytes


class Photo(BaseModel):
    user_id: int
    photo: bytes
