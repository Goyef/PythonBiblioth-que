from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Livre(Base):
    __tablename__ = 'livres'
    
    id = Column(Integer, primary_key=True)
    titre = Column(String(200), nullable=False)
    isbn = Column(String(13))
    annee_publi = Column(Integer)
    auteur = Column(String(100))
    nb_exemplaires_dispo = Column(Integer)
    Descritpion = Column(String)  # Note: faute de frappe conservée
    categorie = Column(String(50))
    language = Column(String(50))
    nb_pages = Column(Integer)
    maison_edition = Column(String(100))

class Auteur(Base):
    __tablename__ = 'auteurs'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    biographie = Column(String)
    nationalite = Column(String(50))
    date_naissance = Column(String)
    date_deces = Column(String)

class Emprunt(Base):
    __tablename__ = 'emprunts'
    
    id = Column(Integer, primary_key=True)
    livre_id = Column(Integer)  # ForeignKey omis pour simplicité
    nom_emprunteur = Column(String(100))
    email_emprunteur = Column(String(100))
    date_emprunt = Column(String)
    date_limite_retour = Column(String)
    date_retour = Column(String)
    statut = Column(String(20))

class Historique(Base):
    __tablename__ = 'historiques'
    
    id = Column(Integer, primary_key=True)
    livre_id = Column(String)
    nmb_emprunt = Column(Integer)

# Configuration de la base de données
engine = create_engine("sqlite:///bibliotheque.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)