# AlgoCryptos
Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies

## Monter environnement de développement

- Outils :
    - Transverses :
        - Git (pré-requis - gestionnaire de code source) : https://git-scm.com/
        - SGBD PostgreSQL (dernière version v10.1) : https://www.postgresql.org/ftp/source/v10.1/
        - SGBD PostgreSQL administration (outil pgadmin) : https://www.pgadmin.org/download/
    - Back-end (scripts Python) :
        - Python (dernière version 3.x)
        - IDE Python : Jetbrain Pycharm community - gratuit
    - Front+back-end (Node / Angular) :
        - NodeJs (dernière version) : https://nodejs.org/en/download/
        - IDE Node : Jetbrain WebStorm Community - gratuit
    
- Paramétrage environnement (cf. pré-requis Outils ci-dessus) :
    - Transverse :
        - Créer la base de données et les users via pgadmin avec les scripts contenus dans server/db (scripts à mettre à jour au fur et à mesure), dans l'ordre :
            - 1 / createUser
            - 2 / createDB
            - 3 / createTables
    - Python :
        - Ouvrir Pycharm et choisir d'ouvrir un projet via Github
        - Choisir Algo_crypto_scripts
        - Paramétrer l'interpreteur Python dans l'IDE (via un virtualEnv)
            -Menu File / Setting 
            -Item Project : AlgoCrypto_scripts
            -Item Project Interpreter :
                - En haut à droite, cliquer sur la petite roue
                - Add Locale
                - Choisir VirtualEnv Environnement (sélectionné par défaut)
                - Dossier du type : \algocryptos_script\venv
                - Base Interpreter : Python 3.6
                - Cliquer sur OK pour instancier le nouveau VirtualEnv
        - Installer les librairies externes Python utilisées par le projet : 
            - Dans le Terminal de Pycharm (onglet en bas de l'IDE)
            - Taper pip3 install -r requirements.txt
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
   
## Deployment
- Dev : Update requirements.txt with command :
    - pip freeze > requirements.txt
    - supprimer logging (déjà présent dans Python)
- Python : Git clone repository + install : to be completed
- Angular : https://angular.io/guide/deployment
    -Pré-requis : Installer Node et installer le package.json : npm install
    -Dans repo algocryptos_web : 
        -src/environments/environment.prod.ts : si nécessaire, maj url API vers serveur node api
        -Lancer la commande pour builder le projet : ng build --prod
        -Récupérer le contenu du dossier dist/ et le copier sur le serveur web (Apache, etc.)
- Node :
    -To be completed : npm install à faire aussi

https://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/
 
## Régler problème en production
- Process manager, il se peut (en théorie non mais on ne sait jamais), qu'un process reste inscrit
dans la table process_params ce qui aura pour effet de bloquer les autres traitements.
Il est possible d'appeler cet api http://localhost:3000/api/params/resetprocesses pour vider la table
et permettre aux traitements de se lancer correctement

## EC2 : Lancer traitements sur serveur via connexion SSH
- source prod/algocryptos_scripts/venv/bin/activate
- export PYTHONPATH=$PYTHONPATH:/home/ec2-user/prod/algocryptos_scripts
- python /home/ec2-user/prod/algocryptos_scripts/dataimporter/main.py -r
- killer tous les traitements python : pkill -f python

## EC2 : Executer des commandes SQL sur RDS via EC2
- psql -h algocryptos.c592sqstvfao.eu-west-3.rds.amazonaws.com -d algocryptos -U algocryptouser
- \dp : voir les tables de la base de données
- select * from coins; // Attention du ; sinon ne fonctinone pas
- psql -h algocryptos.c592sqstvfao.eu-west-3.rds.amazonaws.com -d algocryptos -U algocryptouser -f file.sql => Lancer les requêtes d'un fichier

## EC2 : Divers
- Monitorer Node : pm2 monit
- Modifier la crontab : crontab -e
- Créer une Tunnel SSH pour accéder à la BDD depuis poste local : https://userify.com/blog/howto-connect-mysql-ec2-ssh-tunnel-rds/

## EC2 : Déploiement
- Dépedances : Dans environnemnt de développement : pip freeze > requirements.txt puis mettre à jour sur Github
- Verify sources before deployment @ChangeManager
- Generate server.zip and front.zip and push it on Github in /builds
- Verify that autodeploy script is updated (if none, git pull)
- Connect to EC2 and go to path prod/algocryptos_scripts/scripts/
- Start script on EC2 sh autodeploy.sh ~/prod
- Back-end only : sh autodeploy.sh -b ~/prod
- When script ask, enter rsa : algocryptos
- Check everything is ok + crontab -e to check that crontab is not empty