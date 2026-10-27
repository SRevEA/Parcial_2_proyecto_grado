from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class UsuarioSistema(Base):
    __tablename__ = 'usuario_sistema'

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20))
    estado: Mapped[str] = mapped_column(String(10))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
