from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from bread_bot.main.database.base import SyncSessionLocal, AsyncSessionLocal


class OffsetQueryParams:
    """
    Зависимость для лимитирования списка записей из БД
    """
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


def get_sync_session() -> Session:
    """
    Зависимость для создания сессии БД
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_session() -> AsyncSession:
    """
    Асинхронная зависимость для создания асинхронной сессии БД
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
