from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class RegistroAcceso(Base):
    __tablename__ = 'registro_acceso'

    id_registro: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_punto: Mapped[int] = mapped_column(ForeignKey('punto_acceso.id_punto'))
    id_residente: Mapped[int | None] = mapped_column(
        ForeignKey('residente.id_residente', ondelete='SET NULL'), nullable=True
    )
    resultado: Mapped[str] = mapped_column(String(15))
    similitud: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    capturado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
