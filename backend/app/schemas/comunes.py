from typing import Any

from pydantic import BaseModel


class Respuesta[T](BaseModel):
    success: bool = True
    statusCode: int = 200
    data: T


class DetalleError(BaseModel):
    code: str
    message: str
    details: list[Any] = []


class RespuestaError(BaseModel):
    success: bool = False
    statusCode: int
    error: DetalleError


class Pagina[T](BaseModel):
    items: list[T]
    total: int
