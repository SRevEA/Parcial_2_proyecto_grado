import asyncio
import contextlib

TAMANO_COLA = 50

_suscriptores: set[asyncio.Queue[str]] = set()


def suscribir() -> asyncio.Queue[str]:
    cola: asyncio.Queue[str] = asyncio.Queue(maxsize=TAMANO_COLA)
    _suscriptores.add(cola)
    return cola


def cancelar(cola: asyncio.Queue[str]) -> None:
    _suscriptores.discard(cola)


def publicar(mensaje: str) -> None:
    for cola in list(_suscriptores):
        if cola.full():
            with contextlib.suppress(asyncio.QueueEmpty):
                cola.get_nowait()
        with contextlib.suppress(asyncio.QueueFull):
            cola.put_nowait(mensaje)


def cantidad_suscriptores() -> int:
    return len(_suscriptores)
