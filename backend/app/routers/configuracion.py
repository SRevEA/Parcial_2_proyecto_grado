from fastapi import APIRouter

from ..lib.dependencias import Administrador, Sesion, Usuario
from ..schemas.comunes import Pagina, Respuesta
from ..schemas.configuracion import ClaveValor, NuevoValor
from ..services import configuracion as servicio

router = APIRouter(prefix='/configuracion', tags=['configuracion'])


@router.get('', response_model=Respuesta[Pagina[ClaveValor]])
async def listar(_: Usuario, sesion: Sesion) -> Respuesta[Pagina[ClaveValor]]:
    items = await servicio.listar(session=sesion)
    return Respuesta(data=Pagina(items=items, total=len(items)))


@router.put('/{clave}', response_model=Respuesta[ClaveValor])
async def establecer(_: Administrador, clave: str, datos: NuevoValor) -> Respuesta[ClaveValor]:
    return Respuesta(data=await servicio.establecer(clave, datos.valor))
