import os
import urllib.request
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

CARPETA_MODELOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'modelos'
)

MODELOS = {
    'face_detection_yunet_2023mar.onnx': (
        'https://github.com/opencv/opencv_zoo/raw/main/models/'
        'face_detection_yunet/face_detection_yunet_2023mar.onnx'
    ),
    'face_recognition_sface_2021dec.onnx': (
        'https://github.com/opencv/opencv_zoo/raw/main/models/'
        'face_recognition_sface/face_recognition_sface_2021dec.onnx'
    ),
}

ANCHO, ALTO = 640, 480

_detector: cv2.FaceDetectorYN | None = None
_reconocedor: cv2.FaceRecognizerSF | None = None


def descargar_modelos() -> tuple[str, str]:
    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    for nombre, url in MODELOS.items():
        ruta = os.path.join(CARPETA_MODELOS, nombre)
        if not os.path.exists(ruta) or os.path.getsize(ruta) < 1_000:
            urllib.request.urlretrieve(url, ruta)
    return (
        os.path.join(CARPETA_MODELOS, 'face_detection_yunet_2023mar.onnx'),
        os.path.join(CARPETA_MODELOS, 'face_recognition_sface_2021dec.onnx'),
    )


def _motor() -> tuple[cv2.FaceDetectorYN, cv2.FaceRecognizerSF]:
    global _detector, _reconocedor
    if _detector is None or _reconocedor is None:
        ruta_det, ruta_rec = descargar_modelos()
        _detector = cv2.FaceDetectorYN.create(ruta_det, '', (ANCHO, ALTO), 0.8, 0.3, 5_000)
        _reconocedor = cv2.FaceRecognizerSF.create(ruta_rec, '')
    return _detector, _reconocedor


def decodificar(datos: bytes) -> NDArray[np.uint8] | None:
    imagen = cv2.imdecode(np.frombuffer(datos, dtype=np.uint8), cv2.IMREAD_COLOR)
    if imagen is None:
        return None
    return imagen.astype(np.uint8)


def preparar(imagen: NDArray[np.uint8]) -> NDArray[np.uint8]:
    alto, ancho = imagen.shape[:2]
    escalada: NDArray[Any] = imagen
    if max(alto, ancho) > 1_280:
        escala = 1_280 / max(alto, ancho)
        escalada = cv2.resize(imagen, (int(ancho * escala), int(alto * escala)))
    suavizada = cv2.bilateralFilter(escalada, 5, 50, 50)
    lab = cv2.cvtColor(suavizada, cv2.COLOR_BGR2LAB)
    canales = list(cv2.split(lab))
    canales[0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(canales[0])
    return cv2.cvtColor(cv2.merge(canales), cv2.COLOR_LAB2BGR).astype(np.uint8)


def detectar(imagen: NDArray[np.uint8]) -> list[NDArray[np.float32]]:
    detector, _ = _motor()
    alto, ancho = imagen.shape[:2]
    detector.setInputSize((ancho, alto))
    _, caras = detector.detect(imagen)
    return [] if caras is None else list(caras)


def extraer_vector(imagen: NDArray[np.uint8], cara: NDArray[np.float32]) -> list[float]:
    _, reconocedor = _motor()
    alineada = reconocedor.alignCrop(imagen, cara)
    crudo = reconocedor.feature(alineada).flatten().astype(np.float32)
    norma = float(np.linalg.norm(crudo))
    if norma == 0.0:
        return [float(v) for v in crudo]
    return [float(v) for v in crudo / norma]


def vector_de_rostro_unico(datos: bytes) -> tuple[list[float] | None, int]:
    imagen = decodificar(datos)
    if imagen is None:
        return None, 0
    lista = preparar(imagen)
    caras = detectar(lista)
    if len(caras) != 1:
        return None, len(caras)
    return extraer_vector(lista, caras[0]), 1
