from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bread_bot.main.database.base import DeclarativeBase
from bread_bot.main.webserver import app
from bread_bot.utils.dependencies import get_sync_session, get_async_session

# Синхронные механизмы БД
test_sync_engine = create_engine("sqlite:///:memory:?check_same_thread=False")
TestSyncLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_sync_engine,
)


def init_sync_session(drop_all=True):
    """
    Получить синхронную сессию БД для тестов

    :param drop_all: Удалить все перед новой сессией
    """
    if drop_all:
        DeclarativeBase.metadata.drop_all(test_sync_engine)
    DeclarativeBase.metadata.create_all(test_sync_engine)
    session = TestSyncLocal()
    return session


def dependency_override_get_sync_session():
    """
    Зависимость для FastAPI с синхронными сессиями БД для тестов
    """
    try:
        db = TestSyncLocal()
        yield db
    finally:
        db.close()


# Асинхронные механизмы БД
test_async_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:?check_same_thread=False",
)
TestAsyncSessionLocal = sessionmaker(
    test_async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_async_session(drop_all=True) -> AsyncSession:
    """
    Получить асинхронную сессию БД для тестов

    :param drop_all: Удалить все перед новой сессией
    """
    async with test_async_engine.begin() as conn:
        if drop_all:
            await conn.run_sync(DeclarativeBase.metadata.drop_all)
        await conn.run_sync(DeclarativeBase.metadata.create_all)
    session = TestAsyncSessionLocal()
    return session


async def dependency_override_get_async_session() -> AsyncSession:
    """
    Зависимость для FastAPI с асинхронными сессиями БД для тестов
    """
    async with TestAsyncSessionLocal() as session:
        yield session


# FastApi настройки

TEST_SERVER_URL = "http://test"

test_app = app

test_app.dependency_overrides[get_sync_session] = dependency_override_get_sync_session
test_app.dependency_overrides[get_async_session] = dependency_override_get_async_session
