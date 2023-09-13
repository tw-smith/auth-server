from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password_hash: str


class User(UserBase):
    id: int
    verified: bool

    class Config:
        orm_mode = True