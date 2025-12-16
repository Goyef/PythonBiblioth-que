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

@router.get("/all")
def get_livres(db: Session = Depends(get_db)):
    livres = db.query(Livre).all()
    return {"livres": [{"id": l.id, "titre": l.titre, "auteur": l.auteur, "annee_publi": l.annee_publi} for l in livres]}

@router.delete("/{livre_id}")
def delete_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(Livre).filter(Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    db.delete(livre)
    db.commit()
    return {"message": f"Livre {livre_id} supprimé"}