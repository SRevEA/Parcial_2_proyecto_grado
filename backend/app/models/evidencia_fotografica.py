from datetime import datetime

from sqlalchemy import CHAR, BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class EvidenciaFotografica(Base):
    __tablename__ = 'evidencia_fotografica'

    id_evidencia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_registro: Mapped[int] = mapped_column(
        ForeignKey('registro_acceso.id_registro', ondelete='CASCADE'), unique=True
    )
    ruta_archivo: Mapped[str] = mapped_column(String(255))
    hash_sha256: Mapped[str] = mapped_column(CHAR(64))
    fecha_expiracion: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
