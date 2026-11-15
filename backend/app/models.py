from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    prix: Mapped[int] = mapped_column(default=0)
    quantite: Mapped[int] = mapped_column(default=0)
    seuil_alerte: Mapped[int] = mapped_column(default=5)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    mouvements: Mapped[list["Mouvement"]] = relationship(back_populates="produit")


class Mouvement(Base):
    __tablename__ = "mouvements"

    id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"))
    type: Mapped[str] = mapped_column(String(10))  # "entree" ou "sortie"
    quantite: Mapped[int]
    motif: Mapped[str | None] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column(server_default=func.now())

    produit: Mapped["Produit"] = relationship(back_populates="mouvements")