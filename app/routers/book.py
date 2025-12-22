from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
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
def get_livres(page: int = 1, per_page: int = 5, sort_by: str = "title", order: str = "asc", db: Session = Depends(get_session)):
    sort_column = Book.title
    if sort_by == "author":
        sort_column = Author.last_name
    elif sort_by == "year":
        sort_column = Book.publication_year
    elif sort_by == "popularity":
        sort_column = Book.available_copies
    
    sort_direction = desc if order == "desc" else asc
    
    if sort_by == "author":
        total = db.query(Book).join(Author).count()
        query = db.query(Book).join(Author).order_by(sort_direction(sort_column))
    else:
        total = db.query(Book).count()
        query = db.query(Book).order_by(sort_direction(sort_column))
    
    pages = (total + per_page - 1) // per_page
    
    offset = (page - 1) * per_page
    livres = query.offset(offset).limit(per_page).all()
    
    return {
        "livres": [
            {
                "id": l.id,
                "titre": l.title,
                "isbn": l.isbn,
                "auteur id": l.author_id,
                "auteur": l.authors.first_name + " " + l.authors.last_name,
                "annee_publi": l.publication_year,
                "available_copies": l.available_copies,
                "total_copies": l.total_copies
            } for l in livres
        ],
        "pagination": {
            "page n°": page,
            "book_per_page": per_page,
            "number of books": total,
            "number of pages": pages
        },
        "sort": {
            "sort_by": sort_by,
            "order": order
        }
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
@router.get("/search")
def search_livres(
    page: int = 1,
    per_page: int = 5,
    title: str = None,
    author: str = None,
    isbn: str = None,
    category: str = None,
    year: int = None,
    year_min: int = None,
    year_max: int = None,
    language: str = None,
    available_only: bool = False,
    db: Session = Depends(get_session)
):
    query = db.query(Book)
    
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    
    if author:
        query = query.join(Author).filter(
            (Author.first_name.ilike(f"%{author}%")) | 
            (Author.last_name.ilike(f"%{author}%"))
        )
    
    if isbn:
        query = query.filter(Book.isbn == isbn)
    
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    
    if year:
        query = query.filter(Book.publication_year == year)
    if year_min:
        query = query.filter(Book.publication_year >= year_min)
    if year_max:
        query = query.filter(Book.publication_year <= year_max)
    
    if language:
        query = query.filter(Book.language.ilike(f"%{language}%"))
    
    if available_only:
        query = query.filter(Book.available_copies > 0)
    
    total = query.count()
    pages = (total + per_page - 1) // per_page
    
    offset = (page - 1) * per_page
    livres = query.offset(offset).limit(per_page).all()
    
    return {
        "livres": [
            {
                "id": l.id,
                "titre": l.title,
                "isbn": l.isbn,
                "auteur id": l.author_id,
                "auteur": l.authors.first_name + " " + l.authors.last_name if l.authors else "Inconnu",
                "annee_publi": l.publication_year,
                "categorie": l.category,
                "langue": l.language,
                "available_copies": l.available_copies,
                "total_copies": l.total_copies
            } for l in livres
        ],
        "pagination": {
            "page n°": page,
            "book_per_page": per_page,
            "number of books": total,
            "number of pages": pages
        },
        "filters": {
            "title": title,
            "author": author,
            "isbn": isbn,
            "category": category,
            "year": year,
            "year_min": year_min,
            "year_max": year_max,
            "language": language,
            "available_only": available_only
        }
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
    isbn_exist = db.query(Book).filter(Book.isbn == book.isbn).first()
    if isbn_exist:
        raise HTTPException(status_code=400, detail="ISBN déjà existant")
    
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
    return {
        "id": new_livre.id,
        "title": new_livre.title,
        "isbn": new_livre.isbn,
        "publication_year": new_livre.publication_year,
        "author_id": new_livre.author_id,
        "available_copies": new_livre.available_copies,
        "total_copies": new_livre.total_copies,
        "description": new_livre.description,
        "category": new_livre.category,
        "language": new_livre.language,
        "pages": new_livre.pages,
        "publisher": new_livre.publisher,
        "author_name": new_livre.authors.first_name + " " + new_livre.authors.last_name
    }

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
        
    if book_update.isbn is not None and book_update.isbn != livre.isbn:
        isbn_exist = db.query(Book).filter(Book.isbn == book_update.isbn).first()
        if isbn_exist:
            raise HTTPException(status_code=400, detail="ISBN déjà existant")
    db.commit()
    db.refresh(livre)
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
        "author_name": livre.authors.first_name + " " + livre.authors.last_name
    }