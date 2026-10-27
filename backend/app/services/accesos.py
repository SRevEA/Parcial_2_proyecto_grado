import csv
import io
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from ..lib import almacenamiento
from ..lib.db import session_scope
from ..lib.errors import no_encontrado
from ..repositories import consulta_evidencia as repo_consulta
from ..repositories import evidencia_fotografica as repo_evidencia
from ..repositories import registro_acceso as repo_registro
from ..repositories.registro_acceso import FilaRegistro
from ..schemas.accesos import EvidenciaOut, RegistroOut
from ..types.comunes import ZONA_HORARIA

ENCABEZADOS_CSV = [
    'id_registro',
    'fecha_hora',
    'capturado_en',
    'segundos_respuesta',
    'id_punto',
    'resultado',
    'similitud',
    'residente',
    'torre',
    'numero',
]
LIMITE_EXPORTACION = 20_000
ZONA = ZoneInfo(ZONA_HORARIA)


def _inicio_del_dia(dia: date | None) -> datetime | None:
    return None if dia is None else datetime.combine(dia, time.min, tzinfo=ZONA)


def _fin_del_dia(dia: date | None) -> datetime | None:
    return None if dia is None else datetime.combine(dia, time.max, tzinfo=ZONA)


def _a_salida(fila: FilaRegistro) -> RegistroOut:
    registro = fila.registro
    return RegistroOut(
        id_registro=registro.id_registro,
        id_punto=registro.id_punto,
        resultado=registro.resultado,
        similitud=float(registro.similitud) if registro.similitud is not None else None,
        id_residente=registro.id_residente,
        nombre_residente=f'{fila.nombre} {fila.apellido}' if fila.nombre else None,
        torre=fila.torre,
        numero=fila.numero,
        capturado_en=registro.capturado_en,
        fecha_hora=registro.fecha_hora,
        segundos_respuesta=round((registro.fecha_hora - registro.capturado_en).total_seconds(), 3),
        tiene_evidencia=fila.tiene_evidencia,
    )


async def listar(
    desde: date | None = None,
    hasta: date | None = None,
    resultado: str | None = None,
    id_residente: int | None = None,
    limite: int = 50,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> tuple[list[RegistroOut], int]:
    async with session_scope(session) as s:
        filas = await repo_registro.listar(
            desde=_inicio_del_dia(desde),
            hasta=_fin_del_dia(hasta),
            resultado=resultado,
            id_residente=id_residente,
            limite=limite,
            desplazamiento=desplazamiento,
            session=s,
        )
        total = await repo_registro.contar(
            desde=_inicio_del_dia(desde),
            hasta=_fin_del_dia(hasta),
            resultado=resultado,
            id_residente=id_residente,
            session=s,
        )
    return [_a_salida(fila) for fila in filas], total


async def ver_evidencia(
    id_registro: int, id_usuario: int, session: AsyncSession | None = None
) -> EvidenciaOut:
    async with session_scope(session) as s:
        evidencia = await repo_evidencia.buscar_por_registro(id_registro, session=s)
        if evidencia is None:
            raise no_encontrado('Ese intento no tiene evidencia')
        url = await almacenamiento.url_firmada(evidencia.ruta_archivo)
        await repo_consulta.insertar(evidencia.id_evidencia, id_usuario, session=s)
        return EvidenciaOut(
            id_evidencia=evidencia.id_evidencia,
            id_registro=evidencia.id_registro,
            url=url,
            hash_sha256=evidencia.hash_sha256,
            fecha_expiracion=evidencia.fecha_expiracion,
        )


async def exportar_csv(
    desde: date | None = None,
    hasta: date | None = None,
    resultado: str | None = None,
    session: AsyncSession | None = None,
) -> str:
    registros, _ = await listar(
        desde=desde,
        hasta=hasta,
        resultado=resultado,
        limite=LIMITE_EXPORTACION,
        session=session,
    )
    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerow(ENCABEZADOS_CSV)
    for r in registros:
        escritor.writerow(
            [
                r.id_registro,
                r.fecha_hora.isoformat(),
                r.capturado_en.isoformat(),
                r.segundos_respuesta,
                r.id_punto,
                r.resultado,
                '' if r.similitud is None else f'{r.similitud:.4f}',
                r.nombre_residente or '',
                r.torre or '',
                r.numero or '',
            ]
        )
    return buffer.getvalue()


async def purgar_vencidas() -> int:
    async with session_scope() as s:
        vencidas = await repo_evidencia.listar_vencidas(datetime.now(UTC), session=s)
        if not vencidas:
            return 0
        await almacenamiento.eliminar([e.ruta_archivo for e in vencidas])
        return await repo_evidencia.eliminar_varias([e.id_evidencia for e in vencidas], session=s)
