from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.configuracion import Configuracion


async def obtener(clave: str, session: AsyncSession | None = None) -> str | None:
    async with session_scope(session) as s:
        return await s.scalar(select(Configuracion.valor).where(Configuracion.clave == clave))


async def listar(session: AsyncSession | None = None) -> list[Configuracion]:
    async with session_scope(session) as s:
        filas = await s.scalars(select(Configuracion).order_by(Configuracion.clave))
        return list(filas)


async def establecer(clave: str, valor: str, session: AsyncSession | None = None) -> bool:
    async with session_scope(session) as s:
        fila = await s.scalar(select(Configuracion).where(Configuracion.clave == clave))
        if fila is None:
            return False
        fila.valor = valor
        await s.flush()
        return True
