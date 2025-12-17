from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, or_, select

from app.database import SessionDep
from app.models.auteur import Auteur
from app.models.livre import Livre, Categorie_Livre
# from app.models.emprunt import Emprunt, EmpruntStatus
from app.schemas.livre import BookCreate, BookRead, BookReadWithAuthor, BookUpdate
from app.schemas.common import MessageResponse, PaginatedResponse

router = APIRouter(prefix="/books", tags=["Livres"])


@router.post("/", response_model=BookRead, status_code=201)
def create_book(book: BookCreate, session: SessionDep):
    """Créer un nouveau livre"""
    # Vérifier l'unicité de l'ISBN
    statement = select(Livre).where(Livre.isbn == book.isbn)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Un livre avec l'ISBN {book.isbn} existe déjà")

    # Vérifier que l'auteur existe
    author = session.get(Auteur, book.auteur_id)
    if not author:
        raise HTTPException(status_code=404, detail="Auteur non trouvé")

    db_book = Livre.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.get("/", response_model=PaginatedResponse[BookRead])
def list_books(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("title", regex="^(title|publication_year|author_id|available_copies)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
):
    """Lister tous les livres avec pagination"""
    # Construction de la requête de base
    statement = select(Livre)

    # Tri
    sort_column = getattr(Livre, sort_by)
    if order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column)

    # Compter le total
    count_statement = select(func.count()).select_from(Livre)
    total = session.exec(count_statement).one()

    # Pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    books = session.exec(statement).all()

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/search", response_model=PaginatedResponse[BookReadWithAuthor])
def search_books(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    title: Optional[str] = None,
    author_name: Optional[str] = None,
    isbn: Optional[str] = None,
    category: Optional[Categorie_Livre] = None,
    year: Optional[int] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    language: Optional[str] = None,
    available_only: bool = False,
):
    """Recherche avancée de livres avec multiples critères"""
    # Construction de la requête avec jointure sur Author
    statement = select(Livre, Auteur).join(Auteur, Livre.auteur_id == Auteur.id)

    # Appliquer les filtres
    if title:
        statement = statement.where(Livre.titre(f"%{title}%"))
    if author_name:
        statement = statement.where(
            or_(
                Auteur.prenom(f"%{author_name}%"),
                Auteur.nom(f"%{author_name}%"),
            )
        )

    if isbn:
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        statement = statement.where(Livre.isbn == clean_isbn)

    if category:
        statement = statement.where(Livre.categorie == category)

    if year:
        statement = statement.where(Livre.annee_publi == year)

    if year_min:
        statement = statement.where(Livre.annee_publi >= year_min)

    if year_max:
        statement = statement.where(Livre.annee_publi <= year_max)

    if language:
        statement = statement.where(Livre.language == language.lower())

    if available_only:
        statement = statement.where(Livre.nb_exemplaires_dispo > 0)

    # Compter le total
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # Pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    results = session.exec(statement).all()

    # Construire les réponses avec les informations de l'auteur
    books_with_authors = []
    for book, author in results:
        # Compter les emprunts
        loans_count = session.exec(select(func.count()).where(Emprunt.livre_id == book.id)).one()

        book_dict = book.model_dump()
        book_dict["author_name"] = f"{author.prenom} {author.nom}"
        book_dict["loans_count"] = loans_count
        books_with_authors.append(BookReadWithAuthor(**book_dict))

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=books_with_authors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{book_id}", response_model=BookReadWithAuthor)
def get_book(book_id: int, session: SessionDep):
    """Récupérer les détails complets d'un livre"""
    book = session.get(Livre, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Récupérer l'auteur
    author = session.get(Auteur, book.author_id)
    author_name = f"{author.prenom} {author.nom}" if author else "Inconnu"

    # Compter les emprunts
    loans_count = session.exec(select(func.count()).where(Emprunt.livre_id == book_id)).one()
    book_dict = book.model_dump()
    book_dict["author_name"] = author_name
    book_dict["loans_count"] = loans_count

    return BookReadWithAuthor(**book_dict)


@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_update: BookUpdate, session: SessionDep):
    """Mettre à jour un livre"""
    db_book = session.get(Livre, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Mettre à jour uniquement les champs fournis
    update_data = book_update.model_dump(exclude_unset=True)

    # Vérifier l'unicité de l'ISBN si modifié
    if "isbn" in update_data:
        statement = select(Livre).where(Livre.isbn == update_data["isbn"], Livre.id != book_id)
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un livre avec l'ISBN {update_data['isbn']} existe déjà",
            )

    # Vérifier que l'auteur existe si modifié
    if "author_id" in update_data:
        author = session.get(Auteur, update_data["author_id"])
        if not author:
            raise HTTPException(status_code=404, detail="Auteur non trouvé")

    # Valider la cohérence des copies si modifiées
    available = update_data.get("available_copies", db_book.available_copies)
    total = update_data.get("total_copies", db_book.total_copies)
    if available > total:
        raise HTTPException(
            status_code=400,
            detail="Le nombre d'exemplaires disponibles ne peut pas dépasser le total",
        )

    for key, value in update_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(book_id: int, session: SessionDep):
    """Supprimer un livre (seulement s'il n'a pas d'emprunts actifs)"""
    db_book = session.get(Livre, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    # Vérifier qu'il n'y a pas d'emprunts actifs
    active_loans = session.exec(
        select(func.count()).where(
            Emprunt.livre_id == book_id,
            or_(Emprunt.statut == EmpruntStatus.ACTIVE, Emprunt.statut == EmpruntStatus.LATE),
        )
    ).one()

    if active_loans > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer le livre car il a {active_loans} emprunt(s) actif(s)",
        )

    session.delete(db_book)
    session.commit()
    return MessageResponse(
        message="Livre supprimé avec succès", detail=f"Le livre '{db_book.title}' a été supprimé"
    )
