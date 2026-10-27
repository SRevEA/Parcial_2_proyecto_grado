import contextlib
from typing import Any

import cv2
from numpy.typing import NDArray

VENTANA = 'Punto de acceso'
VERDE = (0, 200, 0)
ROJO = (0, 0, 220)
AMBAR = (0, 180, 255)
GRIS = (160, 160, 160)
PUNTOS = 5


def dibujar(
    cuadro: NDArray[Any],
    caras: list[NDArray[Any]],
    estado: str,
    color: tuple[int, int, int],
    fps: float = 0.0,
) -> NDArray[Any]:
    for cara in caras:
        x, y, w, h = (int(v) for v in cara[:4])
        cv2.rectangle(cuadro, (x, y), (x + w, y + h), color, 2)
        for i in range(PUNTOS):
            cv2.circle(cuadro, (int(cara[4 + i * 2]), int(cara[5 + i * 2])), 3, color, -1)

    ancho = cuadro.shape[1]
    cv2.rectangle(cuadro, (0, 0), (ancho, 34), (20, 20, 20), -1)
    cv2.putText(cuadro, estado, (10, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
    cv2.putText(
        cuadro,
        f'{fps:.0f} fps - q para salir',
        (ancho - 210, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        GRIS,
        1,
        cv2.LINE_AA,
    )
    return cuadro


def disponible() -> bool:
    try:
        cv2.namedWindow(VENTANA, cv2.WINDOW_AUTOSIZE)
        cv2.destroyWindow(VENTANA)
    except cv2.error:
        return False
    return True


def mostrar(cuadro: NDArray[Any]) -> bool:
    cv2.imshow(VENTANA, cuadro)
    return (cv2.waitKey(1) & 0xFF) not in (ord('q'), 27)


def cerrar() -> None:
    with contextlib.suppress(cv2.error):
        cv2.destroyAllWindows()
