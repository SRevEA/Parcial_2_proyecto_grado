import asyncio
import base64
import hashlib
import json
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from ..lib import almacenamiento, eventos, vision
from ..lib.db import session_scope
from ..lib.errors import validacion
from ..repositories import apartamento as repo_apartamento
from ..repositories import evidencia_fotografica as repo_evidencia
from ..repositories import patron_facial as repo_patron
from ..repositories import registro_acceso as repo_registro
from ..repositories import residente as repo_residente
from ..schemas.reconocimiento import IntentoOut, ResidenteReconocido
from ..services import configuracion as servicio_configuracion


async def _datos_del_residente(
    id_residente: int, session: AsyncSession
) -> ResidenteReconocido | None:
    residente = await repo_residente.buscar_por_id(id_residente, session=session)
    if residente is None:
        return None
    apto = await repo_apartamento.buscar_por_id(residente.id_apartamento, session=session)
    return ResidenteReconocido(
        id_residente=residente.id_residente,
        nombre=residente.nombre,
        apellido=residente.apellido,
        torre=apto.torre if apto else '',
        numero=apto.apartamento.numero if apto else '',
    )


async def _guardar_evidencia(id_registro: int, imagen: bytes) -> None:
    async with session_scope() as s:
        dias = await servicio_configuracion.dias_conservacion(session=s)
        ruta = f'{datetime.now(UTC):%Y/%m/%d}/{id_registro}.jpg'
        await almacenamiento.subir(ruta, imagen)
        await repo_evidencia.insertar(
            id_registro=id_registro,
            ruta_archivo=ruta,
            hash_sha256=hashlib.sha256(imagen).hexdigest(),
            fecha_expiracion=datetime.now(UTC) + timedelta(days=dias),
            session=s,
        )


def _publicar(intento: IntentoOut, imagen: bytes) -> None:
    evento = intento.model_dump(mode='json')
    evento['imagen'] = f'data:image/jpeg;base64,{base64.b64encode(imagen).decode()}'
    eventos.publicar(json.dumps(evento))


async def procesar(id_punto: int, imagen: bytes, capturado_en: datetime) -> IntentoOut:
    vector, rostros = await asyncio.to_thread(vision.vector_de_rostro_unico, imagen)
    if vector is None:
        raise validacion('La imagen debe contener exactamente un rostro', [{'rostros': rostros}])

    async with session_scope() as s:
        umbral = await servicio_configuracion.umbral(session=s)
        parecido = await repo_patron.mas_parecido(vector, session=s)
        similitud = 0.0 if parecido is None else parecido[1]
        reconocido = parecido is not None and similitud >= umbral
        id_residente = parecido[0] if reconocido and parecido is not None else None

        registro = await repo_registro.insertar(
            id_punto=id_punto,
            resultado='RECONOCIDO' if reconocido else 'NO_RECONOCIDO',
            capturado_en=capturado_en,
            similitud=similitud,
            id_residente=id_residente,
            session=s,
        )

        intento = IntentoOut(
            id_registro=registro.id_registro,
            id_punto=id_punto,
            resultado=registro.resultado,
            similitud=round(similitud, 4),
            umbral=umbral,
            residente=await _datos_del_residente(id_residente, s) if id_residente else None,
            capturado_en=capturado_en,
            fecha_hora=registro.fecha_hora,
            segundos_respuesta=round((registro.fecha_hora - capturado_en).total_seconds(), 3),
        )

    _publicar(intento, imagen)
    await _guardar_evidencia(intento.id_registro, imagen)
    return intento
