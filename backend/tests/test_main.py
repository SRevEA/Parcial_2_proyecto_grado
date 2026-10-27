from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app, raise_server_exceptions=False)


def test_health_responde_sin_credencial() -> None:
    r = cliente.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_ruta_inexistente_usa_el_envoltorio() -> None:
    r = cliente.get('/api/v1/no-existe')
    assert r.status_code == 404
    cuerpo = r.json()
    assert cuerpo['success'] is False
    assert cuerpo['statusCode'] == 404
    assert cuerpo['error']['code'] == 'NOT_FOUND'
    assert cuerpo['error']['details'] == []


def test_openapi_se_publica_versionado() -> None:
    r = cliente.get('/api/v1/openapi.json')
    assert r.status_code == 200
    assert r.json()['info']['version'] == '1.0.0'
