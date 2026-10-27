from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class PatronFacial(Base):
    __tablename__ = 'patron_facial'

    id_patron: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_residente: Mapped[int] = mapped_column(
        ForeignKey('residente.id_residente', ondelete='CASCADE')
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(128))
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
