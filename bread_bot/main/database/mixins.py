import datetime
import logging

from sqlalchemy import Column, Integer, DateTime, inspect, Boolean, select
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, declared_attr, selectinload

from bread_bot.main.database.base import DeclarativeBase
from bread_bot.utils.dependencies import OffsetQueryParams
from bread_bot.utils.helpers import chunks


logger = logging.getLogger(__name__)


class AbstractIsActiveBaseModel(DeclarativeBase):
    __abstract__ = True

    is_active = Column(Boolean, nullable=False, default=True)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer,
                nullable=False,
                primary_key=True,
                autoincrement=True)
    created_at = Column(DateTime(timezone=False),
                        nullable=False,
                        default=datetime.datetime.now)
    updated_at = Column(DateTime(timezone=False),
                        nullable=False,
                        default=datetime.datetime.now,
                        onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class CRUDMixin(object):
    """
    Различные методы, которые упрощают реализацию запросов
    """
    __table_args__ = {'extend_existing': True}

    @classmethod
    async def _async_filter(
            cls,
            session: AsyncSession,
            filter_expression,
            select_in_load,
            order_by,
            limit,
    ) -> ScalarResult:
        """
        Составление select запроса с фильтрами и ограничениями

        :param session: Сессия Базы Данных
        :param filter_expression: Выражение для where
        :param select_in_load: Загрузка связанных объектов по ключу
        :param order_by: Группировка по полю
        :param limit: Ограничение количества записей
        """
        expression = select(cls)
        if filter_expression is not None:
            expression = expression.where(
                filter_expression
            )
        if select_in_load is not None:
            expression = expression.options(
                selectinload(select_in_load)
            )
        if order_by is not None:
            expression = expression.order_by(
                order_by
            )
        if limit is not None:
            expression = expression.limit(
                limit
            )
        logger.debug(expression)
        result = await session.execute(expression)
        return result.scalars()

    @classmethod
    async def async_filter(
            cls,
            session: AsyncSession,
            filter_expression=None,
            select_in_load=None,
            order_by=None,
            limit=None,
    ):
        scalars = await cls._async_filter(
            session,
            filter_expression,
            select_in_load,
            order_by=order_by,
            limit=limit,
        )
        return scalars.all()

    @classmethod
    async def async_first(
            cls,
            session: AsyncSession,
            filter_expression=None,
            select_in_load=None,
            order_by=None,
    ):
        scalars = await cls._async_filter(
            session,
            filter_expression,
            select_in_load,
            order_by=order_by,
            limit=1
        )
        return scalars.first()

    @classmethod
    async def async_all(cls, db: AsyncSession):
        """
        Async get all objects

        :return: list[EntityModelClass]
        """
        result = await db.execute(
            select(cls)
        )
        return result.scalars().all()

    @classmethod
    async def async_offset_records(
            cls,
            db: AsyncSession,
            offset_params: OffsetQueryParams,
    ):
        """
        Async get all objects with offset

        :return: list[EntityModelClass][offset.skip:offset.limit]
        """
        result = await db.execute(
            select(cls).offset(offset_params.skip).limit(offset_params.limit)
        )
        return result.scalars().all()

    @classmethod
    async def async_add_all(
            cls,
            db: AsyncSession,
            instances: list,
            chunk_size=1000
    ):
        """
        Async Bulk Create/Update by instances
        """
        for chunk in chunks(instances, chunk_size):
            db.add_all(chunk)
            try:
                await db.commit()
            except Exception as exc:
                await db.rollback()
                raise exc
            else:
                logger.info('Созданы/Обновлены объекты %s: %s',
                            cls.__name__, instances)

    @classmethod
    async def async_add(
            cls,
            db: AsyncSession,
            instance: 'CRUDMixin',
    ):
        """
        Async Create/Update by instance
        """
        db.add(instance)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        else:
            try:
                await db.refresh(instance)
            except Exception:
                logger.debug(f'Невозможно обновить объект: {instance}')
            logger.info(f'Создан {cls.__name__}: {instance}')
            return instance

    @classmethod
    async def async_add_by_schema(cls, db: AsyncSession, instance_schema):
        """
        Async create/update by instance_schema

        :param db: Db session
        :param instance_schema: Pydantic schema
        """
        instance = cls(**instance_schema.dict())
        await cls.async_add(db, instance)
        return instance

    @classmethod
    def offset_records(cls, db: Session, offset_params: OffsetQueryParams):
        return db \
            .query(cls) \
            .filter() \
            .offset(offset_params.skip) \
            .limit(offset_params.limit) \
            .all()

    @classmethod
    def all(cls, db: Session):
        return db \
            .query(cls) \
            .filter() \
            .all()

    @classmethod
    def sync_add(cls, db: Session, instance):
        db.add(instance)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise exc
        else:
            logger.info(f'Создан {cls.__name__}: {instance}')
            return instance

    @classmethod
    def sync_add_by_schema(cls, db: Session, instance_schema):
        instance = cls(**instance_schema.dict())
        return cls.sync_add(db, instance)

    @classmethod
    def first(cls, db: Session, **kwargs):
        return db.query(cls).filter_by(**kwargs).first()

    @classmethod
    def filter_by(cls, db: Session, **kwargs):
        return db.query(db).filter_by(**kwargs).all()
