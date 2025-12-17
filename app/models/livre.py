from enum import Enum
from typing import Optional, List

# from app.models.emprunt import Emprunt
from app.models.auteur import Auteur
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine



class Categorie_Livre(str, Enum):
    """Catégories littéraires"""

    FICTION = "Fiction"
    SCIENCE = "Science"
    HISTOIRE = "Histoire"
    PHILOSOPHIE = "Philosophie"
    BIOGRAPHIE = "Biographie"
    POESIE = "Poésie"
    THEATRE = "Théâtre"
    JEUNESSE = "Jeunesse"
    BD = "BD"
    AUTRE = "Autre"


class Livre(SQLModel, table=True):
    """Modèle représentant un livre"""

    __tablename__ = "livres"

    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str = Field(index=True)
    isbn: str = Field(unique=True, index=True, max_length=17)
    annee_publi: int
    auteur_id: int = Field(foreign_key="auteurs.id", index=True)
    nb_exemplaires_dispo: int = Field(default=0, ge=0)
    nb_exemplaires_total: int = Field(gt=0)
    description: Optional[str] = Field(default=None)
    categorie: Categorie_Livre = Field(default=Categorie_Livre.AUTRE)
    language: str = Field(max_length=2)  # Code langue ISO
    pages: int = Field(gt=0)
    maison_edition: str

    # Relations
    auteur: Auteur = Relationship(back_populates="livre")
    # emprunts: list["Emprunt"] = Relationship(back_populates="livre")