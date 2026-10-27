from fastapi import APIRouter

from ..lib.dependencias import Administrador, Sesion, Usuario
from ..schemas.catalogo import ApartamentoOut, CrearApartamento, CrearTorre, TorreOut
from ..schemas.comunes import Pagina, Respuesta
from ..services import catalogo as servicio

router = APIRouter(prefix='/catalogo', tags=['catalogo'])


@router.get('/torres', response_model=Respuesta[Pagina[TorreOut]])
async def listar_torres(_: Usuario, sesion: Sesion) -> Respuesta[Pagina[TorreOut]]:
    items = await servicio.listar_torres(session=sesion)
    return Respuesta(data=Pagina(items=items, total=len(items)))


@router.post('/torres', response_model=Respuesta[TorreOut], status_code=201)
async def crear_torre(_: Administrador, datos: CrearTorre) -> Respuesta[TorreOut]:
    return Respuesta(statusCode=201, data=await servicio.crear_torre(datos.nombre))


@router.put('/torres/{id_torre}', response_model=Respuesta[TorreOut])
async def renombrar_torre(
    _: Administrador, id_torre: int, datos: CrearTorre
) -> Respuesta[TorreOut]:
    return Respuesta(data=await servicio.renombrar_torre(id_torre, datos.nombre))


@router.delete('/torres/{id_torre}', response_model=Respuesta[dict[str, bool]])
async def eliminar_torre(_: Administrador, id_torre: int) -> Respuesta[dict[str, bool]]:
    await servicio.eliminar_torre(id_torre)
    return Respuesta(data={'eliminada': True})


@router.get('/apartamentos', response_model=Respuesta[Pagina[ApartamentoOut]])
async def listar_apartamentos(
    _: Usuario, sesion: Sesion, id_torre: int | None = None
) -> Respuesta[Pagina[ApartamentoOut]]:
    items = await servicio.listar_apartamentos(id_torre=id_torre, session=sesion)
    return Respuesta(data=Pagina(items=items, total=len(items)))


@router.post(
    '/torres/{id_torre}/apartamentos', response_model=Respuesta[ApartamentoOut], status_code=201
)
async def crear_apartamento(
    _: Administrador, id_torre: int, datos: CrearApartamento
) -> Respuesta[ApartamentoOut]:
    return Respuesta(statusCode=201, data=await servicio.crear_apartamento(id_torre, datos.numero))


@router.put('/apartamentos/{id_apartamento}', response_model=Respuesta[ApartamentoOut])
async def cambiar_numero(
    _: Administrador, id_apartamento: int, datos: CrearApartamento
) -> Respuesta[ApartamentoOut]:
    return Respuesta(data=await servicio.cambiar_numero(id_apartamento, datos.numero))


@router.delete('/apartamentos/{id_apartamento}', response_model=Respuesta[dict[str, bool]])
async def eliminar_apartamento(_: Administrador, id_apartamento: int) -> Respuesta[dict[str, bool]]:
    await servicio.eliminar_apartamento(id_apartamento)
    return Respuesta(data={'eliminado': True})
