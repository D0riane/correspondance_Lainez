from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_

from ..app import app, login, db
from ..modeles.donnees import Lettre, Contribution, Publication, Transcription
from ..modeles.utilisateurs import Utilisateur
from ..constantes import LETTRES_PAR_PAGE

from flask_login import login_user, current_user, logout_user


# Route pour l'accueil : nous y affichons les 10 dernières lettres ajoutées.
@app.route('/')
def accueil():
    """"
    Route affichant la page accueil
    """

    # La variable toutes_les_lettres récupèrent toutes les lettres.
    toutes_les_lettres = Lettre.query.all()

    # La variable dernieres_lettres récupèrent les 10 dernières lettres ajoutées.
    # On les récupère grâce à l'ordre décroissant de la valeur de lettre_id,
    # un identifiant automatiquement assigné lors de leur création.
    dernieres_lettres = Lettre.query.order_by(Lettre.lettre_id.desc()).limit(10).all()

    return render_template('pages/accueil.html', nom="Correspondance jésuite", dernieres_lettres=dernieres_lettres,
                           toutes_les_lettres=toutes_les_lettres)


# Route concernant les lettres :

# Route pour voir l'ensemble des lettres. Elles sont présentées sous la forme de tableau avec une pagination.
@app.route('/lettres', methods=["POST", "GET"])
def lettres():
    """"
    Route affichant 10 lettres par pages grâce à la méthode paginate.
    """

    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    lettres = Lettre.query.paginate(page=page, per_page=LETTRES_PAR_PAGE)

    return render_template('pages/lettres.html', nom="Correspondance jésuite",
                           lettres=lettres)


# Route vers chacune des lettres grâce à leur id.
@app.route("/lettres/<lettre_id>", methods=["POST", "GET"])
def unique_lettre(lettre_id):
    """
    Route permettant l'affichage des données d'une seule lettre
    :param lettre_id: Identifiant de la lettre
    :type lettre_id: str
    :return: template HTML (lettre.html)
    """

    unique_lettre = Lettre.query.get(lettre_id)

    publication = Publication.query.filter(db.and_(Publication.publication_id == Lettre.lettre_volume,
                                                   Lettre.lettre_id == lettre_id)).first()

    transcription = Transcription.query.filter(db.and_(Transcription.transcription_lettre_id == Lettre.lettre_id,
                                                       Lettre.lettre_id == lettre_id)).first()

    return render_template("pages/lettre.html", nom="Correspondance jésuite",
                           lettre=unique_lettre, publication=publication, transcription=transcription)


# Route pour voir toutes des lettres sous la forme de tableau sans pagination.
@app.route('/index', methods=["POST", "GET"])
def index():
    """"
        Route pour une page affichant toutes les lettres (sans objet paginate) pour permettre de récupérer
        toutes les données en JSON.
    """

    lettres = Lettre.query.all()

    return render_template('pages/index.html', nom="Correspondance jésuite", lettres=lettres)


# Route vers la liste des ouvrages utilisés pour la constitution de la DB.
@app.route('/publications', methods=["POST", "GET"])
def publications():
    """
        Route permettant l'affichage des ouvrages
    """
    publications = Publication.query.all()
    return render_template('pages/publications.html', nom="Correspondance jésuite", publications=publications)


# Route permettant la recherche dans les lettres.
@app.route("/recherche", methods=["POST", "GET"])
def recherche():
    """
        Route permettant la recherche dans les lettres
    """
    # On utilise .get() pour récupérer le mot-clé (keyword) envoyé par l'utilisateur.
    motclef = request.args.get("keyword", None)

    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # On crée une liste vide de résultat (qui restera vide par défaut si on n'a pas de mot clé)
    resultats = []

    # On fait de même pour le titre de la page
    titre = "Recherche"

    if motclef:
        resultats = Lettre.query.filter(or_(Lettre.lettre_date.like("%{}%".format(motclef)),
                                            Lettre.lettre_redacteur.like("%{}%".format(motclef)),
                                            Lettre.lettre_lieu.like("%{}%".format(motclef)),
                                            Lettre.lettre_volume.like("%{}%".format(motclef))
                                            )).paginate(page=page, per_page=LETTRES_PAR_PAGE)

        titre = "Résultat pour la recherche `" + motclef + "`"
    return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)


# Route concernant les transcriptions

@app.route('/transcriptions', methods=["POST", "GET"])
def transcriptions():
    """"
    Route affichant 10 transcriptions par pages grâce à la méthode paginate.
    """

    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    transcriptions = Transcription.query.paginate(page=page, per_page=LETTRES_PAR_PAGE)

    return render_template('pages/transcriptions.html', nom="Correspondance jésuite",
                           transcriptions=transcriptions)


# Route pour l'authentification des utilisateurs

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    """ Route gérant les inscriptions
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        statut, donnees = Utilisateur.nouvel_utilisateur(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Vous êtes identifié-e ! Bienvenue parmi nous ! ", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")

    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = Utilisateur.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Vous êtes connecté-e", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")


login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")


# Routes pour la création, édition et suppression de lettres dans la base de données :

@app.route('/creation', methods=["POST", "GET"])
def creation():
    """Route permettant la création de lettre
    :returns: création de la page
    :rtype: page html du formulaire souhaité
    """

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    if request.method == "POST":
        status, donnees_lettre = Lettre.ajouter_lettre(
            lettre_numero=request.form.get("lettre_numero", None),
            lettre_redacteur=request.form.get("lettre_redacteur", None),
            lettre_lieu=request.form.get("lettre_lieu", None),
            lettre_date=request.form.get("lettre_date", None),
        )

        if status is True:
            flash("La lettre a été ajoutée ! ", "success")
            return redirect(url_for("lettres"))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + " ; ".join(donnees_lettre), "danger")

    return render_template("pages/lettre_creation.html")


@app.route('/lettres/<int:lettre_id>/edition', methods=["POST", "GET"])
def edition(lettre_id):
    """Route permettant l'édition de lettre"""

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    erreurs = []
    lettre_modifiee = Lettre.query.get_or_404(lettre_id)

    if request.method == "POST":

        lettre_volume = request.form.get("lettre_volume", None)
        lettre_numero = request.form.get("lettre_numero", None)
        lettre_redacteur = request.form.get("lettre_redacteur", None)
        lettre_lieu = request.form.get("lettre_lieu", None)
        lettre_date = request.form.get("lettre_date", None)

        if not lettre_numero:
            erreurs.append("Le champ numero lettre est vide.")
        if not lettre_redacteur:
            erreurs.append("Le champ auteur est vide.")
        if not lettre_lieu:
            erreurs.append("Le champ lieu d'envoi est vide.")
        if not lettre_date:
            erreurs.append("Le champ date d'envoi est vide.")
        if not lettre_volume:
            erreurs.append("Le champ référence volume est vide.")

        if len(erreurs) > 0:
            return False, erreurs

        if not erreurs:
            lettre_modifiee.lettre_numero = lettre_numero
            lettre_modifiee.lettre_volume = lettre_volume
            lettre_modifiee.lettre_redacteur = lettre_redacteur
            lettre_modifiee.lettre_lieu = lettre_lieu
            lettre_modifiee.lettre_date = lettre_date

            db.session.add(lettre_modifiee)
            db.session.commit()

            if lettre_modifiee:
                # On récupère l'id de la lettre référencée dans la base
                lettre = Lettre.query.get_or_404(lettre_id)
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            flash(
                "La lettre modifiée a pour numéro {}, pour volume : {}, pour rédacteur {}, pour lieu {},"
                " pour date {}".format(lettre_modifiee.lettre_numero, lettre_modifiee.lettre_volume,
                                       lettre_modifiee.lettre_redacteur, lettre_modifiee.lettre_lieu,
                                       lettre_modifiee.lettre_date), "success")

            return redirect(url_for("lettres"))

    return render_template("pages/lettre_edition.html", nom="Correspondance jésuite", lettre_modifiee=lettre_modifiee)


@app.route("/lettres/<int:lettre_id>/suppression", methods=["POST", "GET"])
def suppression_lettre(lettre_id):
    """Route permettant la suppression de lettre"""
    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    lettre_a_supprimer = Lettre.query.get_or_404(lettre_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        if lettre_a_supprimer:
            # On récupère l'id de la dernière lettre référencée dans la base
            lettre = Lettre.query.get_or_404(lettre_id)
            # On récupère l'id de l'utilisateur courant authentifié
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # On crée un lien d'autorité
            a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
            # On envoie dans la base et on enregistre
            db.session.add(a_contribue)
            db.session.commit()

        db.session.delete(lettre_a_supprimer)
        db.session.commit()

        flash("La lettre a été supprimée", "success")

        return redirect(url_for('lettres'))
    return render_template("pages/lettre_suppression.html", lettre=lettre_a_supprimer)


# Routes pour la création, édition et suppression de transcription de lettre :

@app.route("/lettres/<int:lettre_id>/ajouter_transcription", methods=["POST", "GET"])
def nouvelle_transcription(lettre_id):

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    erreurs = []
    lettre_a_transcrire = Lettre.query.get_or_404(lettre_id)

    if request.method == "POST":
        lettre_transcrite = request.form.get("transcription_lettre", None)

        if not lettre_transcrite:
            erreurs.append("Il n'y a pas de transcription")

        if len(erreurs) > 0:
            return False, erreurs

        if not erreurs:
            lettre_a_transcrire.transcription_texte.append(Transcription(transcription_texte=lettre_transcrite))
            db.session.add(lettre_a_transcrire)
            db.session.commit()

            if lettre_a_transcrire:
                # On récupère l'id de la dernière lettre référencée dans la base
                transcription = Transcription.query.order_by(Transcription.transcription_id.desc()).limit(1).first()
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            flash(
                "Votre transcription a été ajouté ! Merci de votre contribution !", "success")

            return redirect(url_for("lettres"))

    return render_template("pages/transcription_creation.html", nom="Correspondance jésuite",
                           lettre_a_transcrire=lettre_a_transcrire)


@app.route('/transcription/<int:transcription_id>')
def afficher_transcription(transcription_id):
    """Route permettant d'afficher les transcriptions"""

    transcription = Transcription.query.get(transcription_id)

    transcrire = Contribution.query.filter(db.and_(
        Contribution.contribution_transcription_id == Transcription.transcription_id,
        Transcription.transcription_id == transcription_id)).first()

    utilisateur = Utilisateur.query.filter(db.and_(
        Utilisateur.ut_id == Contribution.contribution_ut_id,
        Transcription.transcription_id == transcription_id)).first()

    return render_template("pages/transcription.html", nom="Correspondance jésuite",
                           transcription=transcription, transcrire=transcrire, utilisateur=utilisateur)


@app.route('/transcription/<int:transcription_id>/modifier_transcription', methods=["POST", "GET"])
def modification_transcription(transcription_id):
    """Route permettant l'édition de transcription"""

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    erreurs = []
    transcription_a_modifier = Transcription.query.get_or_404(transcription_id)

    if request.method == "POST":
        transcription_modifiee = request.form.get("transcription_lettre_modifiee", None)

        if not transcription_modifiee:
            erreurs.append("Vous n'avez pas modifié la transcription.")

        if len(erreurs) > 0:
            return False, erreurs

        if not erreurs:
            transcription_a_modifier.transcription_texte = transcription_modifiee
            db.session.add(transcription_a_modifier)
            db.session.commit()

            if transcription_a_modifier:
                # On récupère l'id de la lettre référencée dans la base
                transcription = Transcription.query.get_or_404(transcription_id)
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            flash(
                "Votre transcription : {}".format(
                    transcription_a_modifier.transcription_texte
                ), "success")

            return redirect(url_for("lettres"))

    return render_template("pages/transcription_edition.html", nom="Correspondance jésuite",
                           transcription_a_modifier=transcription_a_modifier)


@app.route("/transcription/<int:transcription_id>/supprimer_transcription", methods=["POST", "GET"])
def suppression_transcription(transcription_id):
    """Route permettant la suppression de lettre"""
    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    transcription_a_supprimer = Transcription.query.get_or_404(transcription_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        if transcription_a_supprimer:
            # On récupère l'id de la dernière lettre référencée dans la base
            transcription = Transcription.query.get_or_404(transcription_id)
            # On récupère l'id de l'utilisateur courant authentifié
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # On crée un lien d'autorité
            a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
            # On envoie dans la base et on enregistre
            db.session.add(a_contribue)
            db.session.commit()

        db.session.delete(transcription_a_supprimer)
        db.session.commit()

        flash("La transcription a été supprimée", "success")

        return redirect(url_for('lettres'))
    return render_template("pages/transcription_suppression.html", transcription=transcription_a_supprimer)


@app.route('/ajouter_publication', methods=["POST", "GET"])
def publication_creation():
    """Route permettant la création de lettre
    :returns: création de la page
    :rtype: page html du formulaire souhaité
    """

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    if request.method == "POST":
        status, donnees_publication = Publication.ajouter_publication(
            publication_titre=request.form.get("publication_titre", None),
            publication_volume=request.form.get("publication_volume", None),
        )

        if status is True:
            flash("Le volume a été ajoutée ! ", "success")
            return redirect(url_for("publications"))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + " ; ".join(donnees_publication), "danger")

    return render_template("pages/publication_creation.html", errors="errors")


@app.route('/publications/<int:publication_id>/edition', methods=["POST", "GET"])
def edition_publication(publication_id):
    """Route permettant l'édition de lettre"""

    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    erreurs = []
    publication_modifiee = Publication.query.get_or_404(publication_id)

    if request.method == "POST":

        publication_titre = request.form.get("publication_titre", None)
        publication_volume = request.form.get("publication_volume", None)

        if not publication_titre:
            erreurs.append("Le champ numero lettre est vide.")

        if len(erreurs) > 0:
            return False, erreurs

        if not erreurs:
            publication_modifiee.publication_titre = publication_titre
            publication_modifiee.lettre_volume = publication_volume

            db.session.add(publication_modifiee)
            db.session.commit()

            if publication_modifiee:
                # On récupère l'id de la lettre référencée dans la base
                publication = Publication.query.get_or_404(publication_id)
                # On récupère l'id de l'utilisateur courant authentifié
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # On crée un lien d'autorité
                a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
                # On envoie dans la base et on enregistre
                db.session.add(a_contribue)
                db.session.commit()

            flash(
                "Vous avez modifié les données de cet ouvrage. Le titre est maintenant : {} et le tome : {}".format(
                    publication_modifiee.publication_titre, publication_modifiee.publication_volume
                                       ), "success")

            return redirect(url_for("publications"))

    return render_template("pages/publication_edition.html", nom="Correspondance jésuite",
                           publication_modifiee=publication_modifiee)


@app.route("/publications/<int:publication_id>/suppression", methods=["POST", "GET"])
def suppression_publication(publication_id):
    """Route permettant la suppression de lettre"""
    if current_user.is_authenticated is False:
        return render_template("pages/acces_refuse.html")

    source_a_supprimer = Publication.query.get_or_404(publication_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        if source_a_supprimer:
            # On récupère l'id de la dernière lettre référencée dans la base
            publication = Publication.query.get_or_404(publication_id)
            # On récupère l'id de l'utilisateur courant authentifié
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # On crée un lien d'autorité
            a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
            # On envoie dans la base et on enregistre
            db.session.add(a_contribue)
            db.session.commit()

        db.session.delete(source_a_supprimer)
        db.session.commit()

        flash("Cette source a été supprimée", "success")

        return redirect(url_for('publications'))
    return render_template("pages/publication_suppression.html", publication=source_a_supprimer)
