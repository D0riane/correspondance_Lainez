import os

# on définit les chemins
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
print(chemin_actuel)

templates = os.path.join(chemin_actuel, "correspondance", "templates")
print(templates)
