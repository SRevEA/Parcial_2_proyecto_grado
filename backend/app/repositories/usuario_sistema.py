from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..models.usuario_sistema import UsuarioSistema


def _patron(texto: str) -> str:
    limpio = texto.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return f'%{limpio}%'


def _filtrar(
    consulta: Select[*tuple[Any, ...]],
    buscar: str | None,
    rol: str | None,
    estado: str | None,
) -> Select[*tuple[Any, ...]]:
    if buscar:
        texto = _patron(buscar)
        consulta = consulta.where(
            UsuarioSistema.nombre.ilike(texto, escape='\\')
            | UsuarioSistema.correo.ilike(texto, escape='\\')
        )
    if rol is not None:
        consulta = consulta.where(UsuarioSistema.rol == rol)
    if estado is not None:
        consulta = consulta.where(UsuarioSistema.estado == estado)
    return consulta


async def buscar_por_correo(
    correo: str, session: AsyncSession | None = None
) -> UsuarioSistema | None:
    async with session_scope(session) as s:
        return await s.scalar(select(UsuarioSistema).where(UsuarioSistema.correo == correo))


async def buscar_por_id(
    id_usuario: int, session: AsyncSession | None = None
) -> UsuarioSistema | None:
    async with session_scope(session) as s:
        return await s.scalar(select(UsuarioSistema).where(UsuarioSistema.id_usuario == id_usuario))


async def listar(
    buscar: str | None = None,
    rol: str | None = None,
    estado: str | None = None,
    limite: int | None = None,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> list[UsuarioSistema]:
    async with session_scope(session) as s:
        consulta = _filtrar(select(UsuarioSistema), buscar, rol, estado)
        consulta = consulta.order_by(UsuarioSistema.nombre).offset(desplazamiento)
        if limite is not None:
            consulta = consulta.limit(limite)
        filas = await s.scalars(consulta)
        return list(filas)


async def contar(
    buscar: str | None = None,
    rol: str | None = None,
    estado: str | None = None,
    session: AsyncSession | None = None,
) -> int:
    async with session_scope(session) as s:
        consulta = _filtrar(select(func.count()).select_from(UsuarioSistema), buscar, rol, estado)
        total = await s.scalar(consulta)
        return int(total or 0)


async def insertar(
    nombre: str,
    correo: str,
    contrasena_hash: str,
    rol: str,
    session: AsyncSession | None = None,
) -> UsuarioSistema:
    async with session_scope(session) as s:
        usuario = UsuarioSistema(
            nombre=nombre,
            correo=correo,
            contrasena_hash=contrasena_hash,
            rol=rol,
            estado='ACTIVO',
        )
        s.add(usuario)
        await s.flush()
        return usuario


async def actualizar(
    id_usuario: int,
    nombre: str,
    rol: str,
    estado: str,
    session: AsyncSession | None = None,
) -> UsuarioSistema | None:
    async with session_scope(session) as s:
        usuario = await s.scalar(
            select(UsuarioSistema).where(UsuarioSistema.id_usuario == id_usuario)
        )
        if usuario is None:
            return None
        usuario.nombre = nombre
        usuario.rol = rol
        usuario.estado = estado
        await s.flush()
        return usuario


async def cambiar_contrasena(
    id_usuario: int, contrasena_hash: str, session: AsyncSession | None = None
) -> bool:
    async with session_scope(session) as s:
        usuario = await s.scalar(
            select(UsuarioSistema).where(UsuarioSistema.id_usuario == id_usuario)
        )
        if usuario is None:
            return False
        usuario.contrasena_hash = contrasena_hash
        await s.flush()
        return True
