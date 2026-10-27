import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from ..lib import almacenamiento, vision
from ..lib.db import session_scope
from ..lib.errors import conflicto, no_encontrado, precondicion, validacion
from ..models.residente import Residente
from ..repositories import apartamento as repo_apartamento
from ..repositories import autorizacion_datos as repo_autorizacion
from ..repositories import evidencia_fotografica as repo_evidencia
from ..repositories import patron_facial as repo_patron
from ..repositories import residente as repo
from ..schemas.residentes import (
    ActualizarResidente,
    AutorizacionOut,
    CrearResidente,
    PatronesOut,
    RegistrarAutorizacion,
    ResidenteOut,
)
from ..services import configuracion as servicio_configuracion


def _salida(
    residente: Residente,
    id_torre: int,
    torre: str,
    numero: str,
    muestras: int,
    autorizado: bool,
) -> ResidenteOut:
    return ResidenteOut(
        id_residente=residente.id_residente,
        nombre=residente.nombre,
        apellido=residente.apellido,
        documento=residente.documento,
        id_apartamento=residente.id_apartamento,
        id_torre=id_torre,
        torre=torre,
        numero=numero,
        estado=residente.estado,
        muestras=muestras,
        tiene_autorizacion=autorizado,
    )


async def _una_salida(residente: Residente, session: AsyncSession) -> ResidenteOut:
    apto = await repo_apartamento.buscar_por_id(residente.id_apartamento, session=session)
    muestras = await repo_patron.contar_por_residente(residente.id_residente, session=session)
    autorizacion = await repo_autorizacion.buscar_por_residente(
        residente.id_residente, session=session
    )
    return _salida(
        residente,
        apto.apartamento.id_torre if apto else 0,
        apto.torre if apto else '',
        apto.apartamento.numero if apto else '',
        muestras,
        autorizacion is not None and autorizacion.aceptada,
    )


async def listar(
    estado: str | None = None,
    buscar: str | None = None,
    autorizacion: bool | None = None,
    patrones: bool | None = None,
    limite: int = 50,
    desplazamiento: int = 0,
    session: AsyncSession | None = None,
) -> tuple[list[ResidenteOut], int]:
    async with session_scope(session) as s:
        filas = await repo.listar(
            estado=estado,
            buscar=buscar,
            autorizacion=autorizacion,
            patrones=patrones,
            limite=limite,
            desplazamiento=desplazamiento,
            session=s,
        )
        total = await repo.contar(
            estado=estado,
            buscar=buscar,
            autorizacion=autorizacion,
            patrones=patrones,
            session=s,
        )

    return [
        _salida(
            f.residente, f.id_torre or 0, f.torre or '', f.numero or '', f.muestras, f.autorizado
        )
        for f in filas
    ], total


async def obtener(id_residente: int, session: AsyncSession | None = None) -> ResidenteOut:
    async with session_scope(session) as s:
        residente = await repo.buscar_por_id(id_residente, session=s)
        if residente is None:
            raise no_encontrado('El residente no existe')
        return await _una_salida(residente, s)


async def _exigir_apartamento(id_apartamento: int, session: AsyncSession) -> None:
    if await repo_apartamento.buscar_por_id(id_apartamento, session=session) is None:
        raise no_encontrado('Ese apartamento no esta en el catalogo')


async def crear(datos: CrearResidente) -> ResidenteOut:
    async with session_scope() as s:
        if await repo.buscar_por_documento(datos.documento, session=s) is not None:
            raise conflicto('Ya existe un residente con ese documento')
        await _exigir_apartamento(datos.id_apartamento, s)
        residente = await repo.insertar(
            datos.nombre,
            datos.apellido,
            datos.documento,
            datos.id_apartamento,
            session=s,
        )
        return await _una_salida(residente, s)


async def actualizar(id_residente: int, datos: ActualizarResidente) -> ResidenteOut:
    async with session_scope() as s:
        otro = await repo.buscar_por_documento(datos.documento, session=s)
        if otro is not None and otro.id_residente != id_residente:
            raise conflicto('Otro residente ya tiene ese documento')
        await _exigir_apartamento(datos.id_apartamento, s)
        residente = await repo.actualizar(
            id_residente,
            datos.nombre,
            datos.apellido,
            datos.documento,
            datos.id_apartamento,
            session=s,
        )
        if residente is None:
            raise no_encontrado('El residente no existe')
        return await _una_salida(residente, s)


async def cambiar_estado(id_residente: int, estado: str) -> ResidenteOut:
    async with session_scope() as s:
        if not await repo.cambiar_estado(id_residente, estado, session=s):
            raise no_encontrado('El residente no existe')
        residente = await repo.buscar_por_id(id_residente, session=s)
        if residente is None:
            raise no_encontrado('El residente no existe')
        return await _una_salida(residente, s)


async def registrar_autorizacion(
    id_residente: int, datos: RegistrarAutorizacion
) -> AutorizacionOut:
    if not datos.aceptada:
        raise validacion('Sin aceptacion expresa no se puede registrar la autorizacion')
    async with session_scope() as s:
        if await repo.buscar_por_id(id_residente, session=s) is None:
            raise no_encontrado('El residente no existe')
        if await repo_autorizacion.buscar_por_residente(id_residente, session=s) is not None:
            raise conflicto('Ese residente ya tiene autorizacion registrada')
        autorizacion = await repo_autorizacion.insertar(
            id_residente,
            datos.aceptada,
            datos.finalidades,
            await servicio_configuracion.version_politica(session=s),
            session=s,
        )
        return AutorizacionOut.model_validate(autorizacion, from_attributes=True)


async def capturar_patrones(id_residente: int, imagenes: list[bytes]) -> PatronesOut:
    async with session_scope() as s:
        if await repo.buscar_por_id(id_residente, session=s) is None:
            raise no_encontrado('El residente no existe')

        autorizacion = await repo_autorizacion.buscar_por_residente(id_residente, session=s)
        if autorizacion is None or not autorizacion.aceptada:
            raise precondicion(
                'No se puede capturar el patron facial sin la autorizacion del residente'
            )

        vectores: list[list[float]] = []
        rechazadas: list[dict[str, object]] = []
        for indice, datos in enumerate(imagenes):
            vector, cuantos = await asyncio.to_thread(vision.vector_de_rostro_unico, datos)
            if vector is None:
                rechazadas.append({'imagen': indice, 'rostros': cuantos})
                continue
            vectores.append(vector)

        if not vectores:
            raise validacion('Ninguna imagen tenia exactamente un rostro', rechazadas)

        agregados = await repo_patron.insertar_varios(id_residente, vectores, session=s)
        return PatronesOut(
            id_residente=id_residente,
            agregados=agregados,
            total=await repo_patron.contar_por_residente(id_residente, session=s),
        )


async def suprimir(id_residente: int) -> None:
    async with session_scope() as s:
        if await repo.buscar_por_id(id_residente, session=s) is None:
            raise no_encontrado('El residente no existe')

        evidencias = await repo_evidencia.listar_por_residente(id_residente, session=s)
        if evidencias:
            await almacenamiento.eliminar([e.ruta_archivo for e in evidencias])
            await repo_evidencia.eliminar_varias([e.id_evidencia for e in evidencias], session=s)

        await repo_patron.eliminar_por_residente(id_residente, session=s)
        await repo.eliminar(id_residente, session=s)
