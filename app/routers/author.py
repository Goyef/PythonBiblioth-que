from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models import Author as Auteur
from app.database import get_session
from app.schemas.author import AuthorRead
from app.models import Book


router = APIRouter(prefix="/authors", tags=["Auteurs"])


@router.get("/search")
def search_authors(
    page: int = 1,
    per_page: int = 5,
    name: str = None,
    nationalite: str = None,
    sort_by: str = "last_name",
    order: str = "asc",
    db: Session = Depends(get_session),
):
    sort_columns = {
        "last_name": Auteur.last_name,
        "first_name": Auteur.first_name,
        "birthdate": Auteur.birthdate,
    }

    sort_column = sort_columns.get(sort_by, Auteur.last_name)
    sort_direction = desc if order == "desc" else asc

    query = db.query(Auteur)

    if name:
        query = query.filter(
            (Auteur.first_name.ilike(f"%{name}%"))
            | (Auteur.last_name.ilike(f"%{name}%"))
        )

    if nationalite:
        query = query.filter(Auteur.nationalite.ilike(f"%{nationalite}%"))

    total = query.count()
    pages = (total + per_page - 1) // per_page

    offset = (page - 1) * per_page
    authors = (
        query.order_by(sort_direction(sort_column)).offset(offset).limit(per_page).all()
    )

    return {
        "authors": [
            {
                "id": a.id,
                "nom": a.last_name,
                "prenom": a.first_name,
                "nationalite": a.nationalite,
                "date_naissance": a.birthdate,
                "date_deces": a.death_date,
                "biographie": a.biographie,
            }
            for a in authors
        ],
        "pagination": {
            "page n°": page,
            "authors_per_page": per_page,
            "number of authors": total,
            "number of pages": pages,
        },
        "sort": {"sort_by": sort_by, "order": order},
        "filters": {"name": name, "nationalite": nationalite},
    }


@router.get("/")
def get_authors(page: int = 1, db: Session = Depends(get_session)):
    per_page = 5
    offset = (page - 1) * per_page
    authors = db.query(Auteur).offset(offset).limit(per_page).all()
    return {
        "authors": [
            {
                "id": a.id,
                "nom": a.last_name,
                "prenom": a.first_name,
                "date_naissance": a.birthdate,
                "date_deces": a.death_date,
            }
            for a in authors
        ],
        "page": page,
        "total": db.query(Auteur).count(),
        "pages": (db.query(Auteur).count() + per_page - 1),
    }


@router.get("/{author_id}")
def get_author_detail(author_id: int, db: Session = Depends(get_session)):
    author = db.query(Auteur).filter(Auteur.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    livres = db.query(Book).filter(Book.author_id == author_id).all()

    return {
        "id": author.id,
        "last_name": author.last_name,
        "first_name": author.first_name,
        "nationalite": author.nationalite,
        "birthdate": author.birthdate,
        "death_date": author.death_date,
        "biographie": author.biographie,
        "livres": [
            {
                "id": l.id,
                "titre": l.title,
                "isbn": l.isbn,
                "annee_publi": l.publication_year,
                "categorie": l.category,
            }
            for l in livres
        ],
    }


@router.delete("/delete/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_session)):
    from app.models import Book

    author = db.query(Auteur).filter(Auteur.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    livres_count = db.query(Book).filter(Book.author_id == author_id).count()
    if livres_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer cet auteur: il a a minimun un livre associé.",
        )

    db.delete(author)
    db.commit()
    return {"message": f"Auteur {author_id} supprimé"}


@router.post("/add")
def ajouter_auteur(
    last_name: str,
    first_name: str,
    nationalite: str,
    date_naissance: str,
    biographie: str | None = None,
    date_deces: str | None = None,
    db: Session = Depends(get_session),
):
    new_auteur = Auteur(
        last_name=last_name,
        first_name=first_name,
        biographie=biographie,
        nationalite=nationalite,
        birthdate=date_naissance,
        death_date=date_deces,
    )
    author_exist = (
        db.query(Auteur)
        .filter(Auteur.last_name == last_name, Auteur.first_name == first_name)
        .first()
    )
    if author_exist:
        raise HTTPException(status_code=400, detail="Auteur déjà existant")

    db.add(new_auteur)
    db.commit()
    db.refresh(new_auteur)
    return {
        "id": new_auteur.id,
        "last_name": new_auteur.last_name,
        "first_name": new_auteur.first_name,
        "nationalite": new_auteur.nationalite,
        "birthdate": new_auteur.birthdate,
        "death_date": new_auteur.death_date,
        "biographie": new_auteur.biographie,
        "livres": [],
        "nombre_livres": 0,
    }


@router.put("/update/{author_id}")
def update_auteur(
    author_id: int,
    last_name: str | None = None,
    first_name: str | None = None,
    biographie: str | None = None,
    nationalite: str | None = None,
    birthdate: str | None = None,
    death_date: str | None = None,
    db: Session = Depends(get_session),
):
    author = db.query(Auteur).filter(Auteur.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    if last_name is not None:
        author.last_name = last_name
    if first_name is not None:
        author.first_name = first_name
    if biographie is not None:
        author.biographie = biographie
    if nationalite is not None:
        author.nationalite = nationalite
    if birthdate is not None:
        author.birthdate = birthdate
    if death_date is not None:
        author.death_date = death_date

    db.commit()
    db.refresh(author)

    from app.models import Book

    livres = db.query(Book).filter(Book.author_id == author_id).all()

    return {
        "id": author.id,
        "last_name": author.last_name,
        "first_name": author.first_name,
        "nationalite": author.nationalite,
        "birthdate": author.birthdate,
        "death_date": author.death_date,
        "biographie": author.biographie,
        "livres": [
            {
                "id": l.id,
                "titre": l.title,
                "isbn": l.isbn,
                "annee_publi": l.publication_year,
                "categorie": l.category,
            }
            for l in livres
        ],
        "nombre_livres": len(livres),
    }
