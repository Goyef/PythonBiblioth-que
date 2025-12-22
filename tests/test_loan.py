import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Créer un client de test FastAPI
    return TestClient(app)

@pytest.fixture
def sample_loan_data():
    # Donnée d'un emprunt d'exemple
    return {
        "nom_emprunteur": "PATATOR le frere",
        "email_emprunteur": "patator@gmail.com",
        "date_emprunt": "2024-01-01",
        "date_limite_retour": "2024-01-15",
        "date_retour": "2024-01-15",
        "statut": "en cours",
        "book_id": 1
    }

@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base

    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

#TEST

# créer loan
def test_create_loan(client, sample_loan_data):
    response = client.post("/loans/add", params=sample_loan_data)
    assert response.status_code == 200
    data = response.json()
    assert "loan_id" in data
    assert data["message"] == "Emprunt ajouté avec succès"

#get un loan
def test_get_loans(client):
    response = client.get("/loans/")
    assert response.status_code == 200
    data = response.json()
    assert "loans" in data
    assert "page" in data
    assert "total" in data
    assert "pages" in data

# 404
def test_no_loans_found(client):
    response = client.get("/loans/?page=99999")
    assert response.status_code == 404 or response.status_code == 200