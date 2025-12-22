from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import  Author, Book, CategorieEnum
from app.database import get_session
from app.schemas.book import BookCreate, BookRead, BookReadWithAuthor, BookUpdate
from app.schemas.common import PaginatedResponse
from typing import Optional
router = APIRouter(
    prefix="/books",
    tags=["Livres"]
)


@router.get("/" )
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

@router.get("/{livre_id}", response_model=BookReadWithAuthor)
def get_livre_detail(livre_id: int, db: Session = Depends(get_session)):
    livre = db.query(Book).filter(Book.id == livre_id).first()
    
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    return {
        "id": livre.id,
        "title": livre.title,
        "isbn": livre.isbn,
        "publication_year": livre.publication_year,
        "author_id": livre.author_id,
        "available_copies": livre.available_copies,
        "total_copies": livre.total_copies,
        "description": livre.description,
        "category": livre.category,
        "language": livre.language,
        "pages": livre.pages,
        "publisher": livre.publisher,
        "author_name": livre.authors.first_name + " " + livre.authors.last_name,
        "loans_count": 0
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
def ajouter_livre(book: BookCreate, db: Session = Depends(get_session)):
    new_livre = Book(
        title=book.title,
        isbn=book.isbn,
        publication_year=book.publication_year,
        author_id=book.author_id,
        available_copies=book.available_copies,
        total_copies=book.total_copies,
        description=book.description,
        category=book.category,
        language=book.language,
        pages=book.pages,
        publisher=book.publisher
    )

    author = db.get(Author, book.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    cat_enum = CategorieEnum.AUTRE
    if book.category is not None:
        cat_enum = book.category
        cat_enum = CategorieEnum[book.category.upper()]
        new_livre.category = cat_enum
    else:
        new_livre.category = CategorieEnum.AUTRE
    db.add(new_livre)
    db.commit()
    db.refresh(new_livre)
    return {"message": "Livre ajouté avec succès", "livre_id": new_livre.id}

@router.put("/update/{livre_id}")
def update_livre(livre_id: int, book_update: BookUpdate, db: Session = Depends(get_session)):
    livre = db.query(Book).filter(Book.id == livre_id).first()
    
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if book_update.title is not None:
        livre.title = book_update.title
    if book_update.isbn is not None:
        livre.isbn = book_update.isbn
    if book_update.publication_year is not None:
        livre.publication_year = book_update.publication_year
    if book_update.author_id is not None:
        livre.author_id = book_update.author_id
    if book_update.available_copies is not None:
        livre.available_copies = book_update.available_copies
    if book_update.description is not None:
        livre.description = book_update.description
    if book_update.category is not None:
        livre.category = book_update.category
    if book_update.language is not None:
        livre.language = book_update.language
    if book_update.pages is not None:
        livre.pages = book_update.pages
    if book_update.publisher is not None:
        livre.publisher = book_update.publisher

    db.commit()
    return {"message": f"Livre {livre_id} mis à jour avec succès"}