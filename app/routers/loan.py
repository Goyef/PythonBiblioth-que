from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Loan, Book, StatutEmpruntEnum, LoanHistory
from app.schemas.loan import LoanCreate, LoanUpdate
from app.database import get_session
from app.validators import validate_available_copies

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

@router.get("/{loan_id}")
def get_loan_detail(loan_id: int, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    return {
        "id": loan.id,
        "nom_emprunteur": loan.nom_emprunteur,
        "email_emprunteur": loan.email_emprunteur,
        "numero_carte": loan.numero_carte,
        "book_name": loan.books.title,
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
def ajouter_loan(loan: LoanCreate, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Le livre n'est pas disponible en ce moment")
    
    active_loans = db.query(Loan).filter(
        Loan.email_emprunteur == loan.email_emprunteur,
        Loan.statut == StatutEmpruntEnum.ACTIF
    ).count()
    
    if active_loans >= 5:
        raise HTTPException(status_code=400, detail="Vous avez atteint la limite d'emprunts actifs (5)")
    
    try:
        validate_available_copies(book.available_copies - 1, book.total_copies)
    except ValueError :
        raise HTTPException(status_code=400, detail="Le nombre de copies disponibles ne peut pas être négatif")
    
    date_emprunt = datetime.strptime(loan.date_emprunt, "%Y-%m-%d").date()
    date_limite_retour = date_emprunt + timedelta(days=14)
    
    new_loan = Loan(
        nom_emprunteur=loan.nom_emprunteur,
        email_emprunteur=loan.email_emprunteur,
        numero_carte=loan.numero_carte,
        date_emprunt=date_emprunt,
        date_limite_retour=date_limite_retour,
        date_retour=None,
        book_id=loan.book_id,
        statut="actif"
    )
    statut_enum = StatutEmpruntEnum.ACTIF
    if loan.statut is not None:
        statut_enum = loan.statut
        statut_enum = StatutEmpruntEnum[loan.statut.upper()]
        new_loan.statut = statut_enum
    else:
        new_loan.statut = StatutEmpruntEnum.ACTIF
    book.available_copies -= 1
    
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    loan_history = db.query(LoanHistory).filter(LoanHistory.book_id == loan.book_id).first()
    if not loan_history:
        loan_history = LoanHistory(
            book_id=loan.book_id,
            loan_amount=1,
            popularity=1
        )
        db.add(loan_history)
    else:
        loan_history.loan_amount += 1
        loan_history.popularity += 1
    
    db.commit()
    
    return {
        "id": new_loan.id,
        "nom_emprunteur": new_loan.nom_emprunteur,
        "email_emprunteur": new_loan.email_emprunteur,
        "book_name": book.title,
        "date_emprunt": str(new_loan.date_emprunt),
        "date_limite_retour": str(new_loan.date_limite_retour),
        "date_retour": new_loan.date_retour,
        "statut": new_loan.statut
    }

@router.put("/update/{loan_id}")
def update_loan(loan_id: int, loan_update: LoanUpdate, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    if loan_update.nom_emprunteur is not None:
        loan.nom_emprunteur = loan_update.nom_emprunteur
    if loan_update.email_emprunteur is not None:
        loan.email_emprunteur = loan_update.email_emprunteur
    if loan_update.numero_carte is not None:
        loan.numero_carte = loan_update.numero_carte
    if loan_update.date_emprunt is not None:
        loan.date_emprunt = loan_update.date_emprunt
    if loan_update.date_limite_retour is not None:
        loan.date_limite_retour = loan_update.date_limite_retour
    if loan_update.date_retour is not None:
        loan.date_retour = loan_update.date_retour
    if loan_update.statut is not None:
        loan.statut = loan_update.statut
    if loan_update.book_id is not None:
        book = db.query(Book).filter(Book.id == loan_update.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Livre non trouvé")
        loan.book_id = loan_update.book_id

    db.commit()
    db.refresh(loan)
    
    
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    
    return {
        "id": loan.id,
        "nom_emprunteur": loan.nom_emprunteur,
        "email_emprunteur": loan.email_emprunteur,
        "book_name": book.title,
        "date_emprunt": str(loan.date_emprunt),
        "date_limite_retour": str(loan.date_limite_retour),
        "date_retour": loan.date_retour,
        "statut": loan.statut
    }