from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import TokenDataSchema
from bread_bot.main.settings import ALGORITHM, SECRET_KEY
from bread_bot.utils.dependencies import get_async_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    """
    Функция верификации пароля
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Функция хэширования пароля.
    """
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Получить данные пользователя из БД, верифицировать данные
    :return:
    """
    user = await User.async_first(db, User.username == username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    """
    Создание токена на указанный срок по логину и паролю
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(db: AsyncSession = Depends(get_async_session), token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency: Логин по токену
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataSchema(username=username)
    except JWTError:
        raise credentials_exception
    user = await User.async_first(
        db=db,
        where=User.username == token_data.username,
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency: Логин по токену + проверка пользователя на активность
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency: Логин по токену + проверка
    пользователя на активность + Проверка на активность
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access Denied")
    return await get_current_active_user(current_user=current_user)
