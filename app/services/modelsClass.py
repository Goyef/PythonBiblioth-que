# #liçvres
# class Livre:
#     def __init__(self, id : int, titre: str, isbn: str, annee_publi: int, auteur: str, nb_exemplaires_dispo: int, Descritpion: str, categorie: str, language: str, nb_pages: int, maison_edition: str):
#         self.id = id
#         self.titre = titre
#         self.isbn = isbn
#         self.annee_publi = annee_publi
#         self.auteur = auteur
#         self.nb_exemplaires_dispo = nb_exemplaires_dispo
#         self.Descritpion = Descritpion
#         self.categorie = categorie
#         self.language = language
#         self.nb_pages = nb_pages
#         self.maison_edition = maison_edition

#     def fetch_info(self, id: int):
#         if id == self.id:
#             return [self.id, self.titre, self.isbn, self.annee_publi, self.auteur, self.nb_exemplaires_dispo, self.Descritpion, self.categorie, self.language, self.nb_pages, self.maison_edition]
# #auteur
# class Auteur:
#     def __init__(self, id: int, nom: str, prenom: str, biographie: str,nationalite: str, date_naissance: str, date_deces: str):
#         self.id = id
#         self.nom = nom
#         self.prenom = prenom
#         self.biographie = biographie
#         self.nationalite = nationalite
#         self.date_naissance = date_naissance
#         self.date_deces = date_deces

# #emprunt
# class Emprunt:
#     def __init__(self, id: int, livre_id: int, nom_emprunteur: str, email_emprunteur: str, date_emprunt: str, date_limite_retour: str, date_retour: str, statut: str):
#         self.id = id
#         self.livre_id = livre_id
#         self.nom_emprunteur = nom_emprunteur
#         self.email_emprunteur = email_emprunteur
#         self.date_emprunt = date_emprunt
#         self.date_limite_retour = date_limite_retour
#         self.date_retour = date_retour
#         self.statut = statut
        

# #historique
# class Historique:
#     def __init__(self, id: int, livre_id: str, nmb_emprunt: int):
#         self.id = id
#         self.livre_id = livre_id
#         self.nmb_emprunt = nmb_emprunt