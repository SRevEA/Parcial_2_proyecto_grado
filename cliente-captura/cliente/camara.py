from typing import Any

import cv2
from numpy.typing import NDArray

ANCHO, ALTO = 640, 480


def abrir(indice: int) -> cv2.VideoCapture:
    captura = cv2.VideoCapture(indice)
    captura.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
    captura.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
    if not captura.isOpened():
        raise RuntimeError(f'No se pudo abrir la camara {indice}')
    return captura


def leer(captura: cv2.VideoCapture) -> NDArray[Any] | None:
    ok, cuadro = captura.read()
    if not ok:
        return None
    return cuadro


def a_jpg(cuadro: NDArray[Any]) -> bytes:
    ok, buffer = cv2.imencode('.jpg', cuadro, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        raise RuntimeError('No se pudo codificar el cuadro a JPEG')
    return bytes(buffer.tobytes())
