from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    """Créer toutes les tables dans la base de données"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dépendance pour obtenir une session de base de données"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
