from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=RAIZ / '.env', extra='ignore')

    PORT: int = 8100

    SUPABASE_URL: str = Field(min_length=1)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(min_length=1)
    BUCKET_EVIDENCIAS: str = Field(min_length=1)

    DATABASE_URL: str = Field(min_length=1)

    JWT_SECRET: str = Field(min_length=1)
    JWT_HORAS_VIGENCIA: int = 8

    ORIGENES_PERMITIDOS: list[str] = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]


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
