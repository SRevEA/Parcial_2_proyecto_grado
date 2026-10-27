from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from ..lib.dependencias import Punto
from ..schemas.comunes import Respuesta
from ..schemas.reconocimiento import IntentoOut
from ..services import reconocimiento as servicio

router = APIRouter(prefix='/reconocimiento', tags=['reconocimiento'])


@router.post('/intentos', response_model=Respuesta[IntentoOut], status_code=201)
async def registrar_intento(
    punto: Punto,
    imagen: Annotated[UploadFile, File()],
    capturado_en: Annotated[datetime | None, Form()] = None,
) -> Respuesta[IntentoOut]:
    marca = capturado_en or datetime.now(UTC)
    if marca.tzinfo is None:
        marca = marca.replace(tzinfo=UTC)
    intento = await servicio.procesar(punto.id_punto, await imagen.read(), marca)
    return Respuesta(statusCode=201, data=intento)
