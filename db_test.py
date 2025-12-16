from app.models import Base, engine, Session, Livre, Auteur, Emprunt, Historique

# Créer les tables
Base.metadata.create_all(engine)

# Créer une session
session = Session()

# Insérer des données de test
# Auteurs
auteur1 = Auteur(
    nom="Dupont",
    prenom="Jean",
    biographie="Auteur français connu pour ses romans.",
    nationalite="Française",
    date_naissance="1980-05-15",
    date_deces=None
)

auteur2 = Auteur(
    nom="Martin",
    prenom="Marie",
    biographie="Écrivaine spécialisée en littérature jeunesse.",
    nationalite="Française",
    date_naissance="1975-03-22",
    date_deces=None
)

# Livres
livre1 = Livre(
    titre="Python Avancé",
    isbn="1234567890123",
    annee_publi=2023,
    auteur="Dupont Jean",
    nb_exemplaires_dispo=5,
    Descritpion="Un guide complet sur Python.",
    categorie="Informatique",
    language="Français",
    nb_pages=350,
    maison_edition="TechPress"
)

livre2 = Livre(
    titre="Les Aventures de Toto",
    isbn="9876543210987",
    annee_publi=2022,
    auteur="Martin Marie",
    nb_exemplaires_dispo=3,
    Descritpion="Un roman pour enfants.",
    categorie="Jeunesse",
    language="Français",
    nb_pages=120,
    maison_edition="KidBooks"
)

# Emprunts
emprunt1 = Emprunt(
    livre_id=1,
    nom_emprunteur="Alice Dupont",
    email_emprunteur="alice@example.com",
    date_emprunt="2023-10-01",
    date_limite_retour="2023-10-15",
    date_retour=None,
    statut="En cours"
)

emprunt2 = Emprunt(
    livre_id=2,
    nom_emprunteur="Bob Martin",
    email_emprunteur="bob@example.com",
    date_emprunt="2023-09-20",
    date_limite_retour="2023-10-04",
    date_retour="2023-10-02",
    statut="Retourné"
)

# Historiques
historique1 = Historique(
    livre_id="1",
    nmb_emprunt=10
)

historique2 = Historique(
    livre_id="2",
    nmb_emprunt=7
)

# Ajouter à la session
session.add_all([auteur1, auteur2, livre1, livre2, emprunt1, emprunt2, historique1, historique2])
session.commit()

# Afficher les données
print("=== Auteurs ===")
auteurs = session.query(Auteur).all()
for a in auteurs:
    print(f"ID: {a.id}, Nom: {a.nom} {a.prenom}, Nationalité: {a.nationalite}")

print("\n=== Livres ===")
livres = session.query(Livre).all()
for l in livres:
    print(f"ID: {l.id}, Titre: {l.titre}, Auteur: {l.auteur}, Disponible: {l.nb_exemplaires_dispo}")

print("\n=== Emprunts ===")
emprunts = session.query(Emprunt).all()
for e in emprunts:
    print(f"ID: {e.id}, Livre ID: {e.livre_id}, Emprunteur: {e.nom_emprunteur}, Statut: {e.statut}")

print("\n=== Historiques ===")
historiques = session.query(Historique).all()
for h in historiques:
    print(f"ID: {h.id}, Livre ID: {h.livre_id}, Nombre d'emprunts: {h.nmb_emprunt}")

# Fermer la session
session.close()

print("\nBase de données créée et test terminé.")