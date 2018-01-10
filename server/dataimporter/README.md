# DataImporter
Module d'importation des données des APIs (Reddit, Twitter, Cryptocompare, etc.)

## Structuration du module
Isolation des différentes fonctionnalités dans des packages / dossiers

### Packages / Fichiers :
- Coinmarketcap / Cryptocompare : classe qui attaquent directement les API en question
- Config : Classe permettant de récupérer les informations de config situés dans le fichier config.ini (toutes les informations de config doivent être ici et non pas en dur dans le code)
- Dbaccess : Classe permettant les accès DB (exécution de requêtes SQL)
- ExtractData : Méthodes permettants la transformation des données JSON récupérées via les API pour insertion en BDD
- Main.py : Classe centrale, à revoir quand on utilisera un job scheduler 