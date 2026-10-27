import pytest

from app.lib.errors import ErrorApi
from app.repositories import configuracion as repo
from app.services import configuracion as servicio


def _acepta(monkeypatch: pytest.MonkeyPatch) -> None:
    async def establecer(clave: str, valor: str, session: object = None) -> bool:
        return True

    monkeypatch.setattr(repo, 'establecer', establecer)


async def test_umbral_valido_se_guarda(monkeypatch: pytest.MonkeyPatch) -> None:
    _acepta(monkeypatch)
    salida = await servicio.establecer('umbral_similitud', '0.45')
    assert salida.valor == '0.45'


@pytest.mark.parametrize('valor', ['1.5', '0', '1', '-0.2'])
async def test_umbral_fuera_de_rango_falla(monkeypatch: pytest.MonkeyPatch, valor: str) -> None:
    _acepta(monkeypatch)
    with pytest.raises(ErrorApi) as fallo:
        await servicio.establecer('umbral_similitud', valor)
    assert fallo.value.code == 'VALIDATION_ERROR'


async def test_dias_de_conservacion_cero_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    _acepta(monkeypatch)
    with pytest.raises(ErrorApi) as fallo:
        await servicio.establecer('dias_conservacion_evidencia', '0')
    assert fallo.value.code == 'VALIDATION_ERROR'


async def test_clave_inexistente_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    async def establecer(clave: str, valor: str, session: object = None) -> bool:
        return False

    monkeypatch.setattr(repo, 'establecer', establecer)
    with pytest.raises(ErrorApi) as fallo:
        await servicio.establecer('no_existe', 'x')
    assert fallo.value.code == 'NOT_FOUND'


async def test_umbral_se_lee_como_numero(monkeypatch: pytest.MonkeyPatch) -> None:
    async def obtener(clave: str, session: object = None) -> str:
        return '0.363'

    monkeypatch.setattr(repo, 'obtener', obtener)
    assert await servicio.umbral() == 0.363
