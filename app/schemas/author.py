from typing import Optional

from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from app.validators import (
    validate_birth_date,

)

class AuthorBase(BaseModel):
    """Schema de base pour un auteur"""

    first_name: str
    last_name: str
    birth_date: str = None
    death_date: Optional[str] = None
    biography: Optional[str] = None
    nationalite: Optional[str] = None
    website: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name_field(cls, v: str) -> str:
        """Valide le prénom"""
        return v
    
    @field_validator("last_name")
    @classmethod
    def validate_last_name_field(cls, v: str) -> str:
        """Valide le nom de famille"""
        return v
    
    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_field(cls, v: Optional[date], death_date: Optional[date]) -> Optional[date]:
        """Valide la date de naissance"""
        return validate_birth_date(v, death_date)
    
    @field_validator("death_date")
    @classmethod
    def validate_death_date_field(cls, v: Optional[date]) -> Optional[date]:
        """Valide la date de décès"""
        return v
    
    @field_validator("nationalite")
    @classmethod
    def validate_nationalite_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide la nationalité"""
        return v
    
    @field_validator("website")
    @classmethod
    def validate_website_field(cls, v: Optional[str]) -> Optional[str]:
        """Valide le site web"""
        return v

class AuthorCreate(AuthorBase):
    """Schema pour la création d'un auteur"""
    class Config:
        from_attributes = True

class AuthorUpdate(AuthorBase):
    """Schema pour la mise à jour d'un auteur"""

    first_name: str
    last_name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    biography: Optional[str] = None
    nationalite: Optional[str] = None
    website: Optional[str] = None
   
    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_field(cls, v: Optional[date]) -> Optional[date]:
        """Valide la date de naissance"""
        return v
    
    @field_validator("death_date")
    @classmethod
    def validate_death_date_field(cls, v: Optional[date]) -> Optional[date]:
        """Valide la date de décès"""
        return validate_birth_date(v)

class AuthorRead(AuthorBase):
    """Schema pour lire un auteur"""
    id: int

    class Config:
        from_attributes = True