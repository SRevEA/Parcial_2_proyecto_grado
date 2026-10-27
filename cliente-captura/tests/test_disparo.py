from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from cliente import disparo
from cliente.config import settings

RELOJ = 1_000.0


def cara(x: float = 100.0, y: float = 100.0, lado: float = 200.0) -> NDArray[Any]:
    return np.array([x, y, lado, lado] + [0.0] * 10 + [0.99], dtype=np.float32)


@pytest.fixture(autouse=True)
def _limpio() -> None:
    disparo._centro = None
    disparo._lado = 0.0
    disparo._quieto_desde = 0.0
    disparo._ultimo_visto = 0.0
    disparo._ultimo_envio = 0.0
    disparo._ya_enviado = False


def quietos(desde: float, segundos: float, x: float = 100.0) -> tuple[int, float]:
    envios = 0
    reloj = desde
    while reloj < desde + segundos:
        reloj += 0.033
        if disparo.evaluar([cara(x=x)], reloj, False).enviar:
            envios += 1
    return envios, reloj


def sin_rostro(desde: float, segundos: float) -> float:
    reloj = desde
    while reloj < desde + segundos:
        reloj += 0.033
        disparo.evaluar([], reloj, False)
    return reloj


def test_sin_rostro_no_envia() -> None:
    decision = disparo.evaluar([], RELOJ, False)
    assert decision.enviar is False
    assert decision.etiqueta == 'Sin rostro'


def test_no_envia_antes_del_umbral() -> None:
    disparo.evaluar([cara()], RELOJ, False)
    antes = settings.SEGUNDOS_ESTABLE - 0.5
    envios, _ = quietos(RELOJ, antes)
    assert envios == 0


def test_envia_una_sola_vez_al_quedarse_quieto() -> None:
    disparo.evaluar([cara()], RELOJ, False)
    envios, _ = quietos(RELOJ, settings.SEGUNDOS_ESTABLE + 5.0)
    assert envios == 1


def test_moverse_poco_no_vuelve_a_enviar() -> None:
    disparo.evaluar([cara()], RELOJ, False)
    envios, reloj = quietos(RELOJ, settings.SEGUNDOS_ESTABLE + 0.5)
    assert envios == 1
    corrido, _ = quietos(reloj, 5.0, x=108.0)
    assert corrido == 0


def test_si_el_rostro_se_va_y_vuelve_es_otro_intento() -> None:
    disparo.evaluar([cara()], RELOJ, False)
    envios, reloj = quietos(RELOJ, settings.SEGUNDOS_ESTABLE + 0.5)
    assert envios == 1

    reloj = sin_rostro(reloj, settings.SEGUNDOS_SIN_ROSTRO + 0.5)
    reloj += settings.SEGUNDOS_ENTRE_INTENTOS
    disparo.evaluar([cara(x=400.0)], reloj, False)
    nuevos, _ = quietos(reloj, settings.SEGUNDOS_ESTABLE + 0.5, x=400.0)
    assert nuevos == 1


def test_dos_rostros_no_envian() -> None:
    decision = disparo.evaluar([cara(), cara(x=500.0)], RELOJ, False)
    assert decision.enviar is False
    assert '2 rostros' in decision.etiqueta


def test_no_envia_mientras_el_hilo_esta_ocupado() -> None:
    disparo.evaluar([cara()], RELOJ, False)
    reloj = RELOJ + settings.SEGUNDOS_ESTABLE + 0.1
    ocupada = disparo.evaluar([cara()], reloj, True)
    assert ocupada.enviar is False
    assert ocupada.etiqueta == 'Enviando...'
    assert disparo.evaluar([cara()], reloj, False).enviar is True
