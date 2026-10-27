from datetime import datetime
from typing import Any

import httpx

from .config import settings

_CABECERAS = {
    'X-Punto-Id': str(settings.PUNTO_ACCESO_ID),
    'X-Punto-Api-Key': settings.PUNTO_ACCESO_API_KEY,
}


def enviar_intento(imagen: bytes, capturado_en: datetime) -> dict[str, Any]:
    respuesta = httpx.post(
        f'{settings.BACKEND_URL}/api/v1/reconocimiento/intentos',
        headers=_CABECERAS,
        files={'imagen': ('captura.jpg', imagen, 'image/jpeg')},
        data={'capturado_en': capturado_en.isoformat()},
        timeout=30,
    )
    respuesta.raise_for_status()
    cuerpo: dict[str, Any] = respuesta.json()
    return cuerpo


def esta_disponible() -> bool:
    try:
        return httpx.get(f'{settings.BACKEND_URL}/health', timeout=5).status_code == 200
    except httpx.HTTPError:
        return False
