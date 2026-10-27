from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ / '.env', extra='ignore')

    BACKEND_URL: str = Field(min_length=1)
    PUNTO_ACCESO_ID: int
    PUNTO_ACCESO_API_KEY: str = Field(min_length=1)

    CAMARA_INDICE: int = 0
    SEGUNDOS_ESTABLE: float = 2.0
    MOVIMIENTO_TOLERADO: float = 0.08
    SEGUNDOS_SIN_ROSTRO: float = 1.0
    SEGUNDOS_ENTRE_INTENTOS: float = 3.0
    SEGUNDOS_REINTENTO_COLA: float = 20.0
    RUTA_COLA: str = 'cola.db'
    MOSTRAR_VENTANA: bool = True


def _cargar() -> Settings:
    try:
        return Settings()
    except ValidationError:
        archivo = RAIZ / '.env'
        if archivo.exists():
            raise
        raise RuntimeError(
            f'Falta {archivo}. Las claves que necesita estan en {RAIZ / ".env.example"}.'
        ) from None


settings = _cargar()
