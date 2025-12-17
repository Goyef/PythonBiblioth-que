from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Session as SessionLocal, Livre

router = APIRouter(
    prefix="/livres",
    tags=["livres"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_livres(page: int = 1, db: Session = Depends(get_db)):
    per_page = 5
    offset = (page - 1) * per_page
    livres = db.query(Livre).offset(offset).limit(per_page).all()
    total = db.query(Livre).count()
    pages = (total + per_page - 1) // per_page
    return {
        "livres": [{"id": l.id, "titre": l.titre, "auteur": l.auteur, "annee_publi": l.annee_publi} for l in livres],
        "page": page,
        "total": total,
        "pages": pages
    }

@router.delete("/{livre_id}")
def delete_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    db.delete(livre)
    db.commit()
    return {"message": f"Livre {livre_id} supprimé"}

@router.post("/add")
def ajouter_livre(titre: str, isbn: str, annee_publi: int, auteur: str, nb_exemplaires_dispo: int, Descritpion: str, categorie: str, language: str, nb_pages: int, maison_edition: str, db: Session = Depends(get_db)):
    new_livre = Livre(
        titre=titre,
        isbn=isbn,
        annee_publi=annee_publi,
        auteur=auteur,
        nb_exemplaires_dispo=nb_exemplaires_dispo,
        Descritpion=Descritpion,
        categorie=categorie,
        language=language,
        nb_pages=nb_pages,
        maison_edition=maison_edition
    )
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)
    return {"message": "Livre ajouté avec succès", "livre_id": new_livre.id}

@router.put("/update/{livre_id}")
def update_livre(livre_id: int, titre: str | None = None, isbn: str | None = None, annee_publi: int | None = None, auteur: str | None = None, nb_exemplaires_dispo: int | None = None, Descritpion: str | None = None, categorie: str | None = None, language: str | None = None, nb_pages: int | None = None, maison_edition: str | None = None, db: Session = Depends(get_db)):
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if titre is not None:
        livre.titre = titre
    if isbn is not None:
        livre.isbn = isbn
    if annee_publi is not None:
        livre.annee_publi = annee_publi
    if auteur is not None:
        livre.auteur = auteur
    if nb_exemplaires_dispo is not None:
        livre.nb_exemplaires_dispo = nb_exemplaires_dispo
    if Descritpion is not None:
        livre.Descritpion = Descritpion
    if categorie is not None:
        livre.categorie = categorie
    if language is not None:
        livre.language = language
    if nb_pages is not None:
        livre.nb_pages = nb_pages
    if maison_edition is not None:
        livre.maison_edition = maison_edition

    db.commit()
    return {"message": f"Livre {livre_id} mis à jour avec succès"}