import pytest

from app.lib.errors import ErrorApi
from app.lib.seguridad import emitir_token, hashear, leer_token, verificar
from app.repositories import usuario_sistema as repo
from app.schemas.auth import Credenciales
from app.services import auth as servicio
from tests.fakes import UsuarioFalso


def test_hash_y_verificacion() -> None:
    guardado = hashear('Clave.Segura1')
    assert guardado != 'Clave.Segura1'
    assert verificar('Clave.Segura1', guardado)
    assert not verificar('otra', guardado)


def test_verificar_no_estalla_con_hash_invalido() -> None:
    assert not verificar('algo', 'esto-no-es-un-hash')


def test_token_ida_y_vuelta() -> None:
    datos = leer_token(emitir_token(7, 'VIGILANTE'))
    assert datos is not None
    assert datos['sub'] == '7'
    assert datos['rol'] == 'VIGILANTE'


def test_token_alterado_no_se_lee() -> None:
    assert leer_token(emitir_token(7, 'VIGILANTE') + 'x') is None


async def test_login_con_clave_correcta(monkeypatch: pytest.MonkeyPatch) -> None:
    usuario = UsuarioFalso(contrasena_hash=hashear('Correcta1'))

    async def buscar(_: str, session: object = None) -> UsuarioFalso:
        return usuario

    monkeypatch.setattr(repo, 'buscar_por_correo', buscar)
    sesion = await servicio.autenticar(
        Credenciales(correo='admin@proyectogrado.co', contrasena='Correcta1')
    )
    assert sesion.rol == 'ADMINISTRADOR'
    assert sesion.token


async def test_login_con_clave_incorrecta(monkeypatch: pytest.MonkeyPatch) -> None:
    usuario = UsuarioFalso(contrasena_hash=hashear('Correcta1'))

    async def buscar(_: str, session: object = None) -> UsuarioFalso:
        return usuario

    monkeypatch.setattr(repo, 'buscar_por_correo', buscar)
    with pytest.raises(ErrorApi) as fallo:
        await servicio.autenticar(
            Credenciales(correo='admin@proyectogrado.co', contrasena='Mala1234')
        )
    assert fallo.value.status_code == 401
    assert fallo.value.code == 'UNAUTHENTICATED'


async def test_login_de_usuario_inactivo(monkeypatch: pytest.MonkeyPatch) -> None:
    usuario = UsuarioFalso(contrasena_hash=hashear('Correcta1'), estado='INACTIVO')

    async def buscar(_: str, session: object = None) -> UsuarioFalso:
        return usuario

    monkeypatch.setattr(repo, 'buscar_por_correo', buscar)
    with pytest.raises(ErrorApi) as fallo:
        await servicio.autenticar(
            Credenciales(correo='admin@proyectogrado.co', contrasena='Correcta1')
        )
    assert fallo.value.status_code == 401
