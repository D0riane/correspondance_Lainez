# Import des modules Flask et sqlaclchemy nécessaire au fonctionnement de l'application
from flask import request, jsonify
from sqlalchemy import or_

# Import de l'application, des constantes et des classes.
from ..app import app
from ..constantes import API_ROUTE
from ..modeles.donnees import Lettre, Publication, Transcription


def Json_404():
    response = jsonify({"erreur": "Unable to perform the query"})
    response.status_code = 404
    return response


@app.route(API_ROUTE+"/lettres")
def api_lettres():
    """
    Récupérer les données de toutes les lettres en JSON
    """
    query = Lettre.query

    try:
        lettres = query

    except Exception:
        return Json_404()

    dict_lettres = {
            "links": {
                "self": request.url
            },
            "data": [
                lettres.to_jsonapi_dict()
                for lettres in lettres
            ]
        }

    response = jsonify(dict_lettres)

    return response


@app.route(API_ROUTE+"/lettres/<lettre_id>")
def api_lettre_unique(lettre_id):
    """
    Récupérer les données de la lettre en JSON
    """
    try:
        query = Lettre.query.get(lettre_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/publications")
def api_publications():
    """
    Récupérer les données de toutes les publications en JSON
    """
    query = Publication.query
    try:
        publications = query

    except Exception:
        return Json_404()

    dict_publications = {
            "links": {
                "self": request.url
            },
            "data": [
                publications.to_jsonapi_dict()
                for publications in publications
            ]
        }

    response = jsonify(dict_publications)
    return response


@app.route(API_ROUTE+"/publications/<publication_id>")
def api_publication_unique(publication_id):
    """
    Récupérer les données de la publication en JSON
    """
    try:
        query = Publication.query.get(publication_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/transcriptions")
def api_transcriptions():
    """
    Récupérer les données de toutes les transcriptions en JSON
    """
    query = Transcription.query
    try:
        transcriptions = query

    except Exception:
        return Json_404()

    dict_transcriptions = {
            "links": {
                "self": request.url
            },
            "data": [
                transcriptions.to_jsonapi_dict()
                for transcriptions in transcriptions
            ]
        }

    response = jsonify(dict_transcriptions)
    return response


@app.route(API_ROUTE+"/transcriptions/<transcription_id>")
def api_transcription_unique(transcription_id):
    """
    Récupérer les données de la transcription en JSON
    """
    try:
        query = Transcription.query.get(transcription_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/recherche")
def api_lettres_recherche():
    """
    Route permettant d'avoir le résultat d'une recherche en JSON
    """
    # Récupération du mot clé renseigné par l'utilisateur.
    motclef = request.args.get("keyword", None)

    # Si il y a un mot clé, on filtre grâce à .like les résultats de la recherche.
    if motclef:
        query = Lettre.query.filter(or_(Lettre.lettre_numero.like("%{}%".format(motclef)),
                                        Lettre.lettre_date.like("%{}%".format(motclef)),
                                        Lettre.lettre_redacteur.like("%{}%".format(motclef)),
                                        Lettre.lettre_lieu.like("%{}%".format(motclef)),
                                        Lettre.lettre_volume.any(Publication.publication_titre.like("%{}%".format(
                                            motclef)))))
    else:
        query = Lettre.query

    try:
        resultats = query

    except Exception:
        return Json_404()

    dict_resultats = {
        "links": {
            "self": request.url
        },
        "data": [
            lettres.to_jsonapi_dict()
            for lettres in resultats
        ]
    }

    response = jsonify(dict_resultats)
    return response
