from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class AutorizacionDatos(Base):
    __tablename__ = 'autorizacion_datos'

    id_autorizacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_residente: Mapped[int] = mapped_column(
        ForeignKey('residente.id_residente', ondelete='CASCADE'), unique=True
    )
    aceptada: Mapped[bool] = mapped_column(Boolean)
    finalidades: Mapped[str] = mapped_column(Text)
    version_politica: Mapped[str] = mapped_column(String(20))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
