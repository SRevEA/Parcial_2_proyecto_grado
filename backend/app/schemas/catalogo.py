from pydantic import BaseModel, Field


class CrearTorre(BaseModel):
    nombre: str = Field(min_length=1, max_length=20)


class TorreOut(BaseModel):
    id_torre: int
    nombre: str
    apartamentos: int


class CrearApartamento(BaseModel):
    numero: str = Field(min_length=1, max_length=20)


class ApartamentoOut(BaseModel):
    id_apartamento: int
    id_torre: int
    torre: str
    numero: str
    residentes: int
