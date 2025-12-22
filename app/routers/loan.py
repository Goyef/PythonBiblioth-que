from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Loan, Book, StatutEmpruntEnum, LoanHistory
from app.schemas.loan import LoanCreate, LoanUpdate
from app.database import get_session
from app.validators import validate_available_copies

router = APIRouter(prefix="/loans", tags=["Emprunt"])


@router.get("/")
def get_loans(
    page: int = 1,
    per_page: int = 5,
    statut: str = None,
    email_emprunteur: str = None,
    numero_carte: str = None,
    book_id: int = None,
    date_debut: str = None,
    date_fin: str = None,
    db: Session = Depends(get_session),
):
    """
    Consultation des emprunts avec filtres
    - statut: ACTIF, RETOURNE, EN_RETARD (optionnel)
    - email_emprunteur: filtrer par email (optionnel)
    - numero_carte: filtrer par numéro de carte (optionnel)
    - book_id: filtrer par livre (optionnel)
    - date_debut: date minimum (YYYY-MM-DD) (optionnel)
    - date_fin: date maximum (YYYY-MM-DD) (optionnel)
    """
    query = db.query(Loan)

    if statut:
        try:
            statut_enum = StatutEmpruntEnum[statut.upper()]
            query = query.filter(Loan.statut == statut_enum)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail="Statut invalide. Valeurs possibles: ACTIF, RETOURNE, EN_RETARD",
            )

    if email_emprunteur:
        query = query.filter(Loan.email_emprunteur.ilike(f"%{email_emprunteur}%"))

    if numero_carte:
        query = query.filter(Loan.numero_carte == numero_carte)

    if book_id:
        query = query.filter(Loan.book_id == book_id)

    if date_debut:
        try:
            datetime.strptime(date_debut, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Format date_debut invalide (YYYY-MM-DD)"
            )
        query = query.filter(Loan.date_emprunt >= date_debut)

    if date_fin:
        try:
            datetime.strptime(date_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Format date_fin invalide (YYYY-MM-DD)"
            )
        query = query.filter(Loan.date_emprunt <= date_fin)

    # Pagination
    total = query.count()
    offset = (page - 1) * per_page
    loans = query.offset(offset).limit(per_page).all()
    pages = (total + per_page - 1) // per_page

    return {
        "emprunts": [
            {
                "id": l.id,
                "nom_emprunteur": l.nom_emprunteur,
                "email_emprunteur": l.email_emprunteur,
                "numero_carte": l.numero_carte,
                "livre_id": l.book_id,
                "date_emprunt": l.date_emprunt,
                "date_limite_retour": l.date_limite_retour,
                "date_retour": l.date_retour,
                "statut": l.statut.value,
            }
            for l in loans
        ],
        "pagination": {
            "page": page,
            "par_page": per_page,
            "total": total,
            "pages_totales": pages,
        },
        "filtres": {
            "statut": statut,
            "email_emprunteur": email_emprunteur,
            "numero_carte": numero_carte,
            "book_id": book_id,
            "date_debut": date_debut,
            "date_fin": date_fin,
        },
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
        "statut": loan.statut,
    }


@router.post("/renew/{loan_id}")
def renew_loan(loan_id: int, db: Session = Depends(get_session)):
 
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    if loan.statut != StatutEmpruntEnum.ACTIF:
        raise HTTPException(
            status_code=400, detail="Seuls les emprunts actifs peuvent être renouvelés"
        )

    if loan.renewed >= 1:
        raise HTTPException(
            status_code=400,
            detail="Cet emprunt a déjà été renouvelé une fois. Renouvellement limité à 1 par emprunt",
        )

    date_limite_actuelle = datetime.strptime(loan.date_limite_retour, "%Y-%m-%d").date()
    new_date_limite = date_limite_actuelle + timedelta(days=14)
    old_date_limite = loan.date_limite_retour

    loan.date_limite_retour = str(new_date_limite)
    loan.renewed = 1

    db.commit()
    db.refresh(loan)

    return {
        "id": loan.id,
        "nom_emprunteur": loan.nom_emprunteur,
        "email_emprunteur": loan.email_emprunteur,
        "titre_livre": loan.books.title,
        "statut": loan.statut.value,
        "ancienne_date_limite": old_date_limite,
        "nouvelle_date_limite": str(new_date_limite),
        "jours_ajoutes": 14,
        "renouvellements_utilises": loan.renewed,
        "renouvellements_restants": 1 - loan.renewed,
        "message": "Emprunt renouvelé avec succès (+14 jours)",
    }


@router.delete("/delete/{loan_id}")
def delete_loan(loan_id: int, db: Session = Depends(get_session)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")
    db.delete(loan)
    db.commit()
    return {"message": f"Emprunt {loan_id} supprimé"}


@router.post("/return/{loan_id}")
def return_book(loan_id: int, db: Session = Depends(get_session)):

    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    if loan.statut != StatutEmpruntEnum.ACTIF:
        raise HTTPException(
            status_code=400, detail=f"Cet emprunt a déjà le statut {loan.statut.value}"
        )

    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    date_retour_today = datetime.now().date()
    date_limite_retour = datetime.strptime(loan.date_limite_retour, "%Y-%m-%d").date()
    date_emprunt = datetime.strptime(loan.date_emprunt, "%Y-%m-%d").date()

    loan.date_retour = str(date_retour_today)

    is_late = date_retour_today > date_limite_retour
    penalty = 0

    if is_late:
        days_late = (date_retour_today - date_limite_retour).days
        penalty = days_late * 1.0
        loan.statut = StatutEmpruntEnum.EN_RETARD
    else:
        loan.statut = StatutEmpruntEnum.RETOURNE

    book.available_copies += 1

    loan_duration_days = (date_retour_today - date_emprunt).days

    db.commit()
    db.refresh(loan)

    return {
        "id": loan.id,
        "nom_emprunteur": loan.nom_emprunteur,
        "email_emprunteur": loan.email_emprunteur,
        "book_name": book.title,
        "date_emprunt": str(loan.date_emprunt),
        "date_limite_retour": str(loan.date_limite_retour),
        "date_retour": str(loan.date_retour),
        "statut": loan.statut.value,
        "is_late": is_late,
        "penalty": penalty,
        "loan_duration_days": loan_duration_days,
    }


@router.post("/add")
def ajouter_loan(loan: LoanCreate, db: Session = Depends(get_session)):
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400, detail="Le livre n'est pas disponible en ce moment"
        )

    active_loans = (
        db.query(Loan)
        .filter(
            Loan.email_emprunteur == loan.email_emprunteur,
            Loan.statut == StatutEmpruntEnum.ACTIF,
        )
        .count()
    )

    if active_loans >= 5:
        raise HTTPException(
            status_code=400, detail="Vous avez atteint la limite d'emprunts actifs (5)"
        )

    try:
        validate_available_copies(book.available_copies - 1, book.total_copies)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Le nombre de copies disponibles ne peut pas être négatif",
        )

    try:
        date_emprunt = datetime.strptime(loan.date_emprunt, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Format de date d'emprunt invalide (YYYY-MM-DD)"
        )

    date_limite_retour = date_emprunt + timedelta(days=14)

    new_loan = Loan(
        nom_emprunteur=loan.nom_emprunteur,
        email_emprunteur=loan.email_emprunteur,
        numero_carte=loan.numero_carte,
        date_emprunt=date_emprunt,
        date_limite_retour=date_limite_retour,
        date_retour=None,
        book_id=loan.book_id,
        statut="actif",
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

    loan_history = (
        db.query(LoanHistory).filter(LoanHistory.book_id == loan.book_id).first()
    )
    if not loan_history:
        loan_history = LoanHistory(book_id=loan.book_id, loan_amount=1, popularity=1)
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
        "statut": new_loan.statut,
    }


@router.put("/update/{loan_id}")
def update_loan(
    loan_id: int, loan_update: LoanUpdate, db: Session = Depends(get_session)
):
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
        try:
            datetime.strptime(loan_update.date_emprunt, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Format de date d'emprunt invalide (YYYY-MM-DD)"
            )
        loan.date_emprunt = loan_update.date_emprunt
    if loan_update.date_limite_retour is not None:
        try:
            datetime.strptime(loan_update.date_limite_retour, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Format de date limite de retour invalide (YYYY-MM-DD)",
            )
        loan.date_limite_retour = loan_update.date_limite_retour
    if loan_update.date_retour is not None:
        try:
            datetime.strptime(loan_update.date_retour, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Format de date de retour invalide (YYYY-MM-DD)"
            )
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
        "statut": loan.statut,
    }
