from flask import url_for
import datetime
from .. app import db
from ..modeles.utilisateurs import Utilisateur
from flask_login import current_user
from typing import List


# Table des contributions :
# L'utilisateur peut contribuer de différentes façon : les lettres, les sources et les transcriptions. A chaque
# contribution, l'ID de l'objet modifié/ajouté/créé, l'ID de l'utilisateur et la date/heure sont ajouté à la DB.
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

    def author_to_json(self):
        """
         Est appelé pour d'obtenir le lien d'autorité des modifications de données en JSON
        """
        return {
            "contributor": self.utilisateur.to_jsonapi_dict(),
            "on": self.contribution_date
        }


# Table de relation entre une lettre et ses publications :
Source = db.Table("Source",
                  db.Column("source_lettre_id", db.Integer, db.ForeignKey('lettre.lettre_id'), primary_key=True),
                  db.Column("source_publication_id", db.Integer, db.ForeignKey('publication.publication_id'),
                            primary_key=True))


# Table des ouvrages dans lesquels sont publiées les lettres :
class Publication(db.Model):
    __tablename__ = "publication"
    publication_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    publication_titre = db.Column(db.Text)
    publication_volume = db.Column(db.Text)
    contributions = db.relationship("Contribution", back_populates="publication")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: id de la publication
        :rtype: int
        """
        return self.publication_id

    @staticmethod
    def ajouter_publication(publication_titre, publication_volume):
        """
        :param publication_titre: titre de l'ouvrage
        :type: str
        :param publication_volume: Volume de l'ouvrage
        :type: str
        :return: Ajout de données dans la base ou refus en cas d'erreurs
        """
        # Définition d'une liste d'erreur vide.
        erreurs = []

        # Définition des erreurs (paramètre obligatoire) : Si il n'y a pas de titre, une erreur s'ajoute à la liste
        # précédemment définie.
        if not publication_titre:
            erreurs.append("Le champ titre est vide")

        # Définition des erreurs : Vérification que le volume n'est pas déjà enregistrée dans la BD. Sinon, une erreur
        # s'ajoute à la liste précédemment définie.
        ajout_unique = Publication.query.filter(
            db.and_(Publication.publication_titre == publication_titre,
                    Publication.publication_volume == publication_volume)).count()
        if ajout_unique > 0:
            erreurs.append("Ce volume est déjà enregistré dans la base de donnée")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur, création d'une nouvelle publication :
        nouvelle_publication = Publication(
            publication_titre=publication_titre,
            publication_volume=publication_volume)

        try:
            # Envoi dans la DB et enregistrement
            db.session.add(nouvelle_publication)
            db.session.commit()

            # Enregistrement de la modification dans la table contribution :
            if nouvelle_publication:
                # Récupération l'id de la transcription que l'on souhaite supprimer.
                publication = Publication.query.order_by(Publication.publication_id.desc()).limit(1).first()
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
                # Envoi dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Renvoi True à la fonction publication_creation :
            return (True, nouvelle_publication)

        # Si il y a des erreurs :
        except Exception as erreur:
            # Annulation de la transaction en cours
            db.session.rollback()
            # Renvoi False à la fonction publication_creation et les erreurs rencontrées.
            return False, [str(erreur)]

    def to_jsonapi_dict(self):
        """
         Permet de récupérer toutes les données d'une publication en JSON
        """
        return {
            "type": "Publication",
            "id": self.publication_id,
            "attributes": {
                "Titre": self.publication_titre,
                "Volume": self.publication_volume,
            },
            "links": {
                "self": url_for("publications", publication_id=self.publication_id, _external=True),
                "json": url_for("api_publication_unique", publication_id=self.publication_id, _external=True)
            },
            "relationships": {
                 "editions": [
                     contributor.author_to_json()
                     for contributor in self.contributions
                 ]
            }
        }


# Table des lettres :
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
        :param lettre_numero: le numéro de la lettre
        :type: str
        :param lettre_redacteur: le rédacteur de la lettre
        :type: str
        :param lettre_lieu: le lieu d'envoi de la lettre
        :type: str
        :param lettre_date: la date d'envoi de la lettre
        :type: str
        :return: Ajout de données dans la base ou refus en cas d'erreurs
        """

        # Définition d'une liste d'erreur vide.
        erreurs = []

        # Définition des erreurs (paramètre obligatoire) : Si le champs n'est pas rempli correctement,
        # une erreur s'ajoute à la liste précédemment définie.
        if not lettre_numero:
            erreurs.append("Le champ numero de lettre est vide, si la lettre n'est pas de éditée, mettre 0")
        if not lettre_redacteur:
            erreurs.append("Le champ auteur est vide")
        if not lettre_lieu:
            erreurs.append("Le champ lieu est vide")
        if not lettre_date or len(lettre_date) < 4:
            erreurs.append("Le champ date d'envoi doit au moins contenir une année")

        # Définition des erreurs : Vérification que la lettre n'est pas déjà enregistrée dans la BD. Sinon, une erreur
        # s'ajoute à la liste précédemment définie.
        ajout_unique = Lettre.query.filter(
                db.and_(Lettre.lettre_numero == lettre_numero,
                        Lettre.lettre_redacteur == lettre_redacteur, Lettre.lettre_lieu == lettre_lieu,
                        Lettre.lettre_date == lettre_date)).count()
        if ajout_unique > 0:
            erreurs.append("Cette lettre est déjà enregistré dans la base de donnée")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur, création d'une nouvelle publication :
        nouvelle_lettre = Lettre(
            lettre_numero=lettre_numero,
            lettre_redacteur=lettre_redacteur,
            lettre_lieu=lettre_lieu,
            lettre_date=lettre_date,
        )

        try:
            # Envoi dans la DB et enregistrement
            db.session.add(nouvelle_lettre)
            db.session.commit()

            # Enregistrement de l'ajout dans la table contribution :
            if nouvelle_lettre:
                # Récupération l'id de la nouvelle lettre.
                lettre = Lettre.query.order_by(Lettre.lettre_id.desc()).limit(1).first()
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
                # Envoi dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Renvoi True à la fonction creation :
            return (True, nouvelle_lettre)

        # Si il y a des erreurs :
        except Exception as erreur:
            # Annulation de la transaction en cours
            db.session.rollback()
            # Renvoi False à la fonction publication_creation et les erreurs rencontrées.
            return False, [str(erreur)]

    @staticmethod
    def sourcer_lettre(publication_id, lettre_id):
        """
        Fonction qui permet d'associer une publication à une lettre
            :param publication_id: identifiant une publication à ajouter à la lettre
            :type: int
            :param lettre_id: identifiant du document auquel ajouter la publication
            :type: int
            :return: Liste d'erreurs si rencontré
        """
        # Définition d'une liste d'erreur vide.
        erreurs = []

        # Récupération de la publication correspondant à l'ID :
        source = Publication.query.filter(Publication.publication_id == publication_id).first()
        # Récupération de la lettre correspondant à l'ID :
        lettre = Lettre.query.filter(Lettre.lettre_id == lettre_id).first()

        # Définition des erreurs (paramètre obligatoire) : Si le champs n'est pas rempli correctement,
        # une erreur s'ajoute à la liste précédemment définie.
        if not publication_id:
            erreurs.append("Il n'y a pas de publication à associer")
        if not lettre_id:
            erreurs.append("Il n'y a pas de lettre à associer")

        # Si les identifiants ne correspondent à rien,
        if source is None or lettre is None:
            # rien ne se passe.
            return

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si la source n'est pas déjà dans la liste de source contenu dans lettre_volume
        if source not in lettre.lettre_volume:
            # Elle est ajoutée
            lettre.lettre_volume.append(source)

        # Envoi dans la DB et enregistrement
        db.session.add(lettre)
        db.session.commit()

        # Enregistrement de la modification dans la table contribution :
        if lettre:
            # Récupération l'id de la lettre.
            lettre_sourcee = Lettre.query.get_or_404(lettre_id)
            # Récupération l'id de la publication.
            source = Publication.query.filter(Publication.publication_id == publication_id).first()
            # Récupération l'id de l'utilisateur courant
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # Préparation des données à l'enregistrement :
            a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre_sourcee, publication=source)
            # Envoi dans la DB et enregistrement
            db.session.add(a_contribue)
            db.session.commit()

    def to_jsonapi_dict(self):
        """
         Permet de récupérer toutes les données d'une lettre en JSON
        """
        return {
            "type": "Lettre",
            "id": self.lettre_id,
            "attributes": {
                "numero": self.lettre_numero,
                "auteur": self.lettre_redacteur,
                "lieu": self.lettre_lieu,
                "date": self.lettre_date,
            },
            "links": {
                "self": url_for("lettres", lettre_id=self.lettre_id, _external=True),
                "json": url_for("api_lettre_unique", lettre_id=self.lettre_id, _external=True)
            },
            "relationships": {
                 "editions": [
                     contributor.author_to_json()
                     for contributor in self.contributions
                 ],
                "source": [
                    publication.to_jsonapi_dict()
                    for publication in self.lettre_volume
                ],
                "transcription": [
                    transcription.to_jsonapi_dict()
                    for transcription in self.transcription_texte
                ]
            }
        }


# Table des transcriptions des lettres :
class Transcription(db.Model):
    __tablename__ = "transcription"
    transcription_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    transcription_texte = db.Column(db.Text, nullable=False)
    transcription_lettre_id = db.Column(db.Integer, db.ForeignKey('lettre.lettre_id'), nullable=False)
    lettre: Lettre = db.relationship("Lettre", back_populates="transcription_texte")
    contributions = db.relationship("Contribution", back_populates="transcription")

    def get_id(self):
        """
        Retourne l'id de l'objet actuellement utilisé
        :return: Id de la transcription
        :rtype: int
        """
        return self.transcription_id

    def to_jsonapi_dict(self):
        """
         Permet de récupérer toutes les données d'une transcription en JSON
        """
        return {
            "type": "Transcription",
            "id": self.transcription_id,
            "attributes": {
                "ID lettre transcrite": self.transcription_lettre_id,
                "Texte": self.transcription_texte,
            },
            "links": {
                "self": url_for("transcriptions", transcription_id=self.transcription_id, _external=True),
                "json": url_for("api_transcription_unique", transcription_id=self.transcription_id, _external=True)
            },
            "relationships": {
                 "editions": [
                     contributor.author_to_json()
                     for contributor in self.contributions
                 ]
            }
        }
