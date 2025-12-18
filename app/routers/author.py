from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Author as Auteur
from app.database import get_session

router = APIRouter(
    prefix="/authors",
    tags=["authors"]
)

@router.get("/authors")
def get_authors(page: int = 1, db: Session = Depends(get_session)):
    per_page = 5
    offset = (page - 1) * per_page
    authors = db.query(Auteur).offset(offset).limit(per_page).all()
    # nom = db.query(Auteur).offset(offset).limit(per_page).all()
    # prenom = db.query(Auteur).offset(offset).limit(per_page).all()
    # date_naissance = db.query(Auteur).offset(offset).limit(per_page).all()
    # date_deces = db.query(Auteur).offset(offset).limit(per_page).all()
    return {
        "authors": [{"id": a.id, "nom": a.last_name, "prenom": a.first_name, "date_naissance": a.birthdate, "date_deces": a.death_date} for a in authors],
        "page": page,
        "total": db.query(Auteur).count(),
        "pages": (db.query(Auteur).count() + per_page - 1)
    }

@router.delete("/delete/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_session)):
    author = db.query(Auteur).filter(Auteur.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")
    db.delete(author)
    db.commit()
    return {"message": f"Auteur {author_id} supprimé"}
@router.post("/add")
def ajouter_auteur(last_name: str, first_name: str, biographie: str, nationalite: str, date_naissance: str, date_deces: str | None = None, db: Session = Depends(get_session)):
    new_auteur = Auteur(
        last_name=last_name,
        first_name=first_name,
        biographie=biographie,
        nationalite=nationalite,
        birthdate=date_naissance,
        death_date=date_deces
    )
    db.add(new_auteur)
    db.commit()
    db.refresh(new_auteur)
    return {"message": "Auteur ajouté avec succès", "auteur_id": new_auteur.id}

@router.put("/update/{author_id}")
def update_auteur(author_id: int, last_name: str | None = None, first_name: str | None = None, biographie: str | None = None, nationalite: str | None = None, birthdate: str | None = None, death_date: str | None = None, db: Session = Depends(get_session)):
    author = db.query(Auteur).filter(Auteur.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    if last_name is not None:
        author.last_name = last_name
    if first_name is not None:
        author.first_name = first_name
    if biographie is not None:
        author .biographie = biographie
    if nationalite is not None:
        author.nationalite = nationalite
    if birthdate is not None:
        author.birthdate = birthdate
    if death_date is not None:
        author.death_date = death_date

    db.commit()
    db.refresh(author)
    return {"message": "Auteur mis à jour avec succès", "auteur_id": author.id}