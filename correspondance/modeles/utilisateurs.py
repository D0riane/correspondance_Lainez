from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .. app import db, login


# Table des utilisateurs :
class Utilisateur(UserMixin, db.Model):
    __tablename__ = "utilisateur"
    ut_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    ut_nom = db.Column(db.Text, nullable=False)
    ut_login = db.Column(db.Text, nullable=False)
    ut_mdp = db.Column(db.Text, nullable=False)
    ut_mail = db.Column(db.Text, nullable=False)
    contributions = db.relationship("Contribution", back_populates="utilisateur")

    @staticmethod
    def identification(login, motdepasse):
        """ Identifie un utilisateur. Si cela fonctionne, renvoie les données de l'utilisateurs.
        :param login: Login de l'utilisateur
        :param motdepasse: Mot de passe de l'utilisateur
        :returns: Si réussite, données de l'utilisateur. Sinon None
        :rtype: User or None
        """
        # Vérification que le login et le mot de passe correspondent à un utilisateur enregistré dans la BD :
        utilisateur = Utilisateur.query.filter(Utilisateur.ut_login == login).first()
        if utilisateur and check_password_hash(utilisateur.ut_mdp, motdepasse):
            return utilisateur
        return None

    @staticmethod
    def nouvel_utilisateur(login, email, nom, motdepasse):
        """
        Crée un compte utilisateur. Retourne un tuple (booléen, User ou liste).
        Si il y a une erreur, la fonction renvoie False suivi d'une liste d'erreur
        Sinon, elle renvoie True suivi de la donnée enregistrée

        :param login: Login de l'utilisateur
        :type: str
        :param email: Email de l'utilisateur
        :type: str
        :param nom: Nom de l'utilisateur
        :type: str
        :param motdepasse: Mot de passe de l'utilisateur (Minimum 6 caractères)
        :type: str
        """
        # Définition d'une liste d'erreur vide.
        erreurs = []

        # Définition des erreurs (paramètre obligatoire) : Si le champs n'est pas rempli correctement,
        # une erreur s'ajoute à la liste précédemment définie.
        if not login:
            erreurs.append("Le login fourni est vide")
        if not email:
            erreurs.append("L'email fourni est vide")
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not motdepasse or len(motdepasse) < 6:
            erreurs.append("Le mot de passe fourni est vide ou trop court")

        # Définition des erreurs : Vérification qu'un utilisateur n'est pas déjà enregistré avec ce mail ou ce login
        # dans la BD. Sinon, une erreur s'ajoute à la liste précédemment définie.
        uniques = Utilisateur.query.filter(
            db.or_(Utilisateur.ut_mail == email, Utilisateur.ut_login == login)
        ).count()
        if uniques > 0:
            erreurs.append("L'email ou le login sont déjà inscrits dans notre base de données")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur, création d'un nouvel utilisateur :
        utilisateur = Utilisateur(
            ut_nom=nom,
            ut_login=login,
            ut_mail=email,
            ut_mdp=generate_password_hash(motdepasse)
        )

        try:
            # Envoi dans la DB et enregistrement
            db.session.add(utilisateur)
            db.session.commit()

            # Renvoi True et les données de l'utilisateur à la fonction inscription.
            return True, utilisateur

        # Si il y a des erreurs :
        except Exception as erreur:
            # Renvoi False à la fonction inscription et les erreurs rencontrées.
            return False, [str(erreur)]

    def get_id(self):
        """ Retourne l'id de l'objet actuellement utilisé

        :returns: ID de l'utilisateur
        :rtype: int
        """
        return self.ut_id

    def to_jsonapi_dict(self):
        """ It ressembles a little JSON API format but it is not completely compatible

        :return:
        """
        return {
            "type": "people",
            "attributes": {
                "name": self.ut_nom
            }
        }

# login.user_loader est un rappel utilisé pour recharger l'objet utilisateur à partir de l'ID utilisateur stocké
# dans la session. La méthode .get() renvoi un identifiant unique pour identifier l'utilisateur. Elle est utilisée pour
# charger l'utilisateur à partir du rappel user_loader.
@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return Utilisateur.query.get(int(identifiant))
