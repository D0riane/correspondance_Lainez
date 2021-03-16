from flask import url_for
import datetime
from .. app import db
from ..modeles.utilisateurs import Utilisateur
from flask_login import current_user
from typing import List


# table des contributions
class Contribution(db.Model):
    __tablename__ = "contribution"
    contribution_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    contribution_lettre_id = db.Column(db.Integer, db.ForeignKey('lettre.lettre_id'))
    contribution_ut_id = db.Column(db.Integer, db.ForeignKey('utilisateur.ut_id'))
    contribution_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    utilisateur = db.relationship("Utilisateur", back_populates="contributions")
    lettre = db.relationship("Lettre", back_populates="contributions")


class Transcrire(db.Model):
    __tablename__ = "transcrire"
    transcrire_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    transcrire_transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.transcription_id'))
    transcrire_ut_id = db.Column(db.Integer, db.ForeignKey('utilisateur.ut_id'))
    transcrire_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    utilisateur = db.relationship("Utilisateur", back_populates="transcriptions")
    transcription = db.relationship("Transcription", back_populates="transcriptions")


class Publication(db.Model):
    __tablename__ = "publication"
    publication_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    publication_titre = db.Column(db.Text)
    publication_volume = db.Column(db.Text)


# table lettre envoyée
class Lettre(db.Model):
    __tablename__ = "lettre"
    lettre_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    lettre_date = db.Column(db.Text, nullable=False)
    lettre_volume = db.Column(db.Integer, db.ForeignKey('publication.publication_id'), nullable=False)
    lettre_numero = db.Column(db.Text)
    lettre_redacteur = db.Column(db.Text)
    lettre_lieu = db.Column(db.Text)

    transcription_texte: List["Transcription"] = db.relationship("Transcription", back_populates="lettre",
                                                                 cascade="all,delete")
    contributions = db.relationship("Contribution", back_populates="lettre")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: Id de la lettre
        :rtype: int
        """
        return self.id_lettre

    @staticmethod
    def ajouter_lettre(lettre_numero, lettre_redacteur, lettre_lieu, lettre_date, lettre_volume):
        """
        :param lettre_numero:
        :param lettre_redacteur:
        :param lettre_lieu:
        :param lettre_date:
        :param lettre_volume:
        :return:Ajout de données dans la base ou refus en cas d'erreurs
        """
        # Définition des paramètres obligatoires : s'ils manquent, cela crée une liste d'erreurs
        erreurs = []
        if not lettre_numero:
            erreurs.append("Le champ numero de lettre est vide, si la lettre n'est pas de éditée, mettre 0")
        if not lettre_redacteur:
            erreurs.append("Le champ auteur est vide")
        if not lettre_lieu:
            erreurs.append("Le champ lieu est vide")
        if not lettre_date or len(lettre_date) < 4:
            erreurs.append("Le champ date d'envoi doit au moins contenir une année")
        if lettre_volume != "1" and lettre_volume != "2" and lettre_volume != "3" and lettre_volume != "4" \
                and lettre_volume != "5" and lettre_volume != "4" and lettre_volume != "7" and lettre_volume != "8" \
                and lettre_volume != "9" and lettre_volume != "10" and lettre_volume != "11" and lettre_volume != "12":
            erreurs.append("Le volume doit faire partie de la liste de volume pré enregistré")

        # On vérifie que la lettre n'est pas déjà enregistrée dans la BD
        ajout_unique = Lettre.query.filter(
                db.and_(Lettre.lettre_numero == lettre_numero, Lettre.lettre_volume == lettre_volume,
                        Lettre.lettre_redacteur == lettre_redacteur, Lettre.lettre_lieu == lettre_lieu,
                        Lettre.lettre_date == lettre_date)).count()
        if ajout_unique > 0:
            erreurs.append("Cette lettre est déjà enregistré dans la base de donnée")

        # On vérifie qu'il n'y a pas d'erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On créé une nouvelle lettre
        nouvelle_lettre = Lettre(
            lettre_volume=lettre_volume,
            lettre_numero=lettre_numero,
            lettre_redacteur=lettre_redacteur,
            lettre_lieu=lettre_lieu,
            lettre_date=lettre_date
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(nouvelle_lettre)
            # On envoie les données
            db.session.commit()

            if nouvelle_lettre:
                # On récupère l'id de la dernière lettre référencée dans la base
                lettre = Lettre.query.order_by(Lettre.lettre_id.desc()).limit(1).first()
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            return (True, nouvelle_lettre)

        except Exception as erreur:
            # On annule les requêtes de la transaction en cours en cas d'erreurs
            db.session.rollback()
            return False, [str(erreur)]

    def to_jsonapi_dict(self):
        """
         It ressembles a little JSON API format but it is not completely compatible

        :return:
        """
        return {
            "type": "lettre",
            "id": self.lettre_id,
            "attributes": {
                "numero": self.lettre_numero,
                "auteur": self.lettre_redacteur,
                "lieu": self.lettre_lieu,
                "date": self.lettre_date,
                "source": self.lettre_volume,
            },
            "links": {
                "self": url_for("lettres", lettre_id=self.lettre_id, _external=True),
                "json": url_for("api_lettre_single", lettre_id=self.lettre_id, _external=True)
            }
        }


class Transcription(db.Model):
    __tablename__ = "transcription"
    transcription_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    transcription_texte = db.Column(db.Text, nullable=False)
    transcription_lettre_id = db.Column(db.Integer, db.ForeignKey('lettre.lettre_id'), nullable=False)
    lettre: Lettre = db.relationship("Lettre", back_populates="transcription_texte")
    transcriptions = db.relationship("Transcrire", back_populates="transcription")
