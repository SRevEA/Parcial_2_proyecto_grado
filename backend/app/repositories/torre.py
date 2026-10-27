from typing import Any, NamedTuple, cast

from sqlalchemy import CursorResult, Result, Row, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.apartamento import Apartamento
from ..models.torre import Torre


class FilaTorre(NamedTuple):
    torre: Torre
    apartamentos: int


_APARTAMENTOS = (
    select(func.count())
    .select_from(Apartamento)
    .where(Apartamento.id_torre == Torre.id_torre)
    .scalar_subquery()
)


def _a_fila(fila: Row[Any]) -> FilaTorre:
    torre, apartamentos = tuple(fila)
    return FilaTorre(torre, int(apartamentos))


async def listar(session: AsyncSession | None = None) -> list[FilaTorre]:
    async with session_scope(session) as s:
        filas: Result[Any] = await s.execute(select(Torre, _APARTAMENTOS).order_by(Torre.nombre))
        return [_a_fila(fila) for fila in filas.all()]


async def buscar_por_id(id_torre: int, session: AsyncSession | None = None) -> Torre | None:
    async with session_scope(session) as s:
        return await s.scalar(select(Torre).where(Torre.id_torre == id_torre))


async def buscar_por_nombre(nombre: str, session: AsyncSession | None = None) -> Torre | None:
    async with session_scope(session) as s:
        return await s.scalar(select(Torre).where(Torre.nombre == nombre))


async def insertar(nombre: str, session: AsyncSession | None = None) -> Torre:
    async with session_scope(session) as s:
        torre = Torre(nombre=nombre)
        s.add(torre)
        await s.flush()
        return torre


async def renombrar(
    id_torre: int, nombre: str, session: AsyncSession | None = None
) -> Torre | None:
    async with session_scope(session) as s:
        torre = await s.scalar(select(Torre).where(Torre.id_torre == id_torre))
        if torre is None:
            return None
        torre.nombre = nombre
        await s.flush()
        return torre


async def contar_apartamentos(id_torre: int, session: AsyncSession | None = None) -> int:
    async with session_scope(session) as s:
        total = await s.scalar(
            select(func.count()).select_from(Apartamento).where(Apartamento.id_torre == id_torre)
        )
        return int(total or 0)


async def eliminar(id_torre: int, session: AsyncSession | None = None) -> bool:
    async with session_scope(session) as s:
        resultado = cast(
            'CursorResult[Any]',
            await s.execute(delete(Torre).where(Torre.id_torre == id_torre)),
        )
        return int(resultado.rowcount) > 0
