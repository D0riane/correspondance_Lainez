from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .. app import db, login

# On définit la classe utilisateurs :
class Utilisateur(UserMixin, db.Model):
    __tablename__ = "utilisateur"
    ut_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    ut_nom = db.Column(db.Text, nullable=False)
    ut_login = db.Column(db.Text, nullable=False)
    ut_mdp = db.Column(db.Text, nullable=False)
    ut_mail = db.Column(db.Text, nullable=False)

    contributions = db.relationship("Contribution", back_populates="utilisateur")
    transcriptions = db.relationship("Transcrire", back_populates="utilisateur")

    # On définit 2 static méthode pour cette classe : l'identification et la création d'un nouvel utilisateur.
    @staticmethod
    def identification(login, motdepasse):
        """ Identifie un utilisateur. Si cela fonctionne, renvoie les données de l'utilisateurs.

        :param login: Login de l'utilisateur
        :param motdepasse: Mot de passe de l'utilisateur
        :returns: Si réussite, données de l'utilisateur. Sinon None
        :rtype: User or None
        """
        utilisateur = Utilisateur.query.filter(Utilisateur.ut_login == login).first()
        if utilisateur and check_password_hash(utilisateur.ut_mdp, motdepasse):
            return utilisateur
        return None

    @staticmethod
    def nouvel_utilisateur(login, email, nom, motdepasse):
        """ Crée un compte utilisateur-rice. Retourne un tuple (booléen, User ou liste).
        Si il y a une erreur, la fonction renvoie False suivi d'une liste d'erreur
        Sinon, elle renvoie True suivi de la donnée enregistrée

        :param login: Login de l'utilisateur-rice
        :param email: Email de l'utilisateur-rice
        :param nom: Nom de l'utilisateur-rice
        :param motdepasse: Mot de passe de l'utilisateur-rice (Minimum 6 caractères)

        """
        erreurs = []
        if not login:
            erreurs.append("Le login fourni est vide")
        if not email:
            erreurs.append("L'email fourni est vide")
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not motdepasse or len(motdepasse) < 6:
            erreurs.append("Le mot de passe fourni est vide ou trop court")

        # On vérifie que personne n'a utilisé cet email ou ce login
        uniques = Utilisateur.query.filter(
            db.or_(Utilisateur.ut_mail == email, Utilisateur.ut_login == login)
        ).count()
        if uniques > 0:
            erreurs.append("L'email ou le login sont déjà inscrits dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On crée un utilisateur
        utilisateur = Utilisateur(
            ut_nom=nom,
            ut_login=login,
            ut_mail=email,
            ut_mdp=generate_password_hash(motdepasse)
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(utilisateur)
            # On envoie le paquet
            db.session.commit()

            # On renvoie l'utilisateur
            return True, utilisateur
        except Exception as erreur:
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


@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return Utilisateur.query.get(int(identifiant))
