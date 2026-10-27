from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


@dataclass
class UsuarioFalso:
    id_usuario: int = 1
    nombre: str = 'Admin'
    correo: str = 'admin@proyectogrado.co'
    contrasena_hash: str = ''
    rol: str = 'ADMINISTRADOR'
    estado: str = 'ACTIVO'


@dataclass
class ResidenteFalso:
    id_residente: int = 1
    nombre: str = 'Ana'
    apellido: str = 'Perez'
    documento: str = 'DOC-1'
    id_apartamento: int = 1
    estado: str = 'ACTIVO'


@dataclass
class AutorizacionFalsa:
    id_autorizacion: int = 1
    id_residente: int = 1
    aceptada: bool = True
    finalidades: str = 'Control de acceso'
    version_politica: str = '1.0'


@dataclass
class ApartamentoFalso:
    id_apartamento: int = 1
    id_torre: int = 1
    numero: str = '101'


@dataclass
class FilaApartamentoFalsa:
    apartamento: ApartamentoFalso = field(default_factory=ApartamentoFalso)
    torre: str = '1'
    residentes: int = 0


@dataclass
class RegistroFalso:
    id_registro: int = 10
    id_punto: int = 1
    id_residente: int | None = None
    resultado: str = 'NO_RECONOCIDO'
    similitud: Decimal | None = None
    capturado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    fecha_hora: datetime = field(default_factory=lambda: datetime.now(UTC))
