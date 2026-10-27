from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.autorizacion_datos import AutorizacionDatos


async def buscar_por_residente(
    id_residente: int, session: AsyncSession | None = None
) -> AutorizacionDatos | None:
    async with session_scope(session) as s:
        return await s.scalar(
            select(AutorizacionDatos).where(AutorizacionDatos.id_residente == id_residente)
        )


async def insertar(
    id_residente: int,
    aceptada: bool,
    finalidades: str,
    version_politica: str,
    session: AsyncSession | None = None,
) -> AutorizacionDatos:
    async with session_scope(session) as s:
        autorizacion = AutorizacionDatos(
            id_residente=id_residente,
            aceptada=aceptada,
            finalidades=finalidades,
            version_politica=version_politica,
        )
        s.add(autorizacion)
        await s.flush()
        return autorizacion
