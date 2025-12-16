from app.models import Base, engine, Session, Auteur, Livre

# Créer la base de données
Base.metadata.create_all(engine)

# Session
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
print("Tous les livres:")
for livre in tous_livres:
    print(f"- {livre.titre} par {livre.auteur.nom} {livre.auteur.prenom}")

livre_par_isbn = session.query(Livre).filter_by(isbn="1234567890123").first()
print(f"\nLivre par ISBN: {livre_par_isbn.titre}")

# Avec relations
auteur = session.query(Auteur).first()
print(f"\nLivres de {auteur.nom} {auteur.prenom}:")
for livre in auteur.livres:
    print(f"- {livre.titre}")

# Fermer la session
session.close()