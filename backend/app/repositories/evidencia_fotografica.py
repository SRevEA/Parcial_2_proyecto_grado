from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.evidencia_fotografica import EvidenciaFotografica


async def insertar(
    id_registro: int,
    ruta_archivo: str,
    hash_sha256: str,
    fecha_expiracion: datetime,
    session: AsyncSession | None = None,
) -> EvidenciaFotografica:
    async with session_scope(session) as s:
        evidencia = EvidenciaFotografica(
            id_registro=id_registro,
            ruta_archivo=ruta_archivo,
            hash_sha256=hash_sha256,
            fecha_expiracion=fecha_expiracion,
        )
        s.add(evidencia)
        await s.flush()
        return evidencia


async def buscar_por_id(
    id_evidencia: int, session: AsyncSession | None = None
) -> EvidenciaFotografica | None:
    async with session_scope(session) as s:
        return await s.scalar(
            select(EvidenciaFotografica).where(EvidenciaFotografica.id_evidencia == id_evidencia)
        )


async def buscar_por_registro(
    id_registro: int, session: AsyncSession | None = None
) -> EvidenciaFotografica | None:
    async with session_scope(session) as s:
        return await s.scalar(
            select(EvidenciaFotografica).where(EvidenciaFotografica.id_registro == id_registro)
        )


async def listar_vencidas(
    ahora: datetime, session: AsyncSession | None = None
) -> list[EvidenciaFotografica]:
    async with session_scope(session) as s:
        filas = await s.scalars(
            select(EvidenciaFotografica).where(EvidenciaFotografica.fecha_expiracion <= ahora)
        )
        return list(filas)


async def eliminar_varias(ids: list[int], session: AsyncSession | None = None) -> int:
    if not ids:
        return 0
    async with session_scope(session) as s:
        resultado = cast(
            'CursorResult[Any]',
            await s.execute(
                delete(EvidenciaFotografica).where(EvidenciaFotografica.id_evidencia.in_(ids))
            ),
        )
        return int(resultado.rowcount)


async def listar_por_residente(
    id_residente: int, session: AsyncSession | None = None
) -> list[EvidenciaFotografica]:
    from ..models.registro_acceso import RegistroAcceso

    async with session_scope(session) as s:
        filas = await s.scalars(
            select(EvidenciaFotografica)
            .join(RegistroAcceso, RegistroAcceso.id_registro == EvidenciaFotografica.id_registro)
            .where(RegistroAcceso.id_residente == id_residente)
        )
        return list(filas)
