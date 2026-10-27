from typing import Any, cast

from sqlalchemy import CursorResult, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.patron_facial import PatronFacial
from ..models.residente import Residente


async def insertar_varios(
    id_residente: int, vectores: list[list[float]], session: AsyncSession | None = None
) -> int:
    async with session_scope(session) as s:
        for vector in vectores:
            s.add(PatronFacial(id_residente=id_residente, embedding=vector))
        await s.flush()
        return len(vectores)


async def contar_por_residente(id_residente: int, session: AsyncSession | None = None) -> int:
    async with session_scope(session) as s:
        total = await s.scalar(
            select(func.count())
            .select_from(PatronFacial)
            .where(PatronFacial.id_residente == id_residente)
        )
        return int(total or 0)


async def eliminar_por_residente(id_residente: int, session: AsyncSession | None = None) -> int:
    async with session_scope(session) as s:
        resultado = cast(
            'CursorResult[Any]',
            await s.execute(delete(PatronFacial).where(PatronFacial.id_residente == id_residente)),
        )
        return int(resultado.rowcount)


async def mas_parecido(
    vector: list[float], session: AsyncSession | None = None
) -> tuple[int, float] | None:
    async with session_scope(session) as s:
        distancia = PatronFacial.embedding.cosine_distance(vector)
        fila = (
            await s.execute(
                select(PatronFacial.id_residente, distancia.label('distancia'))
                .join(Residente, Residente.id_residente == PatronFacial.id_residente)
                .where(Residente.estado == 'ACTIVO')
                .order_by(distancia)
                .limit(1)
            )
        ).first()
        if fila is None:
            return None
        return int(fila[0]), 1.0 - float(fila[1])
