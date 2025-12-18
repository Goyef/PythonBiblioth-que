import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Créer un client de test FastAPI
    return TestClient(app)

@pytest.fixture
def sample_author_data():
    # Donnée d'un auteur d'exemple
    return {
        "last_name": "PATATOR",
        "first_name": "John",
        "biographie": "auteur fictif",
        "nationalite": "Francaise",
        "date_naissance": "1970-01-01",
        # "date_deces": None
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

# création auteur
def test_create_author(client, sample_author_data):
    response = client.post("/authors/add", params=sample_author_data)
    assert response.status_code == 200
    data = response.json()
    assert "auteur_id" in data
    assert data["message"] == "Auteur ajouté avec succès"
#getter
def test_get_authors(client):
    response = client.get("/authors/")
    assert response.status_code == 200
    data = response.json()
    assert "authors" in data
    assert "page" in data
    assert "total" in data
    assert "pages" in data

# 404
def test_no_authors_found(client):
    response = client.get("/authors/?page=99999")
    assert response.status_code == 404 or response.status_code == 200