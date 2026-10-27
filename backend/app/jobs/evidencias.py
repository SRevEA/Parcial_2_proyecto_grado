import asyncio
import contextlib

from ..services import accesos

SEGUNDOS_ENTRE_PURGAS = 3_600


async def purgar_periodicamente() -> None:
    while True:
        with contextlib.suppress(Exception):
            await accesos.purgar_vencidas()
        await asyncio.sleep(SEGUNDOS_ENTRE_PURGAS)
