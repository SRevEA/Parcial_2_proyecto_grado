from datetime import datetime

from pydantic import BaseModel


class ResidenteReconocido(BaseModel):
    id_residente: int
    nombre: str
    apellido: str
    torre: str
    numero: str


class IntentoOut(BaseModel):
    id_registro: int
    id_punto: int
    resultado: str
    similitud: float
    umbral: float
    residente: ResidenteReconocido | None = None
    capturado_en: datetime
    fecha_hora: datetime
    segundos_respuesta: float
