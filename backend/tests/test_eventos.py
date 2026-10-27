import asyncio

from app.lib import eventos


async def test_el_suscriptor_recibe_lo_publicado() -> None:
    cola = eventos.suscribir()
    try:
        eventos.publicar('{"resultado": "RECONOCIDO"}')
        assert await asyncio.wait_for(cola.get(), timeout=1) == '{"resultado": "RECONOCIDO"}'
    finally:
        eventos.cancelar(cola)


async def test_varios_suscriptores_reciben_el_mismo_evento() -> None:
    primera = eventos.suscribir()
    segunda = eventos.suscribir()
    try:
        eventos.publicar('hola')
        assert await asyncio.wait_for(primera.get(), timeout=1) == 'hola'
        assert await asyncio.wait_for(segunda.get(), timeout=1) == 'hola'
    finally:
        eventos.cancelar(primera)
        eventos.cancelar(segunda)


async def test_cancelar_deja_de_recibir() -> None:
    cola = eventos.suscribir()
    eventos.cancelar(cola)
    eventos.publicar('nada')
    assert cola.empty()


async def test_una_rafaga_no_desconecta_al_suscriptor() -> None:
    cola = eventos.suscribir()
    try:
        for i in range(eventos.TAMANO_COLA + 10):
            eventos.publicar(f'evento-{i}')

        assert eventos.cantidad_suscriptores() == 1
        assert cola.qsize() == eventos.TAMANO_COLA

        recibidos = [cola.get_nowait() for _ in range(cola.qsize())]
        assert recibidos[-1] == f'evento-{eventos.TAMANO_COLA + 9}'
        assert 'evento-0' not in recibidos
    finally:
        eventos.cancelar(cola)
