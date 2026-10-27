import pytest

from app.lib.errors import ErrorApi
from app.repositories import autorizacion_datos as repo_autorizacion
from app.repositories import patron_facial as repo_patron
from app.repositories import residente as repo
from app.services import residentes as servicio
from tests.fakes import AutorizacionFalsa, ResidenteFalso


def _existe_residente(monkeypatch: pytest.MonkeyPatch) -> None:
    async def buscar(_: int, session: object = None) -> ResidenteFalso:
        return ResidenteFalso()

    monkeypatch.setattr(repo, 'buscar_por_id', buscar)


def _sin_autorizacion(monkeypatch: pytest.MonkeyPatch) -> None:
    async def buscar(_: int, session: object = None) -> None:
        return None

    monkeypatch.setattr(repo_autorizacion, 'buscar_por_residente', buscar)


def _con_autorizacion(monkeypatch: pytest.MonkeyPatch, aceptada: bool = True) -> None:
    async def buscar(_: int, session: object = None) -> AutorizacionFalsa:
        return AutorizacionFalsa(aceptada=aceptada)

    monkeypatch.setattr(repo_autorizacion, 'buscar_por_residente', buscar)


async def test_capturar_patrones_sin_autorizacion_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    _existe_residente(monkeypatch)
    _sin_autorizacion(monkeypatch)

    with pytest.raises(ErrorApi) as fallo:
        await servicio.capturar_patrones(1, [b'no-importa'])

    assert fallo.value.status_code == 412
    assert fallo.value.code == 'PRECONDITION_FAILED'


async def test_capturar_patrones_con_autorizacion_rechazada_falla(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _existe_residente(monkeypatch)
    _con_autorizacion(monkeypatch, aceptada=False)

    with pytest.raises(ErrorApi) as fallo:
        await servicio.capturar_patrones(1, [b'no-importa'])

    assert fallo.value.status_code == 412


async def test_capturar_patrones_sin_rostro_no_guarda_nada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _existe_residente(monkeypatch)
    _con_autorizacion(monkeypatch)
    monkeypatch.setattr(servicio.vision, 'vector_de_rostro_unico', lambda _: (None, 0))

    guardados: list[list[list[float]]] = []

    async def insertar(_: int, vectores: list[list[float]], session: object = None) -> int:
        guardados.append(vectores)
        return len(vectores)

    monkeypatch.setattr(repo_patron, 'insertar_varios', insertar)

    with pytest.raises(ErrorApi) as fallo:
        await servicio.capturar_patrones(1, [b'a', b'b'])

    assert fallo.value.code == 'VALIDATION_ERROR'
    assert guardados == []


async def test_capturar_patrones_guarda_los_vectores_validos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _existe_residente(monkeypatch)
    _con_autorizacion(monkeypatch)

    respuestas = iter([([0.1] * 128, 1), (None, 2), ([0.2] * 128, 1)])
    monkeypatch.setattr(servicio.vision, 'vector_de_rostro_unico', lambda _: next(respuestas))

    guardados: list[list[list[float]]] = []

    async def insertar(_: int, vectores: list[list[float]], session: object = None) -> int:
        guardados.append(vectores)
        return len(vectores)

    async def contar(_: int, session: object = None) -> int:
        return 2

    monkeypatch.setattr(repo_patron, 'insertar_varios', insertar)
    monkeypatch.setattr(repo_patron, 'contar_por_residente', contar)

    salida = await servicio.capturar_patrones(1, [b'a', b'b', b'c'])

    assert salida.agregados == 2
    assert len(guardados[0]) == 2


async def test_registrar_autorizacion_sin_aceptar_falla(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.schemas.residentes import RegistrarAutorizacion

    _existe_residente(monkeypatch)

    with pytest.raises(ErrorApi) as fallo:
        await servicio.registrar_autorizacion(
            1, RegistrarAutorizacion(aceptada=False, finalidades='x')
        )

    assert fallo.value.code == 'VALIDATION_ERROR'
