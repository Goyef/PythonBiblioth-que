from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

from app.config import settings
from app.models import Base

connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    """Créer toutes les tables dans la base de données"""
    Base.metadata.create_all(engine)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_session)]
