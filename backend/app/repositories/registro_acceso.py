from datetime import datetime
from decimal import Decimal
from typing import Any, NamedTuple

from sqlalchemy import Result, Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.apartamento import Apartamento
from ..models.evidencia_fotografica import EvidenciaFotografica
from ..models.registro_acceso import RegistroAcceso
from ..models.residente import Residente
from ..models.torre import Torre


class FilaRegistro(NamedTuple):
    registro: RegistroAcceso
    nombre: str | None
    apellido: str | None
    torre: str | None
    numero: str | None
    tiene_evidencia: bool


def _a_fila(fila: Row[Any]) -> FilaRegistro:
    registro, nombre, apellido, torre, numero, evidencia = tuple(fila)
    return FilaRegistro(registro, nombre, apellido, torre, numero, bool(evidencia))


def _filtrar(
    consulta: Select[*tuple[Any, ...]],
    desde: datetime | None,
    hasta: datetime | None,
    resultado: str | None,
    id_residente: int | None,
) -> Select[*tuple[Any, ...]]:
    if desde is not None:
        consulta = consulta.where(RegistroAcceso.fecha_hora >= desde)
    if hasta is not None:
        consulta = consulta.where(RegistroAcceso.fecha_hora <= hasta)
    if resultado is not None:
        consulta = consulta.where(RegistroAcceso.resultado == resultado)
    if id_residente is not None:
        consulta = consulta.where(RegistroAcceso.id_residente == id_residente)
    return consulta


async def insertar(
    id_punto: int,
    resultado: str,
    capturado_en: datetime,
    similitud: float | None = None,
    id_residente: int | None = None,
    session: AsyncSession | None = None,
) -> RegistroAcceso:
    async with session_scope(session) as s:
        registro = RegistroAcceso(
            id_punto=id_punto,
            id_residente=id_residente,
            resultado=resultado,
            similitud=None if similitud is None else Decimal(f'{similitud:.4f}'),
            capturado_en=capturado_en,
        )
        s.add(registro)
        await s.flush()
        return registro


async def buscar_por_id(
    id_registro: int, session: AsyncSession | None = None
) -> RegistroAcceso | None:
    async with session_scope(session) as s:
        return await s.scalar(
            select(RegistroAcceso).where(RegistroAcceso.id_registro == id_registro)
        )


async def listar(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    resultado: str | None = None,
    id_residente: int | None = None,
    limite: int = 50,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> list[FilaRegistro]:
    async with session_scope(session) as s:
        consulta = (
            select(
                RegistroAcceso,
                Residente.nombre,
                Residente.apellido,
                Torre.nombre,
                Apartamento.numero,
                EvidenciaFotografica.id_evidencia.is_not(None),
            )
            .outerjoin(Residente, Residente.id_residente == RegistroAcceso.id_residente)
            .outerjoin(Apartamento, Apartamento.id_apartamento == Residente.id_apartamento)
            .outerjoin(Torre, Torre.id_torre == Apartamento.id_torre)
            .outerjoin(
                EvidenciaFotografica,
                EvidenciaFotografica.id_registro == RegistroAcceso.id_registro,
            )
        )
        filas: Result[Any] = await s.execute(
            _filtrar(consulta, desde, hasta, resultado, id_residente)
            .order_by(RegistroAcceso.fecha_hora.desc())
            .limit(limite)
            .offset(desplazamiento)
        )
        return [_a_fila(fila) for fila in filas.all()]


async def contar(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    resultado: str | None = None,
    id_residente: int | None = None,
    session: AsyncSession | None = None,
) -> int:
    async with session_scope(session) as s:
        consulta = _filtrar(
            select(func.count()).select_from(RegistroAcceso), desde, hasta, resultado, id_residente
        )
        total = await s.scalar(consulta)
        return int(total or 0)
