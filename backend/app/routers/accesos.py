import asyncio
from collections.abc import AsyncIterator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse

from ..lib import eventos
from ..lib.dependencias import Sesion, Usuario, UsuarioDeFlujo
from ..schemas.accesos import EvidenciaOut, RegistroOut
from ..schemas.comunes import Pagina, Respuesta
from ..services import accesos as servicio

router = APIRouter(prefix='/accesos', tags=['accesos'])

SEGUNDOS_LATIDO = 15


@router.get('', response_model=Respuesta[Pagina[RegistroOut]])
async def listar(
    _: Usuario,
    sesion: Sesion,
    desde: date | None = None,
    hasta: date | None = None,
    resultado: str | None = None,
    id_residente: int | None = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> Respuesta[Pagina[RegistroOut]]:
    items, total = await servicio.listar(
        desde=desde,
        hasta=hasta,
        resultado=resultado,
        id_residente=id_residente,
        limite=limite,
        desplazamiento=desplazamiento,
        session=sesion,
    )
    return Respuesta(data=Pagina(items=items, total=total))


@router.get('/exportar')
async def exportar(
    _: Usuario,
    sesion: Sesion,
    desde: date | None = None,
    hasta: date | None = None,
    resultado: str | None = None,
) -> Response:
    contenido = await servicio.exportar_csv(
        desde=desde, hasta=hasta, resultado=resultado, session=sesion
    )
    return Response(
        content=contenido,
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="historial-accesos.csv"'},
    )


@router.get('/monitor')
async def monitor(_: UsuarioDeFlujo) -> StreamingResponse:
    cola = eventos.suscribir()

    async def flujo() -> AsyncIterator[str]:
        try:
            yield ': conectado\n\n'
            while True:
                try:
                    mensaje = await asyncio.wait_for(cola.get(), timeout=SEGUNDOS_LATIDO)
                except TimeoutError:
                    yield ': latido\n\n'
                    continue
                yield f'data: {mensaje}\n\n'
        finally:
            eventos.cancelar(cola)

    return StreamingResponse(
        flujo(),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@router.get('/{id_registro}/evidencia', response_model=Respuesta[EvidenciaOut])
async def evidencia(usuario: Usuario, id_registro: int) -> Respuesta[EvidenciaOut]:
    return Respuesta(data=await servicio.ver_evidencia(id_registro, usuario.id_usuario))
