from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class Configuracion(Base):
    __tablename__ = 'configuracion'

    clave: Mapped[str] = mapped_column(String(60), primary_key=True)
    valor: Mapped[str] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    actualizado: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
