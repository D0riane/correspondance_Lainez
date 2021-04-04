# Import des modules Flask nécessaire au fonctionnement de l'application
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from flask_login import login_user, current_user, logout_user, login_required

# Import de l'application
from ..app import app, login, db

# Import des classes nécessaires contenues dans le module modeles :
from ..modeles.donnees import Lettre, Contribution, Publication, Transcription
from ..modeles.utilisateurs import Utilisateur

# Import des constantes
from ..constantes import RESULTATS_PAR_PAGE


# Route pour l'accueil : nous y affichons les 5 dernières lettres ajoutées et les 5 dernières transcriptions ajoutées.
@app.route('/')
def accueil():
    """"
    Route affichant la page accueil
    """
    # La variable toutes_les_lettres récupèrent toutes les lettres de la DB.
    toutes_les_lettres = Lettre.query.all()
    # La variable dernieres_lettres récupèrent les 5 dernières lettres ajoutées.
    # On les récupère grâce à l'ordre décroissant de la valeur de lettre_id,
    # un identifiant automatiquement assigné lors de leur création.
    dernieres_lettres = Lettre.query.order_by(Lettre.lettre_id.desc()).limit(5).all()

    # Même procédé pour les transcriptions :
    toutes_les_transcriptions = Transcription.query.all()
    dernieres_transcriptions = Transcription.query.order_by(Transcription.transcription_id.desc()).limit(5).all()

    return render_template('pages/accueil.html', nom="Correspondance jésuite", dernieres_lettres=dernieres_lettres,
                           toutes_les_lettres=toutes_les_lettres, dernieres_transcriptions=dernieres_transcriptions,
                           toutes_les_transcriptions=toutes_les_transcriptions)


@app.route('/projet')
def projet():
    """"
    Route affichant la présentation du projet
    """
    return render_template('pages/projet.html', nom="Correspondance jésuite")


# ROUTE POUR L'AFFICHAGE DES LETTRES

# Route pour afficher l'ensemble des lettres, présentées sous la forme de tableau avec une pagination.
@app.route('/lettres', methods=["POST", "GET"])
def lettres():
    """"
    Route affichant 10 lettres par pages grâce à la méthode paginate.
    :return: template HTML (lettres.html)
    """
    # Utilisation de la méthode paginate pour la pagination :
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # Définition des deux deux paramètres de la méthode paginate :
    # - page = correspondant au numéro de page.
    # - per_page : correspondant au nombre de résultat maximal par page.
    # Sa valeur ici est la variable définit dans le fichier constantes.py.
    lettres = Lettre.query.paginate(page=page, per_page=RESULTATS_PAR_PAGE)
    # Définition de la variable publications permettant l'affichage des données de la classe Publication
    # appelées dans le template.
    publications = Publication.query.all()

    return render_template('pages/lettres.html', nom="Correspondance jésuite",
                           lettres=lettres, publications=publications)


# Route vers chacune des lettres grâce à leur id.
@app.route("/lettres/<int:lettre_id>", methods=["POST", "GET"])
def unique_lettre(lettre_id):
    """
    Route permettant l'affichage des données d'une seule lettre
    :param lettre_id: Identifiant de la lettre
    :type lettre_id: int
    :return: template HTML (lettre.html)
    """
    # Récupération de la lettre grâce à lettre_id en utilisant .get()
    unique_lettre = Lettre.query.get(lettre_id)

    # Jointure pour afficher les données de la table publication qui concernent cette lettre.
    publication = Publication.query.filter(db.and_(Publication.publication_id == Lettre.lettre_volume,
                                                   Lettre.lettre_id == lettre_id)).first()

    # Jointure pour afficher les données de la table transcription qui concernent cette lettre.
    transcription = Transcription.query.filter(db.and_(Transcription.transcription_lettre_id == Lettre.lettre_id,
                                                       Lettre.lettre_id == lettre_id)).first()

    return render_template("pages/lettre.html", nom="Correspondance jésuite",
                           lettre=unique_lettre, publication=publication, transcription=transcription)


# Route permettant la recherche dans les lettres.
@app.route("/recherche", methods=["POST", "GET"])
def recherche():
    """
        Route permettant la recherche dans les lettres
        :return: template HTML (recherche.html)
    """
    # Utilisation de .get() pour récupérer le mot-clé (keyword) envoyé par l'utilisateur.
    motclef = request.args.get("keyword", None)

    # Utilisation de la méthode paginate pour la pagination :
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # Création d'une liste vide de résultat. Cette liste restera vide si il n'y a pas de mot clé.
    resultats = []
    # Création d'un titre qui s'affichera si il n'y a pas de mot clé.
    titre = "Recherche"

    # Si il y a un mot clé, les variables résultats et titre changent.
    # Le résultat de la recherche est obtenu grâce à la comparaison avec .like() du mot clé aux données de renseignées
    # dans la table lettre : date, rédacteur, lieu, volume. Pour volume, on utilise .any afin de requêter aussi dans
    # la table Publication.
    if motclef:
        resultats = Lettre.query.filter(or_(Lettre.lettre_numero.like("%{}%".format(motclef)),
                                            Lettre.lettre_date.like("%{}%".format(motclef)),
                                            Lettre.lettre_redacteur.like("%{}%".format(motclef)),
                                            Lettre.lettre_lieu.like("%{}%".format(motclef)),
                                            Lettre.lettre_volume.any(Publication.publication_titre.like("%{}%".format(
                                                motclef))))).paginate(page=page, per_page=RESULTATS_PAR_PAGE)

        titre = "Résultat(s) de votre recherche pour ' " + motclef + " ' "
    return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)


# ROUTE POUR L'AFFICHAGE DES TRANSCRIPTIONS

# # Route pour afficher l'ensemble des transcriptions, présentées sous la forme de tableau avec une pagination.
@app.route('/transcriptions', methods=["POST", "GET"])
def transcriptions():
    """"
    Route affichant 10 transcriptions par pages grâce à la méthode paginate.
    :return: template HTML (transcriptions.html)
    """

    # Utilisation de la méthode paginate pour la pagination :
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # Définition des deux deux paramètres de la méthode paginate :
    # - page = correspondant au numéro de page.
    # - per_page : correspondant au nombre de résultat maximal par page. Sa valeur ici est la variable définit
    # dans le fichier constantes.py.
    transcriptions = Transcription.query.paginate(page=page, per_page=RESULTATS_PAR_PAGE)

    return render_template('pages/transcriptions.html', nom="Correspondance jésuite",
                           transcriptions=transcriptions)


# Route vers chacune des transcription grâce à leur id.
@app.route('/transcriptions/<int:transcription_id>')
def afficher_transcription(transcription_id):
    """Route permettant d'afficher les transcriptions
    :param transcription_id: Identifiant de la transcription
    :type transcription_id: int
    :return: template HTML (transcription.html)
    """
    # Récupération de la transcription grâce à son identifiant (transcription_id) en utilisant .get()
    transcription = Transcription.query.get(transcription_id)

    # Jointure pour afficher les données de la table contribution qui concernent cette transcription :
    # la dernière modification de transcription.
    transcrire = Contribution.query.filter(db.and_(
        Contribution.contribution_transcription_id == Transcription.transcription_id,
        Transcription.transcription_id == transcription_id)).first()

    # Jointure pour afficher les données de la table utilisateur qui concernent cette transcription :
    # l'auteur de la transcription.
    utilisateur = Utilisateur.query.filter(db.and_(
        Utilisateur.ut_id == Contribution.contribution_ut_id,
        Transcription.transcription_id == transcription_id)).first()

    return render_template("pages/transcription.html", nom="Correspondance jésuite",
                           transcription=transcription, transcrire=transcrire, utilisateur=utilisateur)


# ROUTE POUR L'AFFICHAGE DES PUBLICATIONS

# Route vers la liste des ouvrages utilisés pour la constitution de la DB.
@app.route('/publications', methods=["POST", "GET"])
def publications():
    """
        Route permettant l'affichage des ouvrages
        :return: template HTML (publications.html)
    """
    # Récupération de toutes les publications.
    publications = Publication.query.all()

    return render_template('pages/publications.html', nom="Correspondance jésuite", publications=publications)


# Route pour consulter la liste des lettres publiées dans chaque ouvrage :
@app.route('/publications/<int:publication_id>', methods=["POST", "GET"])
def unique_publication(publication_id):
    """
    Route permettant l'affichage des données d'un seul ouvrage
    :param publication_id: Identifiant de la lettre
    :type publication_id: int
    :return: template HTML (publication.html)
    """
    # Récupération de l'ouvrage grâce à publication_id en utilisant .get()
    unique_publication = Publication.query.get(publication_id)

    # Jointure pour afficher les lettres les données de la table lettre qui concernent les lettres publiée dans cet
    # ouvrage.
    lettres = Lettre.query.join(Lettre.lettre_volume).filter(Publication.publication_id == publication_id).all()

    return render_template('pages/publication.html', nom="Correspondance jésuite", publication=unique_publication,
                           lettres=lettres)


# ROUTE POUR L'AUTHENTICATION DES UTILISATEURS :

# Route pour l'inscription d'un nouvel utilisateur.
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    """ Route gérant les inscriptions
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        # Appel de la static method nouvel_utilisateur définie dans la classe Utilisateur.
        # Récupération des données entrées par l'utilisateur dans le formulaire.
        statut, donnees = Utilisateur.nouvel_utilisateur(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        # Si la static method renvoi True, un message informe l'utilisateur qu'il est à présent
        # enregistré comme utilisateur et il est redirigé vers l'accueil.
        if statut is True:
            flash("Vous êtes identifié-e ! Bienvenue parmi nous ! ", "success")
            return redirect("/")
        # Si la static method ne renvoi pas True, un message informe l'utilisateur des erreurs rencontrées.
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


# Route pour la connexion d'un utilisateur.
@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """
    Route permettant de se connecter.
    """
    # Si l'utilisateur courant est connecté, on l'en informe et on le redirige vers la page d'accueil.
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")

    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        # Appel de la static method identification définie dans la classe Utilisateur.
        # Récupération des données entrées par l'utilisateur dans le formulaire.
        utilisateur = Utilisateur.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None))

        # Si la static method identification renvoi utilisateur après la récupération des données entrées par
        # l'utilisateur dans le formulaire, l'utilisateur est considéré comme connecté grâce à login_user
        # (permettant notamment l'utilisation de login_required et current_user)
        # On informe l'utilisateur qu'il est connecté et on le redirige vers l'accueil.
        if utilisateur:
            flash("Vous êtes connecté-e", "success")
            login_user(utilisateur)
            return redirect("/")
        # Si la static method identification ne renvoi pas utilisateur après la récupération des données entrées par
        # l'utilisateur dans le formulaire, un message d'erreur en informe l'utilisateur.
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")


# Nom de la fonction vers laquelle l'utilisateur sera dirigé quand il doit se connecter.
login.login_view = 'connexion'


# Route pour la deconnexion de l'utilisateur :
@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    """
    Route permettant à l'utilisateur de se déconnecter
    """
    # Si l'utilisateur courrant est indentifié, on utilise la fonction logout_user() pour le deconnecter.
    if current_user.is_authenticated is True:
        logout_user()

    # Information à l'utilisateur.
    flash("Vous êtes déconnecté-e", "info")
    # Redirection à la page d'accueil
    return redirect("/")


# ROUTES POUR LA MODIFICATION DE DONNEES DANS LA BASE DE DONNEE PAR L'UTILISATEUR :


# LETTRES : Routes pour la création, édition et suppression de lettres dans la base de données :

# Route pour l'ajout d'une nouvelle lettre :
@app.route('/creation', methods=["POST", "GET"])
@login_required
def creation():
    """
    Route permettant l'ajout d'une nouvelle lettre
    :returns: template HTML avec le formulaire d'ajout de lettre et création d'une nouvelle lettre
    """

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":
        # Appel de la static method ajouter_lettre définie dans la classe Lettre.
        # Récupération des données entrées par l'utilisateur dans le formulaire.
        status, donnees_lettre = Lettre.ajouter_lettre(
            lettre_numero=request.form.get("lettre_numero", None),
            lettre_redacteur=request.form.get("lettre_redacteur", None),
            lettre_lieu=request.form.get("lettre_lieu", None),
            lettre_date=request.form.get("lettre_date", None),
        )

        # Si la static method a renvoyé True : les données ont pu être ajoutée.
        if status is True:
            # Information à l'utilisateur du succès de l'ajout :
            flash("La lettre a été ajoutée ! ", "success")
            # L'utilisateur est redirigé vers la page des lettres,
            # grâce à la fonction lettres précédemment définie.
            return redirect(url_for("lettres"))
        # Sinon, information à l'utilisateur des erreurs rencontrées :
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + " ; ".join(donnees_lettre), "danger")

    return render_template("pages/lettre_creation.html")


# Route pour lier une lettre à sa/ses publication(s) :
@app.route('/lettres/<int:lettre_id>/source', methods=["POST", "GET"])
@login_required
def source(lettre_id):
    """
    Route permettant l'ajout d'une nouvelle source (publication) à la lettre
    :param lettre_id: Identifiant de la lettre
    :type lettre_id: int
    :returns: template HTML avec le formulaire d'ajout de source à la lettre
    et création de ce nouveau lien publication/lettre.
    """
    # Récupération des données entrées par l'utilisateur dans le formulaire:
    source_lettre = request.form.get("publication_id", None)

    # Récupération de l'ID de la lettre à sourcer grâce .get_or_404()
    lettre_a_sourcer = Lettre.query.get_or_404(lettre_id)

    # Définition de la variable publications permettant l'affichage des données de la classe Publication
    # appelées dans le template.
    publications = Publication.query.all()

    # Si des données sont ajoutée par l'utilisateur :
    if source_lettre:
        # On les envoi avec l'ID de la lettre à la static methode sourcer_lettre de la classe Lettre.
        Lettre.sourcer_lettre(source_lettre, lettre_id)

        # En cas de succès de la static method, information à l'utilisateur que la lettre a bien été reliée
        # à un ouvrage.
        flash("La lettre est reliée à l'ouvrage {}".format(source_lettre), "success")

        # L'utilisateur est redirigé vers la page de la lettre, grâce à la fonction unique_lettre précédemment définie.
        return redirect(url_for("unique_lettre", lettre_id=lettre_id))

    return render_template("pages/source_ajouter.html", nom="Correspondance jésuite", lettre=lettre_a_sourcer,
                           publications=publications)


@app.route('/lettres/<lettre_id>/supprimer_source', methods=["POST", "GET"])
@login_required
def supprimer_source(lettre_id):
    """
    Route permettant de retirer un lien publication / lettre.
    (Ne fonctionne malheureusement pas...)
    :param lettre_id: Identifiant de la lettre
    :type lettre_id: int
    :returns: template HTML avec le formulaire d'ajout de source à la lettre
    et création de ce nouveau lien publication/lettre.
    """

    # Récupération de l'ID de la lettre dont on veut retirer le lien à sa publication grâce .get_or_404()
    lettre = Lettre.query.get_or_404(lettre_id)

    # Récupération de l'ID de la publication, déterminé dans le formulaire, dont on veut retirer le lien à la lettre.
    publication_id = request.form.get("publication_id", None)

    if publication_id:
        # On les envoi avec l'ID de la lettre à la static methode sourcer_lettre de la classe Lettre.
        Lettre.retirer_source_lettre(publication_id, lettre_id)

        # En cas de succès, confirmation à l'utilisateur que le lien publication / lettre à été supprimé.
        flash("Source supprimée !", "success")

        # L'utilisateur est redirigé vers la page de la lettre, grâce à la fonction unique_lettre précédemment définie.
        return redirect(url_for("unique_lettre", lettre_id=lettre_id))

    return render_template("pages/source_suppression.html", nom="Correspondance jésuite", lettre=lettre,
                           publication_id=publication_id)


# Route pour l'édition des données d'une lettre :
@app.route('/lettres/<int:lettre_id>/edition', methods=["POST", "GET"])
@login_required
def edition(lettre_id):
    """
    Route permettant l'édition des données d'une lettre
    :param lettre_id: Identifiant de la lettre
    :type lettre_id: int
    :returns: template HTML avec le formulaire d'édition de la transcription et modification de la transcription
    """
    # Définition d'une liste d'erreur vide.
    erreurs = []
    # Récupération de l'ID de la lettre à modifier grâce .get_or_404()
    lettre_modifiee = Lettre.query.get_or_404(lettre_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":

        # Récupération des données entrées par l'utilisateur dans le formulaire:
        lettre_numero = request.form.get("lettre_numero", None)
        lettre_redacteur = request.form.get("lettre_redacteur", None)
        lettre_lieu = request.form.get("lettre_lieu", None)
        lettre_date = request.form.get("lettre_date", None)

        # Définition des erreurs : Il faut un numero de lettre, un auteur, un lieu d'envoi et une date d'envoi.
        # Si c'est le cas, une "erreur" est ajoutée à la liste erreurs.
        if not lettre_numero:
            erreurs.append("Le champ numero lettre est vide.")
        if not lettre_redacteur:
            erreurs.append("Le champ auteur est vide.")
        if not lettre_lieu:
            erreurs.append("Le champ lieu d'envoi est vide.")
        if not lettre_date:
            erreurs.append("Le champ date d'envoi est vide.")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur :
        if not erreurs:
            # On ajoute les données précédemment récupérées du formulaire à la lettre à modifier précédemment
            # selectionnée.
            lettre_modifiee.lettre_numero = lettre_numero
            lettre_modifiee.lettre_redacteur = lettre_redacteur
            lettre_modifiee.lettre_lieu = lettre_lieu
            lettre_modifiee.lettre_date = lettre_date

            # Ajout des nouvelles des données à la place des anciennes et enregistrement.
            db.session.add(lettre_modifiee)
            db.session.commit()

            # Enregistrement de la modification dans la table contribution :
            if lettre_modifiee:
                # Récupération l'id de la lettre que l'on a modifié.
                lettre = Lettre.query.get_or_404(lettre_id)
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
                # Envoie dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Information pour l'utilisateur lui confirmant que la lettre a été modifée et récapitulant les
            # modifications grâce à .format() .
            flash(
                "La lettre modifiée a pour numéro {}, pour rédacteur {}, pour lieu {},"
                " pour date {}".format(lettre_modifiee.lettre_numero,
                                       lettre_modifiee.lettre_redacteur, lettre_modifiee.lettre_lieu,
                                       lettre_modifiee.lettre_date), "success")

            # L'utilisateur est redirigé vers la page des lettres,
            # grâce à la fonction lettres précédemment définie.
            return redirect(url_for("lettres"))

    return render_template("pages/lettre_edition.html", nom="Correspondance jésuite", lettre_modifiee=lettre_modifiee)


# Route pour la suppression d'une lettre de la DB :
@app.route("/lettres/<int:lettre_id>/suppression", methods=["POST", "GET"])
@login_required
def suppression_lettre(lettre_id):
    """
    Route permettant la suppression d'une lettre :
    :param lettre_id: Identifiant de la publication
    :type lettre_id: int
    :returns: template HTML avec le formulaire de confirmation avant la suppression de lettre
    et suppression de la lettre.
    """
    # Récupération de l'id de la publication grâce à .get_or_404()
    lettre_a_supprimer = Lettre.query.get_or_404(lettre_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        # Enregistrement de la modification dans la table contribution :
        if lettre_a_supprimer:
            # Récupération l'id de la lettre que l'on souhaite supprimer.
            lettre = Lettre.query.get_or_404(lettre_id)
            # Récupération l'id de l'utilisateur courant
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # Préparation des données à l'enregistrement :
            a_contribue = Contribution(utilisateur=utilisateur, lettre=lettre)
            # Envoi dans la DB et enregistrement
            db.session.add(a_contribue)
            db.session.commit()

        # Suppression de la publication de la DB et enregistrement de ce changement :
        db.session.delete(lettre_a_supprimer)
        db.session.commit()

        # Information pour l'utilisateur lui confirmant que la lettre a bien été supprimée.
        flash("La lettre a été supprimée", "success")

        # L'utilisateur est redirigé vers la page des lettres,
        # grâce à la fonction lettres précédemment définie.
        return redirect(url_for('lettres'))

    return render_template("pages/lettre_suppression.html", lettre=lettre_a_supprimer)


# TRANSCRIPTION : Routes pour la création, édition et suppression de transcription de lettre :

# Route pour l'ajout de transcription :
@app.route("/lettres/<int:lettre_id>/ajouter_transcription", methods=["POST", "GET"])
@login_required
def nouvelle_transcription(lettre_id):
    """
    Route permettant l'ajout d'une nouvelle transcription
    :param lettre_id: Identifiant de la transcription
    :type lettre_id: int
    :returns: template HTML avec le formulaire d'ajout de transcription et création d'une nouvelle transcription
    """

    # Définition d'une liste d'erreur vide.
    erreurs = []
    # Récupération de l'ID de la lettre à transcrire grâce .get_or_404()
    lettre_a_transcrire = Lettre.query.get_or_404(lettre_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":
        # Récupération des données entrées par l'utilisateur dans le formulaire:
        lettre_transcrite = request.form.get("transcription_lettre", None)

        # Définition d'une erreur : Il faut un texte de transcription.
        if not lettre_transcrite:
            # Si c'est le cas, une "erreur" est ajoutée à la liste erreurs.
            erreurs.append("Il n'y a pas de transcription")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur :
        if not erreurs:
            # On ajoute les données précédemment récupérées du formulaire à la lettre à transcrire précédemment
            # selectionnée.
            lettre_a_transcrire.transcription_texte.append(Transcription(transcription_texte=lettre_transcrite))
            # Ajout des nouvelles des données et enregistrement.
            db.session.add(lettre_a_transcrire)
            db.session.commit()

            # Enregistrement de la modification dans la table contribution :
            if lettre_a_transcrire:
                # Récupération l'id de la transcription que l'on souhaite supprimer.
                transcription = Transcription.query.order_by(Transcription.transcription_id.desc()).limit(1).first()
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
                # Envoie dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Information pour l'utilisateur lui confirmant que la transcription a été ajoutée.
            flash(
                "Votre transcription a été ajouté ! Merci de votre contribution !", "success")

            # L'utilisateur est redirigé vers la page des lettre,
            # grâce à la fonction lettres précédemment définie.
            return redirect(url_for("lettres"))

    return render_template("pages/transcription_creation.html", nom="Correspondance jésuite",
                           lettre_a_transcrire=lettre_a_transcrire)


# Route pour l'édition d'une transcription :
@app.route('/transcription/<int:transcription_id>/modifier_transcription', methods=["POST", "GET"])
@login_required
def modification_transcription(transcription_id):
    """
    Route permettant l'édition d'un ouvrage
    :param transcription_id: Identifiant de la transcription
    :type transcription_id: int
    :returns: template HTML avec le formulaire d'édition de la transcription et modification de la transcription
    """
    # Définition d'une liste d'erreur vide.
    erreurs = []
    # Récupération de l'ID de la transcription à modifier grâce .get_or_404()
    transcription_a_modifier = Transcription.query.get_or_404(transcription_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":
        # Récupération des données entrées par l'utilisateur dans le formulaire:
        transcription_modifiee = request.form.get("transcription_lettre_modifiee", None)

        # Définition d'une erreur : Il faut un nouveau texte de transcription.
        if not transcription_modifiee:
            # Si c'est le cas, une "erreur" est ajoutée à la liste erreurs.
            erreurs.append("Vous n'avez pas modifié la transcription.")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur :
        if not erreurs:
            # On ajoute les données précédemment récupérées du formulaire à la transcription à modifier précédemment
            # selectionnée.
            transcription_a_modifier.transcription_texte = transcription_modifiee

            # Ajout des nouvelles des données à la place des anciennes et enregistrement.
            db.session.add(transcription_a_modifier)
            db.session.commit()

            # Enregistrement de la modification dans la table contribution :
            if transcription_a_modifier:
                # Récupération l'id de la transcription que l'on souhaite supprimer.
                transcription = Transcription.query.get_or_404(transcription_id)
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
                # Envoie dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Information pour l'utilisateur lui confirmant que la transcription a été modifée.
            flash("La transcription a été modifiée !", "success")

            # L'utilisateur est redirigé vers la page des lettres,
            # grâce à la fonction lettres précédemment définie.
            return redirect(url_for("lettres"))

    return render_template("pages/transcription_edition.html", nom="Correspondance jésuite",
                           transcription_a_modifier=transcription_a_modifier)


# Route pour la suppression d'une transcription de la DB :
@app.route("/transcription/<int:transcription_id>/supprimer_transcription", methods=["POST", "GET"])
@login_required
def suppression_transcription(transcription_id):
    """
        Route permettant la suppression d'une transcription :
        :param transcription_id: Identifiant de la publication
        :type transcription_id: int
        :returns: template HTML avec le formulaire de confirmation avant la suppression de transcription
        et suppression de la transcription.
    """

    # Récupération de l'id de la publication grâce à .get_or_404()
    transcription_a_supprimer = Transcription.query.get_or_404(transcription_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        # Enregistrement de la modification dans la table contribution :
        if transcription_a_supprimer:
            # Récupération l'id de la publication que l'on souhaite supprimer.
            transcription = Transcription.query.get_or_404(transcription_id)
            # Récupération l'id de l'utilisateur courant
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # Préparation des données à l'enregistrement :
            a_contribue = Contribution(utilisateur=utilisateur, transcription=transcription)
            # Envoi dans la DB et enregistrement
            db.session.add(a_contribue)
            db.session.commit()

        # Suppression de la transcription de la DB et enregistrement de ce changement :
        db.session.delete(transcription_a_supprimer)
        db.session.commit()

        # Information pour l'utilisateur lui confirmant que la publication a bien été supprimée.
        flash("La transcription a été supprimée", "success")

        # L'utilisateur est redirigé vers la page des lettres,
        # grâce à la fonction lettres précédemment définie.
        return redirect(url_for('lettres'))
    return render_template("pages/transcription_suppression.html", transcription=transcription_a_supprimer)


# PUBLICATIONS : Routes pour la création, l'édition et la suppression d'ouvrage (table publication) :

# Route pour l'ajout d'un nouvel ouvrage dans lequel une lettre est publiée :
@app.route('/ajouter_publication', methods=["POST", "GET"])
@login_required
def publication_creation():
    """
    Route permettant l'ajout d'un nouvel ouvrage
    :returns: template HTML avec le formulaire d'ajout de publication et création du nouvel ouvrage
    """
    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":
        # Appel de la static method ajouter_publication définie dans la classe Publication.
        # Récupération des données entrées par l'utilisateur dans le formulaire.
        status, donnees_publication = Publication.ajouter_publication(
            publication_titre=request.form.get("publication_titre", None),
            publication_volume=request.form.get("publication_volume", None),
        )

        # Si la static method a renvoyé True : les données ont pu être ajoutée.
        # Information à l'utilisateur du succès de l'ajout :
        if status is True:
            flash("Le volume a été ajoutée ! ", "success")
            # L'utilisateur est redirigé vers la page des publications,
            # grâce à la fonction publications précédemment définie.
            return redirect(url_for("publications"))

        # Sinon, information à l'utilisateur des erreurs rencontrées :
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + " ; ".join(donnees_publication), "danger")

    return render_template("pages/publication_creation.html", errors="errors")


# Route pour l'édition d'un ouvrage dans lequel une lettre est publiée :
@app.route('/publications/<int:publication_id>/edition', methods=["POST", "GET"])
@login_required
def edition_publication(publication_id):
    """Route permettant l'édition d'un ouvrage
    :param publication_id: Identifiant de la publication
    :type publication_id: int
    :returns: template HTML avec le formulaire d'édition de publication et modification de l'ouvrage
    """
    # Définition d'une liste d'erreur vide.
    erreurs = []
    # Récupération de l'ID de la publication à modifier grâce .get_or_404()
    publication_modifiee = Publication.query.get_or_404(publication_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == "POST":

        # Récupération des données entrées par l'utilisateur dans le formulaire:
        publication_titre = request.form.get("publication_titre", None)
        publication_volume = request.form.get("publication_volume", None)

        # Définition d'une erreur : le titre ne doit pas être vide.
        if not publication_titre:
            # Si c'est le cas, une "erreur" est ajoutée à la liste erreurs.
            erreurs.append("Le champ numero lettre est vide.")

        # Si la longueur de la liste erreurs est supérieur à 0, donc si il y a au moins une erreur :
        if len(erreurs) > 0:
            # Renvoi False et la liste erreurs.
            return False, erreurs

        # Si il n'y a pas d'erreur :
        if not erreurs:
            # On ajoute les données précédemment récupérées du formulaire à la publication à modifier précédemment
            # selectionnée.
            publication_modifiee.publication_titre = publication_titre
            publication_modifiee.publication_volume = publication_volume

            # Ajout des nouvelles des données à la place des anciennes et enregistrement.
            db.session.add(publication_modifiee)
            db.session.commit()

            # Enregistrement de la modification dans la table contribution :
            if publication_modifiee:
                # Récupération l'id de la publication que l'on souhaite supprimer.
                publication = Publication.query.get_or_404(publication_id)
                # Récupération l'id de l'utilisateur courant
                utilisateur = Utilisateur.query.get(current_user.ut_id)
                # Préparation des données à l'enregistrement :
                a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
                # Envoie dans la DB et enregistrement
                db.session.add(a_contribue)
                db.session.commit()

            # Information pour l'utilisateur lui confirmant que la publication a été modifée et récapitule
            # les modifications grâce à .format().
            flash(
                "Vous avez modifié les données de cet ouvrage. Le titre est maintenant : {} et le tome : {}".format(
                    publication_modifiee.publication_titre, publication_modifiee.publication_volume
                                       ), "success")

            # L'utilisateur est redirigé vers la page des publications,
            # grâce à la fonction publications précédemment définie.
            return redirect(url_for("publications"))

    return render_template("pages/publication_edition.html", nom="Correspondance jésuite",
                           publication_modifiee=publication_modifiee)


# Route pour la suppression d'un ouvrage de la DB :
@app.route("/publications/<int:publication_id>/suppression", methods=["POST", "GET"])
@login_required
def suppression_publication(publication_id):
    """
    Route permettant la suppression d'un ouvrage :
    :param publication_id: Identifiant de la publication
    :type publication_id: int
    :returns: template HTML avec le formulaire de confirmation avant la suppression de publication
    et suppression de l'ouvrage.
    """
    # Récupération de l'id de la publication grâce à .get_or_404()
    source_a_supprimer = Publication.query.get_or_404(publication_id)

    # Si la méthode est POST cela signifie que le formulaire est envoyé
    if request.method == 'POST':

        # Enregistrement de la modification dans la table contribution :
        if source_a_supprimer:
            # Récupération l'id de la publication que l'on souhaite supprimer.
            publication = Publication.query.get_or_404(publication_id)
            # Récupération l'id de l'utilisateur courant
            utilisateur = Utilisateur.query.get(current_user.ut_id)
            # Préparation des données à l'enregistrement :
            a_contribue = Contribution(utilisateur=utilisateur, publication=publication)
            # Envoie dans la DB et enregistrement
            db.session.add(a_contribue)
            db.session.commit()

        # Suppression de la publication de la DB et enregistrement de ce changement :
        db.session.delete(source_a_supprimer)
        db.session.commit()

        # Information pour l'utilisateur lui confirmant que la publication a bien été supprimée.
        flash("Cet ouvrage a été supprimé", "success")

        # L'utilisateur est redirigé vers la page des publications,
        # grâce à la fonction publications précédemment définies.
        return redirect(url_for('publications'))

    return render_template("pages/publication_suppression.html", publication=source_a_supprimer)
