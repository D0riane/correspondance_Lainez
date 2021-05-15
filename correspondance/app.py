# Import des modules nécessaires au fonctionnement de l'application.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .constantes import SECRET_KEY

# Stockage des chemins
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

# Définition de l'application
app = Flask(
    "Application",
    template_folder=templates,
    static_folder=statics
)

# Confinguration du "secret"
app.config['SECRET_KEY'] = SECRET_KEY
# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
# Initiation de l'extension
db = SQLAlchemy(app)

# Mise en place de la gestion d'utilisateur-rice-s
login = LoginManager(app)

# Import les routes nécessaires au fonctionnement de l'application à son lancement.
from .routes import generic
from .routes import api
from .filters import split_new_lines
