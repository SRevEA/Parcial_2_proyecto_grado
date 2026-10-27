from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.errors import conflicto, no_encontrado
from ..lib.seguridad import hashear
from ..repositories import usuario_sistema as repo
from ..schemas.usuarios import ActualizarUsuario, CrearUsuario, UsuarioOut


def _a_salida(usuario: object) -> UsuarioOut:
    return UsuarioOut.model_validate(usuario, from_attributes=True)


async def listar(
    buscar: str | None = None,
    rol: str | None = None,
    estado: str | None = None,
    limite: int = 50,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> tuple[list[UsuarioOut], int]:
    items = await repo.listar(
        buscar=buscar,
        rol=rol,
        estado=estado,
        limite=limite,
        desplazamiento=desplazamiento,
        session=session,
    )
    total = await repo.contar(buscar=buscar, rol=rol, estado=estado, session=session)
    return [_a_salida(u) for u in items], total


async def crear(datos: CrearUsuario) -> UsuarioOut:
    if await repo.buscar_por_correo(str(datos.correo)) is not None:
        raise conflicto('Ya existe un usuario con ese correo')
    usuario = await repo.insertar(
        datos.nombre, str(datos.correo), hashear(datos.contrasena), datos.rol
    )
    return _a_salida(usuario)


async def actualizar(id_usuario: int, datos: ActualizarUsuario) -> UsuarioOut:
    usuario = await repo.actualizar(id_usuario, datos.nombre, datos.rol, datos.estado)
    if usuario is None:
        raise no_encontrado('El usuario no existe')
    return _a_salida(usuario)
