from datetime import datetime

from pydantic import BaseModel


class ORMResponse(BaseModel):
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(ORMResponse):
    id: int
    username: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int


class PasswordCreate(BaseModel):
    title: str
    url: str
    login: str
    password: str


class PasswordResponse(ORMResponse):
    id: int
    title: str
    url: str
    login: str
    password: str
    created_at: datetime
    user_id: int
    user: UserResponse
