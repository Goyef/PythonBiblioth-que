from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from app.models import CategorieEnum
from app.schemas.book import BookRead

class LoanBase(BaseModel):
    """Schema de base pour un emprunt"""

    nom_emprunteur: str
    email_emprunteur: str
    numero_carte: str
    date_emprunt: str
    date_limite_retour: str
    date_retour: Optional[str] = None
    statut: str
    book_id: int

    @field_validator("nom_emprunteur")
    @classmethod
    def validate_nom_emprunteur_field(cls, v: str) -> str:
        """Valide le nom de l'emprunteur"""
        return v
    
    @field_validator("email_emprunteur")
    @classmethod
    def validate_email_emprunteur_field(cls, v: str) -> str:
        """Valide l'email de l'emprunteur"""
        return v
    
    @field_validator("date_emprunt")
    @classmethod
    def validate_date_emprunt_field(cls, v: date) -> date:
        """Valide la date d'emprunt"""
        return v
    
    @field_validator("date_limite_retour")
    @classmethod
    def validate_date_limite_retour_field(cls, v: date) -> date:
        """Valide la date limite de retour"""
        return v
    
    @field_validator("date_retour")
    @classmethod
    def validate_date_retour_field(cls, v: Optional[date]) -> Optional[date]:
        """Valide la date de retour"""
        return v
    
    @field_validator("statut")
    @classmethod
    def validate_statut_field(cls, v: str) -> str:
        """Valide le statut de l'emprunt"""
        return v
    
class LoanCreate(LoanBase):
    """Schema pour la création d'un emprunt"""
    class Config:
        from_attributes = True

class LoanUpdate(BaseModel):
    """Schema pour mettre à jour un emprunt (tous les champs optionnels)"""

    nom_emprunteur: Optional[str] = None
    email_emprunteur: Optional[str] = None
    date_emprunteur: Optional[str] = None
    date_emprunt: Optional[str] = None
    date_limite_retour: Optional[str] = None
    date_retour: Optional[str] = None
    statut: Optional[str] = None
    book_id: Optional[int] = None

    @field_validator("nom_emprunteur")
    @classmethod
    def validate_nom_emprunteur_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide le nom de l'emprunteur"""
        if v is not None:
            return v
        return v
    
    @field_validator("email_emprunteur")
    @classmethod
    def validate_email_emprunteur_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide l'email de l'emprunteur"""
        if v is not None:
            return v
        return v
    
    @field_validator("date_emprunt")
    @classmethod
    def validate_date_emprunt_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide la date d'emprunt"""
        if v is not None:
            return v
        return v
    
    @field_validator("date_limite_retour")
    @classmethod
    def validate_date_limite_retour_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide la date limite de retour"""
        if v is not None:
            return v
        return v
    
    @field_validator("date_retour")
    @classmethod
    def validate_date_retour_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide la date de retour"""
        if v is not None:
            return v
        return v

    @field_validator("statut")
    @classmethod
    def validate_statut_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide le statut de l'emprunt"""
        if v is not None:
            return v
        return v
    
    @field_validator("book_id")
    @classmethod
    def validate_book_id_field(cls, v: Optional[int]) -> Optional[int]:
        """Valide l'ID du livre"""
        if v is not None and v > 0:
            return v
        return v

class LoanRead(LoanBase):
    """Schema pour lire un emprunt"""
    id: int

    class Config:
        from_attributes = True

class LoanReadWithBook(LoanRead):
    """Schema pour lire un emprunt avec les détails du livre associé"""
    book: "BookRead"
    
    class Config:
        from_attributes = True