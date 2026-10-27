from typing import Annotated

from fastapi import APIRouter, Query

from ..lib.dependencias import Administrador, Sesion
from ..schemas.comunes import Pagina, Respuesta
from ..schemas.usuarios import ActualizarUsuario, CrearUsuario, UsuarioOut
from ..services import usuarios as servicio
from ..types.comunes import Estado, Rol

router = APIRouter(prefix='/usuarios', tags=['usuarios'])


@router.get('', response_model=Respuesta[Pagina[UsuarioOut]])
async def listar(
    _: Administrador,
    sesion: Sesion,
    buscar: Annotated[str | None, Query(max_length=80)] = None,
    rol: Annotated[Rol | None, Query()] = None,
    estado: Annotated[Estado | None, Query()] = None,
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
    desplazamiento: Annotated[int, Query(ge=0)] = 0,
) -> Respuesta[Pagina[UsuarioOut]]:
    items, total = await servicio.listar(
        buscar=buscar,
        rol=rol,
        estado=estado,
        limite=limite,
        desplazamiento=desplazamiento,
        session=sesion,
    )
    return Respuesta(data=Pagina(items=items, total=total))


@router.post('', response_model=Respuesta[UsuarioOut], status_code=201)
async def crear(_: Administrador, datos: CrearUsuario) -> Respuesta[UsuarioOut]:
    return Respuesta(statusCode=201, data=await servicio.crear(datos))


@router.put('/{id_usuario}', response_model=Respuesta[UsuarioOut])
async def actualizar(
    _: Administrador, id_usuario: int, datos: ActualizarUsuario
) -> Respuesta[UsuarioOut]:
    return Respuesta(data=await servicio.actualizar(id_usuario, datos))
