from warnings import warn

# Dans ce fichier, nous déterminons les constantes de notre projet :

# Le nombre de lettre par page lors de l'utilisation de l'objet paginate.
LETTRES_PAR_PAGE = 10
#
SECRET_KEY = "JE SUIS UN SECRET !"
# La route pour l'API
API_ROUTE = "/api"

#
if SECRET_KEY == "JE SUIS UN SECRET !":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)
