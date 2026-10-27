from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.errors import no_encontrado, validacion
from ..repositories import configuracion as repo
from ..schemas.configuracion import ClaveValor
from ..types.comunes import CLAVE_DIAS_EVIDENCIA, CLAVE_UMBRAL, CLAVE_VERSION_POLITICA


async def listar(session: AsyncSession | None = None) -> list[ClaveValor]:
    return [
        ClaveValor.model_validate(c, from_attributes=True)
        for c in await repo.listar(session=session)
    ]


async def umbral(session: AsyncSession | None = None) -> float:
    valor = await repo.obtener(CLAVE_UMBRAL, session=session)
    if valor is None:
        raise no_encontrado(f'Falta la configuracion {CLAVE_UMBRAL}')
    return float(valor)


async def dias_conservacion(session: AsyncSession | None = None) -> int:
    valor = await repo.obtener(CLAVE_DIAS_EVIDENCIA, session=session)
    if valor is None:
        raise no_encontrado(f'Falta la configuracion {CLAVE_DIAS_EVIDENCIA}')
    return int(valor)


async def version_politica(session: AsyncSession | None = None) -> str:
    valor = await repo.obtener(CLAVE_VERSION_POLITICA, session=session)
    if valor is None:
        raise no_encontrado(f'Falta la configuracion {CLAVE_VERSION_POLITICA}')
    return valor


async def establecer(clave: str, valor: str) -> ClaveValor:
    if clave == CLAVE_UMBRAL:
        numero = float(valor)
        if not 0.0 < numero < 1.0:
            raise validacion('El umbral de similitud coseno debe estar entre 0 y 1')
    if clave == CLAVE_DIAS_EVIDENCIA and int(valor) < 1:
        raise validacion('El periodo de conservacion debe ser de al menos un dia')
    if not await repo.establecer(clave, valor):
        raise no_encontrado('Esa clave de configuracion no existe')
    return ClaveValor(clave=clave, valor=valor)
