from typing import Any


class ErrorApi(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []


def no_autenticado(message: str = 'Credenciales invalidas') -> ErrorApi:
    return ErrorApi(401, 'UNAUTHENTICATED', message)


def sin_permiso(message: str = 'No tiene permiso para esta operacion') -> ErrorApi:
    return ErrorApi(403, 'FORBIDDEN', message)


def no_encontrado(message: str = 'Recurso no encontrado') -> ErrorApi:
    return ErrorApi(404, 'NOT_FOUND', message)


def conflicto(message: str, details: list[Any] | None = None) -> ErrorApi:
    return ErrorApi(409, 'CONFLICT', message, details)


def precondicion(message: str, details: list[Any] | None = None) -> ErrorApi:
    return ErrorApi(412, 'PRECONDITION_FAILED', message, details)


def validacion(message: str = 'Validation failed', details: list[Any] | None = None) -> ErrorApi:
    return ErrorApi(422, 'VALIDATION_ERROR', message, details)
