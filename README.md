# Correspondance Lainez

## Le projet
Application Flask pour l'évaluation finale du cours Python de Mr Clérice (M2 TNAH, École nationale des chartes, année 2020-2021).

## L'application
Correspondance Jésuite est une application web pensée comme un outil collaboratif pour centraliser l'importante correspondance reçue par le général Lainez, Préposé général de la Compagnie de Jésus entre 1558 et 1565. Pour l'instant, elle rassemble les lettres issues de quelques volumes [numérisés](http://www.sjweb.info/arsi/en/publications/ihsi/monumenta/) de la Monumenta Historica Societatis Iesu, concernant principalement la correspondance européenne.

Elle répond à deux objectifs : 
- Naviguer parmi les données répertoriées dans la base de données : lettres, transcriptions et sources. 
- Participer en ajoutant, éditant et supprimant du contenu : des lettres, des transcriptions et des sources.

### Consulter les données :
Les données sont consultables par tous. Chacun peut consulter les lettres, les transcriptions et les sources.

### Enrichir les données :
L'enrichissement des données est réservé aux utilisateurs. 
Après s'être inscrit, l'utilisateur peut participer à ce projet collaboratif et donc peut ajouter, éditer et supprimer des lettres, des sources et des transcriptions.

### Données ouvertes
Toutes les données sont ouvertes et peuvent être récupérées en JSON.

## Installation (MAC / Linux)
Pré-requis : python3

- Créer un dossier et cloner ce repository dedans : ``git clone https://github.com/D0riane/Correspondance_Lainez.git``
- Aller dans le dossier de l'application : ``cd Correspondance_Lainez``
- Installer l'environnement virtuel : ``virtualenv -p python3 env`` 
- Activer cet environnement : `` source env/bin/activate ``
- Installer les librairies nécessaires rassemblées dans [requirements.txt](https://github.com/D0riane/correspondance_Lainez/blob/master/requirements.txt) : ``pip install -r requirements.txt``
- Lancer l'application : ``python3 run.py``

L'application se lancera sur votre navigateur sur la page http://127.0.0.1:5000 .

## Lancement (MAC / Linux)
A chaque nouveau lancement, il sera nécessaire de :
- Aller dans le dossier de l'application : ``cd Correspondance_Lainez``
- Activer l'environnement virtuel (`` source env/bin/activate ``)
- Lancer l'application ( ``python3 run.py`` ) .

## Auteur 
Ce projet est proposé par **Doriane Hare** ( [@D0riane](https://github.com/D0riane) )
