from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password_hash: str


class User(UserBase):
    id: int
    public_id: str
    verified: bool
    password_locked: bool
    created_at: int

    class Config:
        orm_mode = True