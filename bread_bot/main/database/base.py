from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from bread_bot.main.settings import (
    ASYNC_DATABASE_URI,
    DATABASE_URI,
    DB_POOL_MAX_OVERFLOW,
    DB_POOL_SIZE,
)

sync_engine = create_engine(
    DATABASE_URI,
    poolclass=NullPool,
)
DeclarativeBase = declarative_base()

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URI,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_POOL_MAX_OVERFLOW,
)

async_null_pool_engine = create_async_engine(
    ASYNC_DATABASE_URI,
    poolclass=NullPool,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
