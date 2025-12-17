import re
from datetime import date, datetime

from app.exceptions import InvalidISBNException


def valider_isbn13(isbn: str) -> str:
    """
    Valide un ISBN-13 selon l'algorithme de checksum.

    Args:
        isbn: L'ISBN à valider

    Returns:
        L'ISBN nettoyé (sans tirets)

    Raises:
        InvalidISBNException: Si l'ISBN est invalide
    """
    # Nettoyer l'ISBN (enlever les tirets et espaces)
    clean_isbn = isbn.replace("-", "").replace(" ", "")

    # Vérifier le format
    if not re.match(r"^\d{13}$", clean_isbn):
        raise InvalidISBNException("L'ISBN doit être au format ISBN-13 (13 chiffres)")

    # Calculer le checksum
    total = 0
    for i, digit in enumerate(clean_isbn[:-1]):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight

    checksum = (10 - (total % 10)) % 10

    # Vérifier le checksum
    if checksum != int(clean_isbn[-1]):
        raise InvalidISBNException("Le checksum de l'ISBN est invalide")

    return clean_isbn


def valider_annee_publication(year: int) -> int:
    """
    Valide l'année de publication.

    Args:
        year: L'année à valider

    Returns:
        L'année validée

    Raises:
        ValueError: Si l'année est hors limites
    """
    current_year = datetime.now().year
    if year < 1450 or year > current_year:
        raise ValueError(f"L'année de publication doit être entre 1450 et {current_year}")
    return year


def valider_annee_naissance(annee_naissance: date, annee_deces: date | None = None) -> date:
    """
    Valide la date de naissance d'un auteur.

    Args:
        annee_naissance: La date de naissance
        annee_deces: La date de décès (optionnelle)

    Returns:
        La date de naissance validée

    Raises:
        ValueError: Si la date est invalide
    """
    if annee_naissance > date.today():
        raise ValueError("La date de naissance ne peut pas être dans le futur")

    if annee_deces and annee_naissance >= annee_deces:
        raise ValueError("La date de naissance doit être antérieure à la date de décès")

    return annee_naissance


def valider_exemplaires_disponibles(dispo: int, total: int) -> int:
    """
    Valide que les exemplaires disponibles ne dépassent pas le total.

    Args:
        dispo: Nombre d'exemplaires disponibles
        total: Nombre total d'exemplaires

    Returns:
        Le nombre d'exemplaires disponibles validé

    Raises:
        ValueError: Si la validation échoue
    """
    if dispo < 0:
        raise ValueError("Le nombre d'exemplaires disponibles ne peut pas être négatif")

    if dispo > total:
        raise ValueError("Le nombre d'exemplaires disponibles ne peut pas dépasser le total")

    return dispo
