from flask import render_template, request, url_for, jsonify
from urllib.parse import urlencode

from ..app import app
from ..constantes import LETTRES_PAR_PAGE, API_ROUTE
from ..modeles.donnees import Lettre, Utilisateur, Publication, Transcription


def Json_404():
    response = jsonify({"erreur": "Unable to perform the query"})
    response.status_code = 404
    return response


@app.route(API_ROUTE+"/lettres")
def api_lettres():
    try:
        query = Lettre.query.all()
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/lettres/<lettre_id>")
def api_lettre_unique(lettre_id):
    try:
        query = Lettre.query.get(lettre_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/publications")
def api_publications():
    try:
        query = Publication.query.all()
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/publications/<publication_id>")
def api_publication_unique(publication_id):
    try:
        query = Publication.query.get(publication_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/transcriptions")
def api_transcriptions():
    try:
        query = Transcription.query.all()
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/transcriptions/<transcription_id>")
def api_transcription_unique(transcription_id):
    try:
        query = Transcription.query.get(transcription_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return Json_404()


@app.route(API_ROUTE+"/recherche")
def api_lettres_recherche():
    """ Route permettant d'avoir le résultat d'une recherche en JSON
    """
    # q est très souvent utilisé pour indiquer une capacité de recherche
    motclef = request.args.get("q", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    if motclef:
        query = Lettre.query.filter(
            Lettre.date_envoi.like("%{}%".format(motclef))
        )
    else:
        query = Lettre.query

    try:
        resultats = query.paginate(page=page, per_page=LETTRES_PAR_PAGE)
    except Exception:
        return Json_404()

    dict_resultats = {
        "links": {
            "self": request.url
        },
        "data": [
            lettres.to_jsonapi_dict()
            for lettres in resultats.items
        ]
    }

    if resultats.has_next:
        arguments = {
            "page": resultats.next_num
        }
        if motclef:
            arguments["q"] = motclef
        dict_resultats["links"]["next"] = url_for("api_lettres_recherche", _external=True)+"?"+urlencode(arguments)

    if resultats.has_prev:
        arguments = {
            "page": resultats.prev_num
        }
        if motclef:
            arguments["q"] = motclef
        dict_resultats["links"]["prev"] = url_for("api_lettres_recherche", _external=True)+"?"+urlencode(arguments)

    response = jsonify(dict_resultats)
    return response
