from fastapi import APIRouter

from ..lib.dependencias import Usuario
from ..schemas.auth import CambioContrasena, Credenciales, Sesion
from ..schemas.comunes import Respuesta
from ..services import auth as servicio

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Respuesta[Sesion])
async def login(credenciales: Credenciales) -> Respuesta[Sesion]:
    return Respuesta(data=await servicio.autenticar(credenciales))


@router.get('/yo', response_model=Respuesta[Sesion])
async def yo(usuario: Usuario) -> Respuesta[Sesion]:
    return Respuesta(
        data=Sesion(
            token='',
            id_usuario=usuario.id_usuario,
            nombre=usuario.nombre,
            rol=usuario.rol,
        )
    )


@router.post('/contrasena', response_model=Respuesta[dict[str, bool]])
async def cambiar(usuario: Usuario, cambio: CambioContrasena) -> Respuesta[dict[str, bool]]:
    await servicio.cambiar_contrasena(usuario.id_usuario, cambio)
    return Respuesta(data={'cambiada': True})
