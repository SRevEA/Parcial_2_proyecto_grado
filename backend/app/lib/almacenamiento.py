import httpx

from ..config import settings

_BASE = f'{settings.SUPABASE_URL}/storage/v1'
_CABECERAS = {'Authorization': f'Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}'}

_cliente = httpx.AsyncClient(timeout=30, headers=_CABECERAS)


async def cerrar() -> None:
    await _cliente.aclose()


async def subir(ruta: str, datos: bytes, tipo: str = 'image/jpeg') -> None:
    r = await _cliente.post(
        f'{_BASE}/object/{settings.BUCKET_EVIDENCIAS}/{ruta}',
        headers={'Content-Type': tipo, 'x-upsert': 'true'},
        content=datos,
    )
    r.raise_for_status()


async def url_firmada(ruta: str, segundos: int = 300) -> str:
    r = await _cliente.post(
        f'{_BASE}/object/sign/{settings.BUCKET_EVIDENCIAS}/{ruta}',
        json={'expiresIn': segundos},
    )
    r.raise_for_status()
    firmada: str = r.json()['signedURL']
    return f'{_BASE}{firmada}' if firmada.startswith('/') else firmada


async def eliminar(rutas: list[str]) -> None:
    if not rutas:
        return
    r = await _cliente.request(
        'DELETE',
        f'{_BASE}/object/{settings.BUCKET_EVIDENCIAS}',
        json={'prefixes': rutas},
    )
    r.raise_for_status()
