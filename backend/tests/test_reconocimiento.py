from datetime import UTC, datetime, timedelta

import pytest

from app.lib.errors import ErrorApi
from app.repositories import apartamento as repo_apartamento
from app.repositories import evidencia_fotografica as repo_evidencia
from app.repositories import patron_facial as repo_patron
from app.repositories import registro_acceso as repo_registro
from app.repositories import residente as repo_residente
from app.services import configuracion as servicio_configuracion
from app.services import reconocimiento as servicio
from tests.fakes import FilaApartamentoFalsa, RegistroFalso, ResidenteFalso

UMBRAL = 0.363


def _montar(
    monkeypatch: pytest.MonkeyPatch, parecido: tuple[int, float] | None
) -> dict[str, object]:
    capturado: dict[str, object] = {}

    monkeypatch.setattr(servicio.vision, 'vector_de_rostro_unico', lambda _: ([0.1] * 128, 1))

    async def umbral(session: object = None) -> float:
        return UMBRAL

    async def dias(session: object = None) -> int:
        return 30

    async def mas_parecido(_: list[float], session: object = None) -> tuple[int, float] | None:
        return parecido

    async def insertar_registro(**kwargs: object) -> RegistroFalso:
        capturado['registro'] = kwargs
        ahora = datetime.now(UTC)
        return RegistroFalso(
            resultado=str(kwargs['resultado']),
            id_residente=kwargs['id_residente'],  # type: ignore[arg-type]
            capturado_en=kwargs['capturado_en'],  # type: ignore[arg-type]
            fecha_hora=ahora,
        )

    async def subir(ruta: str, datos: bytes, tipo: str = 'image/jpeg') -> None:
        capturado['ruta_evidencia'] = ruta

    async def insertar_evidencia(**kwargs: object) -> object:
        capturado['evidencia'] = kwargs
        return object()

    async def buscar_residente(_: int, session: object = None) -> ResidenteFalso:
        return ResidenteFalso()

    async def buscar_apartamento(_: int, session: object = None) -> FilaApartamentoFalsa:
        return FilaApartamentoFalsa()

    monkeypatch.setattr(servicio_configuracion, 'umbral', umbral)
    monkeypatch.setattr(servicio_configuracion, 'dias_conservacion', dias)
    monkeypatch.setattr(repo_patron, 'mas_parecido', mas_parecido)
    monkeypatch.setattr(repo_registro, 'insertar', insertar_registro)
    monkeypatch.setattr(servicio.almacenamiento, 'subir', subir)
    monkeypatch.setattr(repo_evidencia, 'insertar', insertar_evidencia)
    monkeypatch.setattr(repo_residente, 'buscar_por_id', buscar_residente)
    monkeypatch.setattr(repo_apartamento, 'buscar_por_id', buscar_apartamento)
    return capturado


async def test_similitud_sobre_el_umbral_reconoce(monkeypatch: pytest.MonkeyPatch) -> None:
    _montar(monkeypatch, (1, 0.90))
    intento = await servicio.procesar(1, b'jpeg', datetime.now(UTC))

    assert intento.resultado == 'RECONOCIDO'
    assert intento.residente is not None
    assert intento.residente.nombre == 'Ana'
    assert intento.similitud == 0.9


async def test_similitud_bajo_el_umbral_no_reconoce(monkeypatch: pytest.MonkeyPatch) -> None:
    capturado = _montar(monkeypatch, (1, 0.20))
    intento = await servicio.procesar(1, b'jpeg', datetime.now(UTC))

    assert intento.resultado == 'NO_RECONOCIDO'
    assert intento.residente is None
    registro = capturado['registro']
    assert isinstance(registro, dict)
    assert registro['id_residente'] is None


async def test_similitud_justo_en_el_umbral_reconoce(monkeypatch: pytest.MonkeyPatch) -> None:
    _montar(monkeypatch, (1, UMBRAL))
    intento = await servicio.procesar(1, b'jpeg', datetime.now(UTC))
    assert intento.resultado == 'RECONOCIDO'


async def test_sin_patrones_registrados_no_reconoce(monkeypatch: pytest.MonkeyPatch) -> None:
    _montar(monkeypatch, None)
    intento = await servicio.procesar(1, b'jpeg', datetime.now(UTC))

    assert intento.resultado == 'NO_RECONOCIDO'
    assert intento.similitud == 0.0


async def test_siempre_guarda_evidencia_aunque_no_reconozca(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capturado = _montar(monkeypatch, (1, 0.10))
    await servicio.procesar(1, b'jpeg', datetime.now(UTC))

    assert 'ruta_evidencia' in capturado
    evidencia = capturado['evidencia']
    assert isinstance(evidencia, dict)
    assert len(str(evidencia['hash_sha256'])) == 64


async def test_calcula_los_segundos_de_respuesta(monkeypatch: pytest.MonkeyPatch) -> None:
    _montar(monkeypatch, (1, 0.9))
    hace_un_segundo = datetime.now(UTC) - timedelta(seconds=1)
    intento = await servicio.procesar(1, b'jpeg', hace_un_segundo)
    assert intento.segundos_respuesta >= 1.0


async def test_imagen_sin_rostro_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    _montar(monkeypatch, (1, 0.9))
    monkeypatch.setattr(servicio.vision, 'vector_de_rostro_unico', lambda _: (None, 3))

    with pytest.raises(ErrorApi) as fallo:
        await servicio.procesar(1, b'jpeg', datetime.now(UTC))

    assert fallo.value.code == 'VALIDATION_ERROR'
    assert fallo.value.details == [{'rostros': 3}]
