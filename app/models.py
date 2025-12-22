import enum
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

class CategorieEnum(str, enum.Enum):
    """Énumération des catégories littéraires"""
    FICTION = "Fiction"
    SCIENCE = "Science"
    HISTOIRE = "Histoire"
    PHILOSOPHIE = "Philosophie"
    AUTRE = "Autre" 


class StatutEmpruntEnum(str, enum.Enum):
    """Énumération des statuts d'emprunt"""
    ACTIF = "Actif"
    RETOURNE = "Retourné"
    EN_RETARD = "En retard"

    
class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    isbn = Column(String(13))
    publication_year = Column(Integer)
    
    available_copies = Column(Integer)
    total_copies = Column(Integer)
    description = Column(String)
    
    category = Column(
        Enum(CategorieEnum, name="categorie_enum"),  
        nullable=False,
        default=CategorieEnum.AUTRE
    )

    language = Column(String(50))
    pages = Column(Integer)
    publisher = Column(String(100))

    author_id = Column(Integer, ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False, index=True)
    authors = relationship("Author", back_populates="books")
    loans = relationship("Loan", back_populates="books")
    loan_history = relationship("LoanHistory", back_populates="books")

 
class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    biographie = Column(String, nullable=True)
    nationalite = Column(String(50))
    birthdate = Column(String)
    death_date = Column(String, nullable=True)
    website = Column(String(100), nullable=True)

    books = relationship("Book", back_populates="authors")

class Loan(Base):
    __tablename__ = 'loans'
    
    id = Column(Integer, primary_key=True)
    
    nom_emprunteur = Column(String(100))
    email_emprunteur = Column(String(100))
    numero_carte = Column(String(50))
    date_emprunt = Column(String)
    date_limite_retour = Column(String)
    date_retour = Column(String)
    statut = Column(
        Enum(StatutEmpruntEnum, name="statut_emprunt_enum"),  
        nullable=False,
        default=StatutEmpruntEnum.ACTIF
    )
    book_id = Column(Integer, ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True)
    books = relationship("Book", back_populates="loans")
    
class LoanHistory(Base):
    __tablename__ = 'loan_history'
    
    id = Column(Integer, primary_key=True)
    loan_amount = Column(Integer)
    avg_loan_duration = Column(Integer, nullable=True)  
    popularity = Column(Integer, nullable=False, default=0)

    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    books = relationship("Book", back_populates="loan_history")