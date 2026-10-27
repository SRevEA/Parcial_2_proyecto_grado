from typing import Any, NamedTuple, cast

from sqlalchemy import CursorResult, Result, Row, Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.apartamento import Apartamento
from ..models.autorizacion_datos import AutorizacionDatos
from ..models.patron_facial import PatronFacial
from ..models.residente import Residente
from ..models.torre import Torre


class FilaResidente(NamedTuple):
    residente: Residente
    id_torre: int | None
    torre: str | None
    numero: str | None
    muestras: int
    autorizado: bool


_MUESTRAS = (
    select(func.count())
    .select_from(PatronFacial)
    .where(PatronFacial.id_residente == Residente.id_residente)
    .scalar_subquery()
)

_AUTORIZADO = (
    select(func.count())
    .select_from(AutorizacionDatos)
    .where(
        AutorizacionDatos.id_residente == Residente.id_residente,
        AutorizacionDatos.aceptada.is_(True),
    )
    .scalar_subquery()
)


def _patron(texto: str) -> str:
    limpio = texto.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return f'%{limpio}%'


def _filtrar(
    consulta: Select[*tuple[Any, ...]],
    estado: str | None,
    buscar: str | None,
    autorizacion: bool | None,
    patrones: bool | None,
) -> Select[*tuple[Any, ...]]:
    if estado is not None:
        consulta = consulta.where(Residente.estado == estado)
    if buscar:
        texto = _patron(buscar)
        consulta = consulta.where(
            func.concat(Residente.nombre, ' ', Residente.apellido).ilike(texto, escape='\\')
            | Residente.documento.ilike(texto, escape='\\')
            | Torre.nombre.ilike(texto, escape='\\')
            | Apartamento.numero.ilike(texto, escape='\\')
        )
    if autorizacion is not None:
        consulta = consulta.where(_AUTORIZADO > 0 if autorizacion else _AUTORIZADO == 0)
    if patrones is not None:
        consulta = consulta.where(_MUESTRAS > 0 if patrones else _MUESTRAS == 0)
    return consulta


def _a_fila(fila: Row[Any]) -> FilaResidente:
    residente, id_torre, torre, numero, muestras, autorizado = tuple(fila)
    return FilaResidente(residente, id_torre, torre, numero, int(muestras), autorizado > 0)


async def buscar_por_id(id_residente: int, session: AsyncSession | None = None) -> Residente | None:
    async with session_scope(session) as s:
        return await s.scalar(select(Residente).where(Residente.id_residente == id_residente))


async def buscar_por_documento(
    documento: str, session: AsyncSession | None = None
) -> Residente | None:
    async with session_scope(session) as s:
        return await s.scalar(select(Residente).where(Residente.documento == documento))


async def listar(
    estado: str | None = None,
    buscar: str | None = None,
    autorizacion: bool | None = None,
    patrones: bool | None = None,
    limite: int | None = None,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> list[FilaResidente]:
    async with session_scope(session) as s:
        consulta = (
            select(
                Residente,
                Apartamento.id_torre,
                Torre.nombre,
                Apartamento.numero,
                _MUESTRAS,
                _AUTORIZADO,
            )
            .outerjoin(Apartamento, Apartamento.id_apartamento == Residente.id_apartamento)
            .outerjoin(Torre, Torre.id_torre == Apartamento.id_torre)
        )
        consulta = (
            _filtrar(consulta, estado, buscar, autorizacion, patrones)
            .order_by(Residente.apellido, Residente.nombre)
            .offset(desplazamiento)
        )
        if limite is not None:
            consulta = consulta.limit(limite)
        filas: Result[Any] = await s.execute(consulta)
        return [_a_fila(fila) for fila in filas.all()]


async def contar(
    estado: str | None = None,
    buscar: str | None = None,
    autorizacion: bool | None = None,
    patrones: bool | None = None,
    session: AsyncSession | None = None,
) -> int:
    async with session_scope(session) as s:
        consulta = (
            select(func.count())
            .select_from(Residente)
            .outerjoin(Apartamento, Apartamento.id_apartamento == Residente.id_apartamento)
            .outerjoin(Torre, Torre.id_torre == Apartamento.id_torre)
        )
        total = await s.scalar(_filtrar(consulta, estado, buscar, autorizacion, patrones))
        return int(total or 0)


async def insertar(
    nombre: str,
    apellido: str,
    documento: str,
    id_apartamento: int,
    session: AsyncSession | None = None,
) -> Residente:
    async with session_scope(session) as s:
        residente = Residente(
            nombre=nombre,
            apellido=apellido,
            documento=documento,
            id_apartamento=id_apartamento,
            estado='ACTIVO',
        )
        s.add(residente)
        await s.flush()
        return residente


async def actualizar(
    id_residente: int,
    nombre: str,
    apellido: str,
    documento: str,
    id_apartamento: int,
    session: AsyncSession | None = None,
) -> Residente | None:
    async with session_scope(session) as s:
        residente = await s.scalar(select(Residente).where(Residente.id_residente == id_residente))
        if residente is None:
            return None
        residente.nombre = nombre
        residente.apellido = apellido
        residente.documento = documento
        residente.id_apartamento = id_apartamento
        await s.flush()
        return residente


async def cambiar_estado(
    id_residente: int, estado: str, session: AsyncSession | None = None
) -> bool:
    async with session_scope(session) as s:
        residente = await s.scalar(select(Residente).where(Residente.id_residente == id_residente))
        if residente is None:
            return False
        residente.estado = estado
        await s.flush()
        return True


async def eliminar(id_residente: int, session: AsyncSession | None = None) -> bool:
    async with session_scope(session) as s:
        resultado = cast(
            'CursorResult[Any]',
            await s.execute(delete(Residente).where(Residente.id_residente == id_residente)),
        )
        return int(resultado.rowcount) > 0
