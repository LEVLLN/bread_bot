
from fastapi import Body, Query
from pydantic import BaseModel, EmailStr, Field


class TokenSchema(BaseModel):
    """
    Данные токена
    """

    access_token: str = Query(..., title="Токен")
    token_type: str = Query(..., title="Тип токена")


class TokenDataSchema(BaseModel):
    """
    Данные токена
    """

    username: str | None = None


class UserSchema(BaseModel):
    """
    Пользователь
    """

    username: str = Body(..., title="Логин")
    email: EmailStr = Body(..., title="Электронная почта")
    first_name: str | None = Body(None, title="Имя")
    surname: str | None = Body(None, title="Фамилия")

    class Config:
        orm_mode = True


class UserInfoSchema(UserSchema):
    """
    Пользователь
    """

    id: int = Query(..., title="ID")
    is_active: bool | None = Query(..., title="Активен")

    class Config:
        orm_mode = True


class UserCreateSchema(UserSchema):
    """
    Пользователь с паролем
    """

    hashed_password: str = Field(..., alias="password", title="Пароль")
