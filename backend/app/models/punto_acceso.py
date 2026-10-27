from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class PuntoAcceso(Base):
    __tablename__ = 'punto_acceso'

    id_punto: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    ubicacion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    equipo_captura: Mapped[str | None] = mapped_column(String(60), nullable=True)
    api_key_hash: Mapped[str] = mapped_column(String(255))
    estado: Mapped[str] = mapped_column(String(10))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
