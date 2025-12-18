from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import  Author, Book, CategorieEnum
from app.database import get_session
from app.exceptions import AuthorNotFoundException

router = APIRouter(
    prefix="/books",
    tags=["Livres"]
)


@router.get("/")
def get_livres(page: int = 1, db: Session = Depends(get_session)):
    per_page = 5
    offset = (page - 1) * per_page
    livres = db.query(Book).offset(offset).limit(per_page).all()
    total = db.query(Book).count()
    pages = (total + per_page - 1) // per_page
    return {
        "livres": [{"id": l.id, "titre": l.title, "auteur id": l.author_id, "annee_publi": l.publication_year} for l in livres],
        "page": page,
        "total": total,
        "pages": pages
    }

@router.get("/{livre_id}")
def get_livre_detail(livre_id: int, db: Session = Depends(get_session)):
    livre = db.query(Book).filter(Book.id == livre_id).first()

    return {
        "id": livre.id,
        "titre": livre.title,
        "isbn": livre.isbn,
        "annee_publi": livre.publication_year,
        "auteur ": livre.authors.first_name + " " + livre.authors.last_name,
        "nb_exemplaires_dispo": livre.available_copies,
        "description": livre.description,
        "categorie": livre.category,
        "language": livre.language,
        "nb_pages": livre.pages,
        "maison_edition": livre.publisher
    }
@router.delete("/{livre_id}")
def delete_livre(livre_id: int, db: Session = Depends(get_session)):
    livre = db.query(Book).filter(Book.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    db.delete(livre)
    db.commit()
    return {"message": f"Livre {livre_id} supprimé"}

@router.post("/add")
def ajouter_livre(title: str, isbn: str, publication_year: int, author_id: str, available_copies: int, description: str, category: str, language: str, pages: int, publisher: str, db: Session = Depends(get_session)):
    new_livre = Book(
        title=title,
        isbn=isbn,
        publication_year=publication_year,
        author_id=author_id,
        available_copies=available_copies,
        description=description,
        category=category,
        language=language,
        pages=pages,
        publisher=publisher
    )

    author = db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    cat_enum = CategorieEnum.AUTRE
    if category.upper() in CategorieEnum.__members__:
        cat_enum = CategorieEnum[category.upper()]
        new_livre.category = cat_enum
    else:
        new_livre.category = CategorieEnum.AUTRE
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)
    return {"message": "Livre ajouté avec succès", "livre_id": new_livre.id}

@router.put("/update/{livre_id}")
def update_livre(livre_id: int, titre: str | None = None, isbn: str | None = None, annee_publi: int | None = None, auteur: str | None = None, nb_exemplaires_dispo: int | None = None, Descritpion: str | None = None, categorie: str | None = None, language: str | None = None, nb_pages: int | None = None, maison_edition: str | None = None, db: Session = Depends(get_session)):
    livre = db.query(Book).filter(Book.id == livre_id).first()
    
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