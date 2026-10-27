from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class Torre(Base):
    __tablename__ = 'torre'

    id_torre: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
