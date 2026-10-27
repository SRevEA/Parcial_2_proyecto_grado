from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.punto_acceso import PuntoAcceso
from ..models.usuario_sistema import UsuarioSistema
from ..repositories import punto_acceso as repo_punto
from ..repositories import usuario_sistema as repo_usuario
from .db import sesion_de_peticion, session_scope
from .errors import no_autenticado, sin_permiso
from .seguridad import leer_token, verificar

Sesion = Annotated[AsyncSession, Depends(sesion_de_peticion)]


async def _validar_token(authorization: str | None, sesion: AsyncSession) -> UsuarioSistema:
    if authorization is None or not authorization.lower().startswith('bearer '):
        raise no_autenticado('Falta el token de sesion')
    datos = leer_token(authorization.split(' ', 1)[1].strip())
    if datos is None:
        raise no_autenticado('Token invalido o expirado')
    usuario = await repo_usuario.buscar_por_id(int(datos['sub']), session=sesion)
    if usuario is None or usuario.estado != 'ACTIVO':
        raise no_autenticado('El usuario ya no esta activo')
    return usuario


async def usuario_actual(
    sesion: Sesion,
    authorization: Annotated[str | None, Header()] = None,
) -> UsuarioSistema:
    return await _validar_token(authorization, sesion)


async def usuario_sin_sesion_compartida(
    authorization: Annotated[str | None, Header()] = None,
) -> UsuarioSistema:
    async with session_scope() as sesion:
        return await _validar_token(authorization, sesion)


Usuario = Annotated[UsuarioSistema, Depends(usuario_actual)]
UsuarioDeFlujo = Annotated[UsuarioSistema, Depends(usuario_sin_sesion_compartida)]


async def administrador(usuario: Usuario) -> UsuarioSistema:
    if usuario.rol != 'ADMINISTRADOR':
        raise sin_permiso('Esta operacion es solo para administradores')
    return usuario


Administrador = Annotated[UsuarioSistema, Depends(administrador)]


async def punto_actual(
    x_punto_id: Annotated[int | None, Header()] = None,
    x_punto_api_key: Annotated[str | None, Header()] = None,
) -> PuntoAcceso:
    if x_punto_id is None or x_punto_api_key is None:
        raise no_autenticado('Falta la credencial del punto de acceso')
    punto = await repo_punto.buscar_por_id(x_punto_id)
    if punto is None or punto.estado != 'ACTIVO':
        raise no_autenticado('Punto de acceso no registrado')
    if not verificar(x_punto_api_key, punto.api_key_hash):
        raise no_autenticado('Credencial del punto de acceso invalida')
    return punto


Punto = Annotated[PuntoAcceso, Depends(punto_actual)]
