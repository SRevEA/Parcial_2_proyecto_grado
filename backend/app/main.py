import asyncio
import contextlib
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .jobs.evidencias import purgar_periodicamente
from .lib import almacenamiento
from .lib.errors import ErrorApi
from .routers import (
    accesos,
    auth,
    catalogo,
    configuracion,
    reconocimiento,
    residentes,
    usuarios,
)


@contextlib.asynccontextmanager
async def ciclo(_: FastAPI) -> AsyncIterator[None]:
    tarea = asyncio.create_task(purgar_periodicamente())
    try:
        yield
    finally:
        tarea.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await tarea
        await almacenamiento.cerrar()


app = FastAPI(
    title='API del sistema de reconocimiento facial',
    version='1.0.0',
    docs_url='/api/v1/docs',
    openapi_url='/api/v1/openapi.json',
    lifespan=ciclo,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api = APIRouter(prefix='/api/v1')
api.include_router(auth.router)
api.include_router(usuarios.router)
api.include_router(residentes.router)
api.include_router(reconocimiento.router)
api.include_router(accesos.router)
api.include_router(configuracion.router)
api.include_router(catalogo.router)
app.include_router(api)


def _cuerpo_error(status_code: int, code: str, message: str, details: list[Any]) -> dict[str, Any]:
    return {
        'success': False,
        'statusCode': status_code,
        'error': {'code': code, 'message': message, 'details': details},
    }


@app.exception_handler(ErrorApi)
async def manejar_error_api(_: Request, exc: ErrorApi) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_cuerpo_error(exc.status_code, exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def manejar_validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {'campo': '.'.join(str(p) for p in e.get('loc', ())), 'detalle': e.get('msg', '')}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_cuerpo_error(422, 'VALIDATION_ERROR', 'Validation failed', details),
    )


@app.exception_handler(StarletteHTTPException)
async def manejar_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    codigos = {
        401: 'UNAUTHENTICATED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=_cuerpo_error(
            exc.status_code, codigos.get(exc.status_code, 'HTTP_ERROR'), str(exc.detail), []
        ),
    )


@app.exception_handler(Exception)
async def manejar_no_esperado(_: Request, __: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_cuerpo_error(500, 'INTERNAL_ERROR', 'Error interno', []),
    )


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
