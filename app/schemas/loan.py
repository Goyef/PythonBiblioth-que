from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from app.models import CategorieEnum
from app.schemas.book import BookRead

class LoanBase(BaseModel):
    """Schema de base pour un emprunt"""

    nom_emprunteur: str
    email_emprunteur: str
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

class LoanUpdate(LoanBase):
    """Schema pour la mise à jour d'un emprunt"""
    
    nom_emprunteur: str
    email_emprunteur: str
    date_emprunt: str
    date_limite_retour: str
    date_retour: Optional[str] = None
    statut: str
    book_id: int

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