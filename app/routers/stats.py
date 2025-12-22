from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Book, Loan, Author, StatutEmpruntEnum, LoanHistory
from app.database import get_session

router = APIRouter(prefix="/stats", tags=["Statistiques"])


@router.get("/global")
def obtenir_stats_globales(db: Session = Depends(get_session)):

    total_livres = db.query(func.count(Book.id)).scalar() or 0

    total_exemplaires = db.query(func.sum(Book.total_copies)).scalar() or 0
    exemplaires_disponibles = db.query(func.sum(Book.available_copies)).scalar() or 0
    exemplaires_empruntes = (total_exemplaires or 0) - (exemplaires_disponibles or 0)

    emprunts_actifs = (
        db.query(func.count(Loan.id))
        .filter(Loan.statut == StatutEmpruntEnum.ACTIF)
        .scalar()
        or 0
    )

    emprunts_retard = (
        db.query(func.count(Loan.id))
        .filter(Loan.statut == StatutEmpruntEnum.EN_RETARD)
        .scalar()
        or 0
    )

    emprunts_retournes = (
        db.query(func.count(Loan.id))
        .filter(Loan.statut == StatutEmpruntEnum.RETOURNE)
        .scalar()
        or 0
    )

    total_emprunts = emprunts_actifs + emprunts_retard + emprunts_retournes

    taux_occupation = 0.0
    if total_exemplaires > 0:
        taux_occupation = (exemplaires_empruntes / total_exemplaires) * 100

    livres_disponibles = (
        db.query(func.count(Book.id)).filter(Book.available_copies > 0).scalar() or 0
    )
    livres_rupture_stock = total_livres - livres_disponibles

    return {
        "catalogue": {
            "total_livres": total_livres,
            "livres_en_stock": livres_disponibles,
            "livres_hors_stock": livres_rupture_stock,
        },
        "inventaire": {
            "total_exemplaires": total_exemplaires,
            "exemplaires_disponibles": exemplaires_disponibles,
            "exemplaires_empruntes": exemplaires_empruntes,
        },
        "emprunts": {
            "emprunts_actifs": emprunts_actifs,
            "emprunts_retard": emprunts_retard,
            "emprunts_retournes": emprunts_retournes,
            "total_emprunts": total_emprunts,
        },
        "indicateurs": {"taux_occupation_pourcent": round(taux_occupation, 2)},
    }
