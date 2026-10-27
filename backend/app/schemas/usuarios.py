from pydantic import BaseModel, EmailStr, Field

from ..types.comunes import Estado, Rol


class CrearUsuario(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    correo: EmailStr
    contrasena: str = Field(min_length=8)
    rol: Rol


class ActualizarUsuario(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    rol: Rol
    estado: Estado


class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    rol: str
    estado: str
