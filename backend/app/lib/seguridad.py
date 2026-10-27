from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from ..config import settings


def hashear(texto: str) -> str:
    return bcrypt.hashpw(texto.encode(), bcrypt.gensalt()).decode()


def verificar(texto: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(texto.encode(), hash_guardado.encode())
    except ValueError:
        return False


def emitir_token(id_usuario: int, rol: str) -> str:
    ahora = datetime.now(UTC)
    carga = {
        'sub': str(id_usuario),
        'rol': rol,
        'iat': ahora,
        'exp': ahora + timedelta(hours=settings.JWT_HORAS_VIGENCIA),
    }
    return jwt.encode(carga, settings.JWT_SECRET, algorithm='HS256')


def leer_token(token: str) -> dict[str, Any] | None:
    try:
        datos: dict[str, Any] = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    except jwt.PyJWTError:
        return None
    return datos
