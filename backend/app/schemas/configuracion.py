from pydantic import BaseModel, Field


class ClaveValor(BaseModel):
    clave: str
    valor: str
    descripcion: str | None = None


class NuevoValor(BaseModel):
    valor: str = Field(min_length=1)
