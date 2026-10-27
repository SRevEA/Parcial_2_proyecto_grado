from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.db import session_scope
from ..lib.errors import conflicto, no_encontrado, precondicion, validacion
from ..repositories import apartamento as repo_apartamento
from ..repositories import torre as repo_torre
from ..repositories.apartamento import FilaApartamento
from ..schemas.catalogo import ApartamentoOut, TorreOut


def _salida_apartamento(fila: FilaApartamento) -> ApartamentoOut:
    return ApartamentoOut(
        id_apartamento=fila.apartamento.id_apartamento,
        id_torre=fila.apartamento.id_torre,
        torre=fila.torre,
        numero=fila.apartamento.numero,
        residentes=fila.residentes,
    )


def _limpiar(texto: str, que: str) -> str:
    limpio = ' '.join(texto.split())
    if not limpio:
        raise validacion(f'El {que} no puede quedar vacio')
    return limpio


async def listar_torres(session: AsyncSession | None = None) -> list[TorreOut]:
    filas = await repo_torre.listar(session=session)
    return [
        TorreOut(
            id_torre=fila.torre.id_torre,
            nombre=fila.torre.nombre,
            apartamentos=fila.apartamentos,
        )
        for fila in filas
    ]


async def crear_torre(nombre: str) -> TorreOut:
    limpio = _limpiar(nombre, 'nombre de la torre')
    async with session_scope() as s:
        if await repo_torre.buscar_por_nombre(limpio, session=s) is not None:
            raise conflicto('Ya existe una torre con ese nombre')
        torre = await repo_torre.insertar(limpio, session=s)
        return TorreOut(id_torre=torre.id_torre, nombre=torre.nombre, apartamentos=0)


async def renombrar_torre(id_torre: int, nombre: str) -> TorreOut:
    limpio = _limpiar(nombre, 'nombre de la torre')
    async with session_scope() as s:
        otra = await repo_torre.buscar_por_nombre(limpio, session=s)
        if otra is not None and otra.id_torre != id_torre:
            raise conflicto('Otra torre ya tiene ese nombre')
        torre = await repo_torre.renombrar(id_torre, limpio, session=s)
        if torre is None:
            raise no_encontrado('La torre no existe')
        return TorreOut(
            id_torre=torre.id_torre,
            nombre=torre.nombre,
            apartamentos=await repo_torre.contar_apartamentos(id_torre, session=s),
        )


async def eliminar_torre(id_torre: int) -> None:
    async with session_scope() as s:
        if await repo_torre.buscar_por_id(id_torre, session=s) is None:
            raise no_encontrado('La torre no existe')
        apartamentos = await repo_torre.contar_apartamentos(id_torre, session=s)
        if apartamentos > 0:
            raise precondicion(
                f'La torre tiene {apartamentos} apartamentos. Hay que borrarlos primero.'
            )
        await repo_torre.eliminar(id_torre, session=s)


async def listar_apartamentos(
    id_torre: int | None = None, session: AsyncSession | None = None
) -> list[ApartamentoOut]:
    filas = await repo_apartamento.listar(id_torre=id_torre, session=session)
    return [_salida_apartamento(fila) for fila in filas]


async def crear_apartamento(id_torre: int, numero: str) -> ApartamentoOut:
    limpio = _limpiar(numero, 'numero del apartamento')
    async with session_scope() as s:
        torre = await repo_torre.buscar_por_id(id_torre, session=s)
        if torre is None:
            raise no_encontrado('La torre no existe')
        if await repo_apartamento.buscar(id_torre, limpio, session=s) is not None:
            raise conflicto('Esa torre ya tiene un apartamento con ese numero')
        apartamento = await repo_apartamento.insertar(id_torre, limpio, session=s)
        return ApartamentoOut(
            id_apartamento=apartamento.id_apartamento,
            id_torre=id_torre,
            torre=torre.nombre,
            numero=apartamento.numero,
            residentes=0,
        )


async def cambiar_numero(id_apartamento: int, numero: str) -> ApartamentoOut:
    limpio = _limpiar(numero, 'numero del apartamento')
    async with session_scope() as s:
        actual = await repo_apartamento.buscar_por_id(id_apartamento, session=s)
        if actual is None:
            raise no_encontrado('El apartamento no existe')
        otro = await repo_apartamento.buscar(actual.apartamento.id_torre, limpio, session=s)
        if otro is not None and otro.id_apartamento != id_apartamento:
            raise conflicto('Esa torre ya tiene un apartamento con ese numero')
        if await repo_apartamento.cambiar_numero(id_apartamento, limpio, session=s) is None:
            raise no_encontrado('El apartamento no existe')
        fila = await repo_apartamento.buscar_por_id(id_apartamento, session=s)
        if fila is None:
            raise no_encontrado('El apartamento no existe')
        return _salida_apartamento(fila)


async def eliminar_apartamento(id_apartamento: int) -> None:
    async with session_scope() as s:
        if await repo_apartamento.buscar_por_id(id_apartamento, session=s) is None:
            raise no_encontrado('El apartamento no existe')
        residentes = await repo_apartamento.contar_residentes(id_apartamento, session=s)
        if residentes > 0:
            raise precondicion(
                f'El apartamento tiene {residentes} residentes registrados. '
                'Hay que reubicarlos o suprimirlos primero.'
            )
        await repo_apartamento.eliminar(id_apartamento, session=s)
