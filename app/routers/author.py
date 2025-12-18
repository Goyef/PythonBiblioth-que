from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Session as SessionLocal, Auteur

router = APIRouter(
    prefix="/auteurs",
    tags=["auteurs"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/auteurs")
def get_auteurs(page: int = 1, db: Session = Depends(get_db)):
    per_page = 5
    offset = (page - 1) * per_page
    auteurs = db.query(Auteur).offset(offset).limit(per_page).all()
    # nom = db.query(Auteur).offset(offset).limit(per_page).all()
    # prenom = db.query(Auteur).offset(offset).limit(per_page).all()
    # date_naissance = db.query(Auteur).offset(offset).limit(per_page).all()
    # date_deces = db.query(Auteur).offset(offset).limit(per_page).all()
    return {
        "auteurs": [{"id": a.id, "nom": a.nom, "prenom": a.prenom, "date_naissance": a.date_naissance, "date_deces": a.date_deces} for a in auteurs],
        "page": page,
        "total": db.query(Auteur).count(),
        "pages": (db.query(Auteur).count() + per_page - 1)
    }

@router.delete("/delete/{auteur_id}")
def delete_auteur(auteur_id: int, db: Session = Depends(get_db)):
    auteur = db.query(Auteur).filter(Auteur.id == auteur_id).first()
    if not auteur:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")
    db.delete(auteur)
    db.commit()
    return {"message": f"Auteur {auteur_id} supprimé"}

@router.post("/add")
def ajouter_auteur(nom: str, prenom: str, biographie: str, nationalite: str, date_naissance: str, date_deces: str | None = None, db: Session = Depends(get_db)):
    new_auteur = Auteur(
        nom=nom,
        prenom=prenom,
        biographie=biographie,
        nationalite=nationalite,
        date_naissance=date_naissance,
        date_deces=date_deces
    )
    db.add(new_auteur)
    db.commit()
    db.refresh(new_auteur)
    return {"message": "Auteur ajouté avec succès", "auteur_id": new_auteur.id}

@router.put("/update/{auteur_id}")
def update_auteur(auteur_id: int, nom: str | None = None, prenom: str | None = None, biographie: str | None = None, nationalite: str | None = None, date_naissance: str | None = None, date_deces: str | None = None, db: Session = Depends(get_db)):
    auteur = db.query(Auteur).filter(Auteur.id == auteur_id).first()
    if not auteur:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")
    
    if nom is not None:
        auteur.nom = nom
    if prenom is not None:
        auteur.prenom = prenom
    if biographie is not None:
        auteur.biographie = biographie
    if nationalite is not None:
        auteur.nationalite = nationalite
    if date_naissance is not None:
        auteur.date_naissance = date_naissance
    if date_deces is not None:
        auteur.date_deces = date_deces
    
    db.commit()
    db.refresh(auteur)
    return {"message": "Auteur mis à jour avec succès", "auteur_id": auteur.id}