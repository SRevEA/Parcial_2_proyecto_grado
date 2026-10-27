from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..lib.db import Base


class Apartamento(Base):
    __tablename__ = 'apartamento'

    id_apartamento: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_torre: Mapped[int] = mapped_column(ForeignKey('torre.id_torre'))
    numero: Mapped[str] = mapped_column(String(20))
