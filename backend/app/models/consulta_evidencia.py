from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class ConsultaEvidencia(Base):
    __tablename__ = 'consulta_evidencia'

    id_consulta: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_evidencia: Mapped[int | None] = mapped_column(
        ForeignKey('evidencia_fotografica.id_evidencia', ondelete='SET NULL'), nullable=True
    )
    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuario_sistema.id_usuario'))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
