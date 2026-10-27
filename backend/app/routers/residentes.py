from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile

from ..lib.dependencias import Administrador, Sesion, Usuario
from ..schemas.comunes import Pagina, Respuesta
from ..schemas.residentes import (
    ActualizarResidente,
    AutorizacionOut,
    CrearResidente,
    PatronesOut,
    RegistrarAutorizacion,
    ResidenteOut,
)
from ..services import residentes as servicio
from ..types.comunes import Estado

router = APIRouter(prefix='/residentes', tags=['residentes'])


@router.get('', response_model=Respuesta[Pagina[ResidenteOut]])
async def listar(
    _: Usuario,
    sesion: Sesion,
    estado: Annotated[Estado | None, Query()] = None,
    buscar: Annotated[str | None, Query(max_length=80)] = None,
    autorizacion: bool | None = None,
    patrones: bool | None = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> Respuesta[Pagina[ResidenteOut]]:
    items, total = await servicio.listar(
        estado=estado,
        buscar=buscar,
        autorizacion=autorizacion,
        patrones=patrones,
        limite=limite,
        desplazamiento=desplazamiento,
        session=sesion,
    )
    return Respuesta(data=Pagina(items=items, total=total))


@router.get('/{id_residente}', response_model=Respuesta[ResidenteOut])
async def obtener(_: Usuario, sesion: Sesion, id_residente: int) -> Respuesta[ResidenteOut]:
    return Respuesta(data=await servicio.obtener(id_residente, session=sesion))


@router.post('', response_model=Respuesta[ResidenteOut], status_code=201)
async def crear(_: Administrador, datos: CrearResidente) -> Respuesta[ResidenteOut]:
    return Respuesta(statusCode=201, data=await servicio.crear(datos))


@router.put('/{id_residente}', response_model=Respuesta[ResidenteOut])
async def actualizar(
    _: Administrador, id_residente: int, datos: ActualizarResidente
) -> Respuesta[ResidenteOut]:
    return Respuesta(data=await servicio.actualizar(id_residente, datos))


@router.post(
    '/{id_residente}/autorizacion', response_model=Respuesta[AutorizacionOut], status_code=201
)
async def autorizar(
    _: Administrador, id_residente: int, datos: RegistrarAutorizacion
) -> Respuesta[AutorizacionOut]:
    return Respuesta(
        statusCode=201, data=await servicio.registrar_autorizacion(id_residente, datos)
    )


@router.post('/{id_residente}/patrones', response_model=Respuesta[PatronesOut], status_code=201)
async def capturar(
    _: Administrador,
    id_residente: int,
    imagenes: Annotated[list[UploadFile], File()],
) -> Respuesta[PatronesOut]:
    datos = [await imagen.read() for imagen in imagenes]
    return Respuesta(statusCode=201, data=await servicio.capturar_patrones(id_residente, datos))


@router.post('/{id_residente}/inactivar', response_model=Respuesta[ResidenteOut])
async def inactivar(_: Administrador, id_residente: int) -> Respuesta[ResidenteOut]:
    return Respuesta(data=await servicio.cambiar_estado(id_residente, 'INACTIVO'))


@router.post('/{id_residente}/activar', response_model=Respuesta[ResidenteOut])
async def activar(_: Administrador, id_residente: int) -> Respuesta[ResidenteOut]:
    return Respuesta(data=await servicio.cambiar_estado(id_residente, 'ACTIVO'))


@router.delete('/{id_residente}', response_model=Respuesta[dict[str, bool]])
async def suprimir(_: Administrador, id_residente: int) -> Respuesta[dict[str, bool]]:
    await servicio.suprimir(id_residente)
    return Respuesta(data={'suprimido': True})
