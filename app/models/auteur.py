from datetime import date
from typing import Optional

from app.models.livre import Livre
from sqlmodel import Field, Relationship, SQLModel


class Auteur(SQLModel, table=True):
    """Modèle représentant un auteur"""

    __tablename__ = "auteurs"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    prenom: str = Field(index=True)
    date_naissance: date
    nationalite: str = Field(max_length=2)  # Code pays ISO
    biographie: Optional[str] = Field(default=None)
    date_deces: Optional[date] = Field(default=None)

    # Relations
    livres: list["Livre"] = Relationship(back_populates="auteur")
