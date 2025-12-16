from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.schemas.items import Base
from app.services.business_logic import Auteur, Livre


# Créer la base de données
engine = create_engine("sqlite:///bibliotheque.db")
Base.metadata.create_all(engine)

# Session
Session = sessionmaker(bind=engine)