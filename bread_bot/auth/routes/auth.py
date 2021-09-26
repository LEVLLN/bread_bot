import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from bread_bot.auth.methods.auth_methods import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from bread_bot.auth.models import User
from bread_bot.auth.schemas.auth import TokenSchema, \
    UserCreateSchema, \
    UserInfoSchema
from bread_bot.main.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from bread_bot.utils.dependencies import \
    OffsetQueryParams, \
    get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='',
    tags=['auth'],
    dependencies=[Depends(get_async_session)],
    responses={404: {'description': 'Not found'}},
)


@router.post('/users/create', response_model=UserInfoSchema)
async def create_user(user_schema: UserCreateSchema,
                      db: AsyncSession = Depends(get_async_session)):
    """
    Зарегистрировать пользователя
    """
    user_schema.hashed_password = get_password_hash(
        user_schema.hashed_password)
    try:
        user = await User.async_add_by_schema(db, user_schema)
    except Exception as e:
        logger.info(f'Не удалось создать пользователя '
                    f'по причине: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка регистрации пользователя'
        )
    else:
        return user


@router.get('/users',
            response_model=list[UserInfoSchema],
            dependencies=[Depends(get_current_active_user)])
async def get_users(db: AsyncSession = Depends(get_async_session),
                    offset_params: OffsetQueryParams = Depends()):
    """
    Получить список пользователей
    """
    return await User.async_offset_records(db=db, offset_params=offset_params)


@router.post('/token', response_model=TokenSchema)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_session)):
    """
    Логин и получение токена авторизации
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/users/public/', response_model=list[UserInfoSchema])
async def public_users(session: AsyncSession = Depends(get_async_session)):
    logger.info('Getting All public users')
    return await User.async_all(session)
