from typing import Any, NamedTuple

from numpy.typing import NDArray

from .config import settings


class Decision(NamedTuple):
    enviar: bool
    etiqueta: str


_centro: tuple[float, float] | None = None
_lado = 0.0
_quieto_desde = 0.0
_ultimo_visto = 0.0
_ultimo_envio = 0.0
_ya_enviado = False


def _medidas(cara: NDArray[Any]) -> tuple[tuple[float, float], float]:
    x, y, ancho, alto = (float(v) for v in cara[:4])
    return (x + ancho / 2, y + alto / 2), max(ancho, alto)


def _se_movio(centro: tuple[float, float], lado: float) -> bool:
    if _centro is None:
        return True
    margen = lado * settings.MOVIMIENTO_TOLERADO
    return (
        abs(centro[0] - _centro[0]) > margen
        or abs(centro[1] - _centro[1]) > margen
        or abs(lado - _lado) > margen
    )


def _olvidar() -> None:
    global _centro, _lado, _ya_enviado
    _centro = None
    _lado = 0.0
    _ya_enviado = False


def evaluar(caras: list[NDArray[Any]], ahora: float, ocupado: bool) -> Decision:
    global _centro, _lado, _quieto_desde, _ultimo_visto, _ultimo_envio, _ya_enviado

    if len(caras) != 1:
        if ahora - _ultimo_visto >= settings.SEGUNDOS_SIN_ROSTRO:
            _olvidar()
        if not caras:
            return Decision(False, 'Sin rostro')
        return Decision(False, f'{len(caras)} rostros: debe haber uno solo')

    _ultimo_visto = ahora
    centro, lado = _medidas(caras[0])

    if _se_movio(centro, lado):
        _centro, _lado, _quieto_desde = centro, lado, ahora
        return Decision(False, 'Mira al frente y quedate quieto')

    _centro, _lado = centro, lado

    if _ya_enviado:
        return Decision(False, '')

    falta = settings.SEGUNDOS_ESTABLE - (ahora - _quieto_desde)
    if falta > 0:
        return Decision(False, f'Quieto... {falta:.1f}s')

    if ocupado:
        return Decision(False, 'Enviando...')

    espera = settings.SEGUNDOS_ENTRE_INTENTOS - (ahora - _ultimo_envio)
    if espera > 0:
        return Decision(False, f'Listo en {espera:.0f}s')

    _ultimo_envio = ahora
    _ya_enviado = True
    return Decision(True, '')
