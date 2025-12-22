from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Loan
from app.schemas.loan import LoanRead
from app.database import get_session

router = APIRouter(
    prefix="/loans",
    tags=["Emprunt"]
)

@router.get("/")
def get_loans(page: int = 1, db: Session = Depends(get_session)):
    per_page = 5
    offset = (page - 1) * per_page
    loan = db.query(Loan).offset(offset).limit(per_page).all()
    return {
        "loans": [{"id": l.id, "nom_emprunteur": l.nom_emprunteur, "date_limite_retour": l.date_limite_retour, "statut": l.statut} for l in loan],
        "page": page,
        "total": db.query(Loan).count(),
        "pages": (db.query(Loan).count() + per_page - 1)
    }

@router.get("/{loan_id}", response_model=LoanRead)
def get_loan_detail(loan_id: int, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    return {
        "id": loan.id,
        "nom_emprunteur": loan.nom_emprunteur,
        "email_emprunteur": loan.email_emprunteur,
        "book_id": loan.book_id,
        "date_emprunt": loan.date_emprunt,
        "date_limite_retour": loan.date_limite_retour,
        "date_retour": loan.date_retour,
        "statut": loan.statut
    }

@router.delete("/delete/{loan_id}")
def delete_loan(loan_id: int, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")
    db.delete(loan)
    db.commit()
    return {"message": f"Emprunt {loan_id} supprimé"}

@router.post("/add")
def ajouter_loan(nom_emprunteur: str, email_emprunteur: str, date_emprunt: str, date_limite_retour: str, date_retour: str, book_id: str, statut: str, db: Session = Depends(get_session)):
    new_loan = Loan(
        nom_emprunteur=nom_emprunteur,
        email_emprunteur=email_emprunteur,
        date_emprunt=date_emprunt,
        date_limite_retour=date_limite_retour,
        date_retour=date_retour,
        book_id=book_id,
        statut=statut
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return {"message": "Emprunt ajouté avec succès", "loan_id": new_loan.id}

@router.put("/update/{loan_id}")
def update_loan(loan_id: int, nom_emprunteur: str | None = None, email_emprunteur: str | None = None, date_emprunt: str | None = None, date_limite_retour: str | None = None, date_retour: str | None = None, statut: str | None = None, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    if nom_emprunteur is not None:
        loan.nom_emprunteur = nom_emprunteur
    if email_emprunteur is not None:
        loan.email_emprunteur = email_emprunteur
    if date_emprunt is not None:
        loan.date_emprunt = date_emprunt
    if date_limite_retour is not None:
        loan.date_limite_retour = date_limite_retour
    if date_retour is not None:
        loan.date_retour = date_retour
    if statut is not None:
        loan.statut = statut

    db.commit()
    db.refresh(loan)
    return {"message": "Emprunt mis à jour avec succès", "loan_id": loan.id}