from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Auteur(Base):
    __tablename__ = 'auteurs'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    livres = relationship("Livre", back_populates="auteur")

class Livre(Base):
    __tablename__ = "livres"
    
    id = Column(Integer, primary_key=True)
    titre = Column(String(200), nullable=False)
    isbn = Column(String(13), unique=True)
    prix = Column(Float, nullable=False)
    auteur_id = Column(Integer, ForeignKey("auteurs.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    # Relation
    auteur = relationship("Auteur", back_populates="livres")


