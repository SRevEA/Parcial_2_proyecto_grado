from ..lib.errors import no_autenticado, validacion
from ..lib.seguridad import emitir_token, hashear, verificar
from ..repositories import usuario_sistema as repo
from ..schemas.auth import CambioContrasena, Credenciales, Sesion


async def autenticar(credenciales: Credenciales) -> Sesion:
    usuario = await repo.buscar_por_correo(str(credenciales.correo))
    if usuario is None or not verificar(credenciales.contrasena, usuario.contrasena_hash):
        raise no_autenticado('Correo o contrasena incorrectos')
    if usuario.estado != 'ACTIVO':
        raise no_autenticado('El usuario esta inactivo')
    return Sesion(
        token=emitir_token(usuario.id_usuario, usuario.rol),
        id_usuario=usuario.id_usuario,
        nombre=usuario.nombre,
        rol=usuario.rol,
    )


async def cambiar_contrasena(id_usuario: int, cambio: CambioContrasena) -> None:
    usuario = await repo.buscar_por_id(id_usuario)
    if usuario is None or not verificar(cambio.actual, usuario.contrasena_hash):
        raise no_autenticado('La contrasena actual no coincide')
    if cambio.nueva == cambio.actual:
        raise validacion('La contrasena nueva debe ser distinta de la actual')
    await repo.cambiar_contrasena(id_usuario, hashear(cambio.nueva))
