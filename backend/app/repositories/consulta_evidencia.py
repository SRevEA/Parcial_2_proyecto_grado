from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.consulta_evidencia import ConsultaEvidencia


async def insertar(
    id_evidencia: int, id_usuario: int, session: AsyncSession | None = None
) -> ConsultaEvidencia:
    async with session_scope(session) as s:
        consulta = ConsultaEvidencia(id_evidencia=id_evidencia, id_usuario=id_usuario)
        s.add(consulta)
        await s.flush()
        return consulta


async def listar(limite: int = 100, session: AsyncSession | None = None) -> list[ConsultaEvidencia]:
    async with session_scope(session) as s:
        filas = await s.scalars(
            select(ConsultaEvidencia).order_by(ConsultaEvidencia.fecha_hora.desc()).limit(limite)
        )
        return list(filas)
