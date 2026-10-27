import os
from typing import Any

import cv2
from numpy.typing import NDArray

RUTA_MODELO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'modelos',
    'face_detection_yunet_2023mar.onnx',
)

ANCHO_DETECCION = 640
COORDENADAS = 14

_detector: cv2.FaceDetectorYN | None = None


def _motor() -> cv2.FaceDetectorYN:
    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(RUTA_MODELO, '', (640, 480), 0.8, 0.3, 5_000)
    return _detector


def detectar(cuadro: NDArray[Any]) -> list[NDArray[Any]]:
    ancho = cuadro.shape[1]
    factor = 1.0 if ancho <= ANCHO_DETECCION else ANCHO_DETECCION / ancho
    chico = cuadro if factor == 1.0 else cv2.resize(cuadro, (0, 0), fx=factor, fy=factor)

    detector = _motor()
    detector.setInputSize((chico.shape[1], chico.shape[0]))
    _, caras = detector.detect(chico)
    if caras is None:
        return []
    if factor == 1.0:
        return list(caras)
    escaladas = []
    for cara in caras:
        copia = cara.copy()
        copia[:COORDENADAS] /= factor
        escaladas.append(copia)
    return escaladas
