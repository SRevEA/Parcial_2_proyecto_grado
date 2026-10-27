from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class Residente(Base):
    __tablename__ = 'residente'

    id_residente: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    documento: Mapped[str] = mapped_column(String(20), unique=True)
    id_apartamento: Mapped[int] = mapped_column(ForeignKey('apartamento.id_apartamento'))
    estado: Mapped[str] = mapped_column(String(10))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
