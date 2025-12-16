from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Créer la base de données
engine = create_engine("sqlite:///bibliotheque.db")
Base.metadata.create_all(engine)

# Session
Session = sessionmaker(bind=engine)
session = Session()

# Créer des objets
auteur = Auteur(
    nom="Dupont",
    prenom="Jean",
    email="jean@example.com"
)

livre = Livre(
    titre="Python Avancé",
    isbn="1234567890123",
    prix=39.99,
    auteur=auteur
)

# Sauvegarder
session.add(auteur)
session.add(livre)
session.commit()

# Requêtes
tous_livres = session.query(Livre).all()
livre_par_isbn = session.query(Livre).filter_by(isbn="1234567890123").first()

# Avec relations
auteur = session.query(Auteur).first()
for livre in auteur.livres:
    print(livre.titre)