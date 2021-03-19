from flask import url_for
import datetime
from .. app import db
from ..modeles.utilisateurs import Utilisateur
from flask_login import current_user
from typing import List


# table des contributions : l'utilisateur peut contribuer de différentes façon :
# les lettres, les sources et les transcriptions.
class Contribution(db.Model):
    __tablename__ = "contribution"
    contribution_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    contribution_lettre_id = db.Column(db.Integer, db.ForeignKey('lettre.lettre_id'))
    contribution_publication_id = db.Column(db.Integer, db.ForeignKey('publication.publication_id'))
    contribution_transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.transcription_id'))
    contribution_ut_id = db.Column(db.Integer, db.ForeignKey('utilisateur.ut_id'))
    contribution_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    utilisateur = db.relationship("Utilisateur", back_populates="contributions")
    lettre = db.relationship("Lettre", back_populates="contributions")
    publication = db.relationship("Publication", back_populates="contributions")
    transcription = db.relationship("Transcription", back_populates="contributions")


# Table de relation entre une lettre et sa publication :
Source = db.Table("Source",
                  db.Column("source_lettre_id", db.Integer, db.ForeignKey('lettre.lettre_id'), primary_key=True),
                  db.Column("source_publication_id", db.Integer, db.ForeignKey('publication.publication_id'),
                            primary_key=True))








class Publication(db.Model):
    __tablename__ = "publication"
    publication_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    publication_titre = db.Column(db.Text)
    publication_volume = db.Column(db.Text)

    contributions = db.relationship("Contribution", back_populates="publication")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: Id de la lettre
        :rtype: int
        """
        return self.publication_id

    @staticmethod
    def ajouter_publication(publication_titre, publication_volume):
        """
        :param publication_titre:
        :param publication_volume:

        :return:Ajout de données dans la base ou refus en cas d'erreurs
        """
        # Définition des paramètres obligatoires : s'ils manquent, cela crée une liste d'erreurs
        erreurs = []

        if not publication_titre:
            erreurs.append("Le champ titre est vide")

        # On vérifie que le volume n'est pas déjà enregistrée dans la BD
        ajout_unique = Publication.query.filter(
            db.and_(Publication.publication_titre == publication_titre,
                    Publication.publication_volume == publication_volume)).count()
        if ajout_unique > 0:
            erreurs.append("Ce volume est déjà enregistré dans la base de donnée")

        # On vérifie qu'il n'y a pas d'erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On créé une nouvelle lettre
        nouvelle_publication = Publication(
            publication_titre=publication_titre,
            publication_volume=publication_volume)

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(nouvelle_publication)
            # On envoie les données
            db.session.commit()

            if nouvelle_publication:
                # On récupère l'id de la dernière lettre référencée dans la base
                publication = Publication.query.order_by(Publication.publication_id.desc()).limit(1).first()
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            return (True, nouvelle_publication)

        except Exception as erreur:
            # On annule les requêtes de la transaction en cours en cas d'erreurs
            db.session.rollback()
            return False, [str(erreur)]


# table lettre envoyée
class Lettre(db.Model):
    __tablename__ = "lettre"
    lettre_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    lettre_date = db.Column(db.Text, nullable=False)
    lettre_numero = db.Column(db.Text)
    lettre_redacteur = db.Column(db.Text)
    lettre_lieu = db.Column(db.Text)

    lettre_volume = db.relationship("Publication", secondary=Source, backref=db.backref("Lettre", lazy='dynamic'))

    transcription_texte: List["Transcription"] = db.relationship("Transcription", back_populates="lettre",
                                                                 cascade="all,delete")
    contributions = db.relationship("Contribution", back_populates="lettre")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: Id de la lettre
        :rtype: int
        """
        return self.lettre_id

    @staticmethod
    def ajouter_lettre(lettre_numero, lettre_redacteur, lettre_lieu, lettre_date):
        """
        :param lettre_numero:
        :param lettre_redacteur:
        :param lettre_lieu:
        :param lettre_date:
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

        # On vérifie que la lettre n'est pas déjà enregistrée dans la BD
        ajout_unique = Lettre.query.filter(
                db.and_(Lettre.lettre_numero == lettre_numero,
                        Lettre.lettre_redacteur == lettre_redacteur, Lettre.lettre_lieu == lettre_lieu,
                        Lettre.lettre_date == lettre_date)).count()
        if ajout_unique > 0:
            erreurs.append("Cette lettre est déjà enregistré dans la base de donnée")

        # On vérifie qu'il n'y a pas d'erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On créé une nouvelle lettre
        nouvelle_lettre = Lettre(
            lettre_numero=lettre_numero,
            lettre_redacteur=lettre_redacteur,
            lettre_lieu=lettre_lieu,
            lettre_date=lettre_date,
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

    @staticmethod
    def sourcer_lettre(publication_id, lettre_id):
        '''
        Fonction qui permet d'associer une publication à une lettre
            :param publication_id: identifiant une publication à ajouter à la lettre (int)
            :param lettre_id: identifiant du document auquel ajouter la publication (int)
            :return: renvoie une liste d'erreurs s'il y en a
        '''

        erreurs = []
        if not publication_id:
            erreurs.append("Il n'y a pas de publication à associer")
        if not lettre_id:
            erreurs.append("Il n'y a pas de lettre à associer")

        source = Publication.query.filter(Publication.publication_id == publication_id).first()
        # je récupère la publication correspondant à l'id
        lettre = Lettre.query.filter(Lettre.lettre_id == lettre_id).first()
        # idem pour la lettre

        if source is None or lettre is None:
            # si les identifiants ne correspondent à rien, rien ne se passe.
            return

        if source not in lettre.lettre_volume:
            # si la source n'est pas déjà dans la liste de source contenu dans lettre_volume
            lettre.lettre_volume.append(source)
            # je l'ajoute à cette liste

        db.session.add(lettre)
        db.session.commit()

        if lettre:
            # On récupère l'id de la lettre référencée dans la base
            lettre_sourcee = Lettre.query.get_or_404(lettre_id)
            source = Publication.query.filter(Publication.publication_id == publication_id).first()
            # On récupère l'id de l'utilisateur courant authentifié
            utilisateur = Utilisateur.query.get(current_user.ut_id)

            # On crée un lien d'autorité
            a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre_sourcee, publication=source)
            # On envoie dans la base et on enregistre
            db.session.add(a_contribue)
            db.session.commit()

        return erreurs


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

    contributions = db.relationship("Contribution", back_populates="transcription")
