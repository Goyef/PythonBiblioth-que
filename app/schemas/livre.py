from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models.livre import Categorie_Livre
from app.schemas.validateur import (
    valider_exemplaires_disponibles,
    valider_isbn13,
    valider_annee_publication,
)


class LivreBase(BaseModel):
    """Schema de base pour un livre"""

    titre: str
    isbn: str
    annee_publi: int
    auteur_id: int
    available_copies: int
    nb_exemplaires_dispo: int
    description: Optional[str] = None
    categorie: Categorie_Livre = Categorie_Livre.AUTRE
    language: str
    pages: int
    maison_edition: str

    @field_validator("isbn")
    @classmethod
    def valider_champs_isbn(cls, v: str) -> str:
        """Valide l'ISBN"""
        return valider_isbn13(v)

    @field_validator("publication_year")
    @classmethod
    def valider_annee_publication(cls, v: int) -> int:
        """Valide l'année de publication"""
        return valider_annee_publication(v)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Valide que la langue est un code ISO de 2 lettres"""
        if len(v) != 2 or not v.isalpha():
            raise ValueError("La langue doit être un code ISO de 2 lettres")
        return v.lower()

    @field_validator("pages")
    @classmethod
    def valider_nmb_pages(cls, v: int) -> int:
        """Valide le nombre de pages"""
        if v <= 0:
            raise ValueError("Le nombre de pages doit être supérieur à 0")
        return v

    @field_validator("total_copies")
    @classmethod
    def valider_nmb_exemplaire(cls, v: int) -> int:
        """Valide le nombre total d'exemplaires"""
        if v <= 0:
            raise ValueError("Le nombre total d'exemplaires doit être supérieur à 0")
        return v

    @model_validator(mode="after")
    def validate_copies(self):
        """Valide que disponible <= total"""
        valider_exemplaires_disponibles(self.available_copies, self.nb_exemplaires_dispo)
        return self


class BookCreate(LivreBase):
    """Schema pour créer un livre"""

    pass


class BookUpdate(BaseModel):
    """Schema pour mettre à jour un livre (tous les champs optionnels)"""

    titre: Optional[str] = None
    isbn: Optional[str] = None
    annee_publi: Optional[int] = None
    auteur_id: Optional[int] = None
    available_copies: Optional[int] = None
    nb_exemplaires_dispo: Optional[int] = None
    description: Optional[str] = None
    categorie: Optional[Categorie_Livre] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    maison_edition: Optional[str] = None

    @field_validator("isbn")
    @classmethod
    def valider_champs_isbn(cls, v: Optional[str]) -> Optional[str]:
        """Valide l'ISBN"""
        if v is not None:
            return valider_isbn13(v)
        return v

    @field_validator("publication_year")
    @classmethod
    def valider_annee_publication(cls, v: Optional[int]) -> Optional[int]:
        """Valide l'année de publication"""
        if v is not None:
            return valider_annee_publication(v)
        return v

    @field_validator("language")
    @classmethod
    def valider_language(cls, v: Optional[str]) -> Optional[str]:
        """Valide que la langue est un code ISO de 2 lettres"""
        if v is not None:
            if len(v) != 2 or not v.isalpha():
                raise ValueError("La langue doit être un code ISO de 2 lettres")
            return v.lower()
        return v


class BookRead(LivreBase):
    """Schema pour lire un livre"""

    id: int

    class Config:
        from_attributes = True


class BookReadWithAuthor(BookRead):
    """Schema pour lire un livre avec les informations de l'auteur"""

    author_name: str = ""
    loans_count: int = 0
