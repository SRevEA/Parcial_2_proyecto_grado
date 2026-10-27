from datetime import datetime

from pydantic import BaseModel


class RegistroOut(BaseModel):
    id_registro: int
    id_punto: int
    resultado: str
    similitud: float | None = None
    id_residente: int | None = None
    nombre_residente: str | None = None
    torre: str | None = None
    numero: str | None = None
    capturado_en: datetime
    fecha_hora: datetime
    segundos_respuesta: float
    tiene_evidencia: bool


class EvidenciaOut(BaseModel):
    id_evidencia: int
    id_registro: int
    url: str
    hash_sha256: str
    fecha_expiracion: datetime
