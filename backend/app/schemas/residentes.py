from pydantic import BaseModel, Field


class CrearResidente(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    documento: str = Field(min_length=1, max_length=20)
    id_apartamento: int = Field(gt=0)


class ActualizarResidente(CrearResidente):
    pass


class ResidenteOut(BaseModel):
    id_residente: int
    nombre: str
    apellido: str
    documento: str
    id_apartamento: int
    id_torre: int
    torre: str
    numero: str
    estado: str
    muestras: int
    tiene_autorizacion: bool


class RegistrarAutorizacion(BaseModel):
    aceptada: bool
    finalidades: str = Field(min_length=1)


class AutorizacionOut(BaseModel):
    id_residente: int
    aceptada: bool
    finalidades: str
    version_politica: str


class PatronesOut(BaseModel):
    id_residente: int
    agregados: int
    total: int
