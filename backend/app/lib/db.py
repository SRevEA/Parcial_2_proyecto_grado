from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=1_800,
)

crear_sesion = async_sessionmaker(engine, expire_on_commit=False)


async def sesion_de_peticion() -> AsyncIterator[AsyncSession]:
    async with crear_sesion() as propia:
        try:
            yield propia
            await propia.commit()
        except Exception:
            await propia.rollback()
            raise


@asynccontextmanager
async def session_scope(session: AsyncSession | None = None) -> AsyncIterator[AsyncSession]:
    if session is not None:
        yield session
        return
    async with crear_sesion() as propia:
        try:
            yield propia
            await propia.commit()
        except Exception:
            await propia.rollback()
            raise
