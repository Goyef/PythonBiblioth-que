from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models.book import BookCategory
from app.schemas.validators import (
    validate_available_copies,
    validate_isbn13,
    validate_publication_year,
)


class BookBase(BaseModel):
    """Schema de base pour un livre"""

    title: str
    isbn: str
    publication_year: int
    author_id: int
    available_copies: int
    total_copies: int
    description: Optional[str] = None
    category: BookCategory = BookCategory.AUTRE
    language: str
    pages: int
    publisher: str

    @field_validator("isbn")
    @classmethod
    def validate_isbn_field(cls, v: str) -> str:
        """Valide l'ISBN"""
        return validate_isbn13(v)

    @field_validator("publication_year")
    @classmethod
    def validate_year_field(cls, v: int) -> int:
        """Valide l'année de publication"""
        return validate_publication_year(v)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Valide que la langue est un code ISO de 2 lettres"""
        if len(v) != 2 or not v.isalpha():
            raise ValueError("La langue doit être un code ISO de 2 lettres")
        return v.lower()

    @field_validator("pages")
    @classmethod
    def validate_pages(cls, v: int) -> int:
        """Valide le nombre de pages"""
        if v <= 0:
            raise ValueError("Le nombre de pages doit être supérieur à 0")
        return v

    @field_validator("total_copies")
    @classmethod
    def validate_total(cls, v: int) -> int:
        """Valide le nombre total d'exemplaires"""
        if v <= 0:
            raise ValueError("Le nombre total d'exemplaires doit être supérieur à 0")
        return v

    @model_validator(mode="after")
    def validate_copies(self):
        """Valide que disponible <= total"""
        validate_available_copies(self.available_copies, self.total_copies)
        return self


class BookCreate(BookBase):
    """Schema pour créer un livre"""

    pass


class BookUpdate(BaseModel):
    """Schema pour mettre à jour un livre (tous les champs optionnels)"""

    title: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    author_id: Optional[int] = None
    available_copies: Optional[int] = None
    total_copies: Optional[int] = None
    description: Optional[str] = None
    category: Optional[BookCategory] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide l'ISBN"""
        if v is not None:
            return validate_isbn13(v)
        return v

    @field_validator("publication_year")
    @classmethod
    def validate_year_field(cls, v: Optional[int]) -> Optional[int]:
        """Valide l'année de publication"""
        if v is not None:
            return validate_publication_year(v)
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Valide que la langue est un code ISO de 2 lettres"""
        if v is not None:
            if len(v) != 2 or not v.isalpha():
                raise ValueError("La langue doit être un code ISO de 2 lettres")
            return v.lower()
        return v


class BookRead(BookBase):
    """Schema pour lire un livre"""

    id: int

    class Config:
        from_attributes = True


class BookReadWithAuthor(BookRead):
    """Schema pour lire un livre avec les informations de l'auteur"""

    author_name: str = ""
    loans_count: int = 0
