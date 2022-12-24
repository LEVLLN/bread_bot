from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from bread_bot.main.settings import (
    DATABASE_URI,
    ASYNC_DATABASE_URI,
    DB_POOL_SIZE,
    DB_POOL_MAX_OVERFLOW,
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
