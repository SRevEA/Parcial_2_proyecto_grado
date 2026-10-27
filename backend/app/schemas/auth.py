from pydantic import BaseModel, EmailStr, Field


class Credenciales(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=1)


class Sesion(BaseModel):
    token: str
    id_usuario: int
    nombre: str
    rol: str


class CambioContrasena(BaseModel):
    actual: str = Field(min_length=1)
    nueva: str = Field(min_length=8)
