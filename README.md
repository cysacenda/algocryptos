# AlgoCryptos
Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies

## Monter environnement de développement
- Outils :
    - Transverses :
        - Git
        - SGBD PostgreSQL (dernière version v10.1)
        - SGBD PostgreSQL administration : pgadmin
    - Python :
        - Python (dernière version)
        - IDE Python : Jetbrain Pycharm community - gratuit
    - Fronting / Node / Angular :
        - NodeJs (dernière version)
        - IDE Jetbrain WebStorm
        - ...
    
- Paramétrage environnement (cf. pré-requis Outils ci-dessus) :
    - Transverse :
        - Créer la base de données et les users via pgadmin avec les scripts contenus dans server/db (scripts à mettre à jour au fur et à mesure), dans l'ordre :
            - 1 / createUser
            - 2 / createDB
            - 3 / createTables
    - Python :
        - Paramétrer Python dans l'IDE : File / Setting / Project Interpreter / Add Local et choisir installation Python locale
        - Installer les librairies manquantes Python dans le Terminal de Pycharm via la commande "setup.py install" 
        - installer le token github / sinon utilisation possible login / mdp
    - Fronting / Node / Angular :
        - Faire un install du package.json
        - Utiliser les scripts du package.json via Webstorm pour builder le node, starter le node et starter l'angular
        - Il est possible de faire du debug avec Webstorm (node / angular)

## Déploiement / Gestion de la BDD
- Une release par semaine pour le moment
- S'assurer que tout ce qui est commité fonctionne
- Figer une branche prod 1-2j avant de déployer
- Dev : Toute modification du modèle de données doit être répercutée dans les scripts :
    -createTables.sql : Création du modèle de données, toutes les tables, etc.
    -populateDB.sql : Ajout de données en bas
    -modifsBDD.sql : toutes les modifications du modèle de données actuellement en prod, doit être vidé après chaque déploiement

## Infos login / mdp (Dev / Ops only)
- Télécharger logiciel Keepass : https://keepass.info/
- Récupérer la BDD Keepass dans Github : algocryptos/docs/keepass
- Demander la masterkey à CSA via Slack
- PostgreSQL admin : algocryptos

## Accès Cloud (Ops only)
- Devops only: Demander création d'un compte à CSA via Slack


## Utilisation Git via Pycharm (simple)
- Pousser du code sur Git : 
    - VCS / Update (on update avec la dernière version du code avant de pousser, si merge nécessaire, faire bien attention de ne pas écraser du code)
    - VCS / Commit...
        - Vérifier / sélectionnez les fichiers qui vont être commités
        - Si vous voulez pusher sur Github et pas uniquement en local, faire commit & push
- Updater votre local avec le code présent sur Github :
    - VCS / Update
    
##Régler problème en production
- Process manager, il se peut (en théorie non mais on ne sais jamais), qu'un process reste inscrit
dans la table process_params ce qui aura pour effet de bloquer les autres traitements.
Il est possible d'appeler cet api http://localhost:3000/api/params/resetprocesses pour vider la table
et permettre aux traitements de se lancer correctement