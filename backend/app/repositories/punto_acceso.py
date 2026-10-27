from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.punto_acceso import PuntoAcceso


async def listar_activos(session: AsyncSession | None = None) -> list[PuntoAcceso]:
    async with session_scope(session) as s:
        filas = await s.scalars(select(PuntoAcceso).where(PuntoAcceso.estado == 'ACTIVO'))
        return list(filas)


async def buscar_por_id(id_punto: int, session: AsyncSession | None = None) -> PuntoAcceso | None:
    async with session_scope(session) as s:
        return await s.scalar(select(PuntoAcceso).where(PuntoAcceso.id_punto == id_punto))
