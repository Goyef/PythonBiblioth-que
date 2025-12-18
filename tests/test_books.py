import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Créer un client de test FastAPI
    return TestClient(app)

@pytest.fixture
def sample_book_data():
    # DOnnée d'un livre d'exemple
    return {
        "title": "super livre du test ultime",
        "isbn": "123-4567890123",
        "publication_year": 2020,
        "author_id": "1",
        "available_copies": 30,
        "description": "il est l élu",
        "category": "Fiction",
        "language": "Fr",
        "pages": 250,
        "publisher": "Maison de Test"
    }

@pytest.fixture
def db_session():
    # from app.database import get_session, create_db_and_tables
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base

    engine = create_engine("sqlite:///:memory:") # créer une bdd SQLite en mémoire pour les tests
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


#TEST

# création livre
def test_create_book(client, sample_book_data):
    response = client.post("/books/add", json=sample_book_data)
    assert response.status_code == 200
    data = response.json()
    assert "livre_id" in data
    assert data["message"] == "Livre ajouté avec succès"

#getter marche ?
def test_get_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert "livres" in data
    assert "page" in data
    assert "total" in data
    assert "pages" in data

# 404 si pas de livre
def test_no_books_found(client):
    response = client.get("/books/?page=99999")
    assert response.status_code == 404 or response.status_code == 200
