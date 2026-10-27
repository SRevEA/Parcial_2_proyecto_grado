from typing import Any, NamedTuple, cast

from sqlalchemy import CursorResult, Result, Row, Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.apartamento import Apartamento
from ..models.residente import Residente
from ..models.torre import Torre


class FilaApartamento(NamedTuple):
    apartamento: Apartamento
    torre: str
    residentes: int


_RESIDENTES = (
    select(func.count())
    .select_from(Residente)
    .where(Residente.id_apartamento == Apartamento.id_apartamento)
    .scalar_subquery()
)


def _consulta() -> Select[*tuple[Any, ...]]:
    return select(Apartamento, Torre.nombre, _RESIDENTES).join(
        Torre, Torre.id_torre == Apartamento.id_torre
    )


def _a_fila(fila: Row[Any]) -> FilaApartamento:
    apartamento, torre, residentes = tuple(fila)
    return FilaApartamento(apartamento, torre, int(residentes))


async def listar(
    id_torre: int | None = None, session: AsyncSession | None = None
) -> list[FilaApartamento]:
    async with session_scope(session) as s:
        consulta = _consulta()
        if id_torre is not None:
            consulta = consulta.where(Apartamento.id_torre == id_torre)
        filas: Result[Any] = await s.execute(consulta.order_by(Torre.nombre, Apartamento.numero))
        return [_a_fila(fila) for fila in filas.all()]


async def buscar_por_id(
    id_apartamento: int, session: AsyncSession | None = None
) -> FilaApartamento | None:
    async with session_scope(session) as s:
        filas: Result[Any] = await s.execute(
            _consulta().where(Apartamento.id_apartamento == id_apartamento)
        )
        fila = filas.one_or_none()
        return None if fila is None else _a_fila(fila)


async def buscar(
    id_torre: int, numero: str, session: AsyncSession | None = None
) -> Apartamento | None:
    async with session_scope(session) as s:
        return await s.scalar(
            select(Apartamento).where(
                Apartamento.id_torre == id_torre, Apartamento.numero == numero
            )
        )


async def insertar(id_torre: int, numero: str, session: AsyncSession | None = None) -> Apartamento:
    async with session_scope(session) as s:
        apartamento = Apartamento(id_torre=id_torre, numero=numero)
        s.add(apartamento)
        await s.flush()
        return apartamento


async def cambiar_numero(
    id_apartamento: int, numero: str, session: AsyncSession | None = None
) -> Apartamento | None:
    async with session_scope(session) as s:
        apartamento = await s.scalar(
            select(Apartamento).where(Apartamento.id_apartamento == id_apartamento)
        )
        if apartamento is None:
            return None
        apartamento.numero = numero
        await s.flush()
        return apartamento


async def contar_residentes(id_apartamento: int, session: AsyncSession | None = None) -> int:
    async with session_scope(session) as s:
        total = await s.scalar(
            select(func.count())
            .select_from(Residente)
            .where(Residente.id_apartamento == id_apartamento)
        )
        return int(total or 0)


async def eliminar(id_apartamento: int, session: AsyncSession | None = None) -> bool:
    async with session_scope(session) as s:
        resultado = cast(
            'CursorResult[Any]',
            await s.execute(
                delete(Apartamento).where(Apartamento.id_apartamento == id_apartamento)
            ),
        )
        return int(resultado.rowcount) > 0
