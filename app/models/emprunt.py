from datetime import datetime
from enum import Enum
from typing import Optional

from app.models.livre import Livre
from sqlmodel import Field, Relationship, SQLModel


class EmpruntStatus(str, Enum):
    """Statuts possibles d'un emprunt"""

    ACTIVE = "actif"
    RETURNED = "retourné"
    LATE = "en retard"


class Emprunt(SQLModel, table=True):
    """Modèle représentant un emprunt de livre"""

    __tablename__ = "emprunts"

    id: Optional[int] = Field(default=None, primary_key=True)
    livre_id: int = Field(foreign_key="livres.id", index=True)
    nom_emprunteur: str = Field(index=True)
    email_emprunteur: str = Field(index=True)
    numero_carte_emprunt: str = Field(index=True)
    date_emprunt: datetime = Field(default_factory=datetime.now)
    date_limite_retour: datetime
    date_retour: Optional[datetime] = Field(default=None)
    statut: EmpruntStatus = Field(default=EmpruntStatus.ACTIVE)

    # Relations
    livre: "Livre" = Relationship(back_populates="emprunts")



# de coté on verra :
# comments: Optional[str] = Field(default=None)
# renewed: bool = Field(default=False)