import queue
import sqlite3
import threading
from datetime import datetime
from typing import Any

import httpx

from . import api, cola
from .config import settings

Resultado = tuple[str, Any]

_por_enviar: queue.Queue[tuple[bytes, datetime] | None] = queue.Queue(maxsize=1)
_resultados: queue.Queue[Resultado] = queue.Queue()
_hilo: threading.Thread | None = None


def _vaciar_cola(conexion: sqlite3.Connection) -> None:
    for id_pendiente, imagen, capturado in cola.pendientes(conexion):
        try:
            api.enviar_intento(imagen, datetime.fromisoformat(capturado))
        except httpx.RequestError:
            return
        except httpx.HTTPStatusError as error:
            cola.descartar(conexion, id_pendiente)
            _resultados.put(('descartado', error.response.status_code))
            continue
        cola.descartar(conexion, id_pendiente)
        _resultados.put(('reenviado', id_pendiente))


def _trabajar() -> None:
    conexion = cola.abrir(settings.RUTA_COLA)
    pendientes = cola.cuantos(conexion)
    if pendientes:
        _resultados.put(('encolados', pendientes))
    try:
        while True:
            try:
                tarea = _por_enviar.get(timeout=settings.SEGUNDOS_REINTENTO_COLA)
            except queue.Empty:
                _vaciar_cola(conexion)
                continue
            if tarea is None:
                return
            imagen, capturado_en = tarea
            try:
                _resultados.put(('ok', api.enviar_intento(imagen, capturado_en)))
            except httpx.RequestError as error:
                cola.encolar(conexion, imagen, capturado_en)
                _resultados.put(('sin_conexion', error.__class__.__name__))
            except httpx.HTTPStatusError as error:
                _resultados.put(('rechazado', error.response.status_code))
    finally:
        conexion.close()


def iniciar() -> None:
    global _hilo
    _hilo = threading.Thread(target=_trabajar, daemon=True)
    _hilo.start()


def ocupado() -> bool:
    return _por_enviar.full()


def enviar(imagen: bytes, capturado_en: datetime) -> bool:
    try:
        _por_enviar.put_nowait((imagen, capturado_en))
    except queue.Full:
        return False
    return True


def resultados() -> list[Resultado]:
    salida = []
    while True:
        try:
            salida.append(_resultados.get_nowait())
        except queue.Empty:
            return salida


def detener() -> None:
    if _hilo is None:
        return
    try:
        _por_enviar.put_nowait(None)
    except queue.Full:
        pass
    _hilo.join(timeout=2)
