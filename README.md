# algocryptos
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
        - Installer les librairies manquantes Python avec la commande pip3 install xxxx (where xxxx = library name)
        - installer le token github
    - Fronting / Node / Angular :

##Infos login / mdp (Dev / Ops only)
- Télécharger logiciel Keepass : https://keepass.info/
- Récupérer la BDD Keepass dans Github : algocryptos/docs/keepass
- Demander la masterkey à CSA via Slack
- PostgreSQL admin : algocryptos

## Accès Cloud (Ops only)
- Devops only: Demander création d'un compte à CSA via Slack


