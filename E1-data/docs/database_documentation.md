# Documentation C4 – Base de données


## 1. Modélisations des données (Méthode / formalisme Merise)
Éléments disponibles:
- Fichier `diagramme_ER.png` (diagramme entité–relation) représentant les entités principales: `Currency`, `TradingPair`, `Exchange`, `CryptocurrencyCSV`, `CSVHistoricalData`, `OHLCVMinute`, `OHLCVHourly`, `OHLCVDaily`, `User`, `ForecastMinute`, `ForecastHourly`, `ForecastDaily`.
- Les entités et contraintes sont implémentées dans `models.py` avec `UniqueConstraint` et contraintes de nullabilité.
- Livrables formalisés MCD/MLD sont dans `merise_model.md` (voir ce fichier pour la description des entités, associations, cardinalités et traduction relationnelle).
 - Un diagramme Mermaid (MCD) est intégré dans `merise_model.md` pour une visualisation graphique directement dans le dépôt.

## 2. Modèle physique fonctionnel (création sans erreur)
- Le moteur est initialisé dans `database.py` via SQLAlchemy: `create_engine("postgresql+psycopg2://...")` puis `Base.metadata.create_all(engine)`.
- Toutes les tables sont créées à partir des classes ORM sans dépendances cycliques déclarées.
- Colonnes critiques définies avec `nullable=False` garantissant l’intégrité.

## 3. Choix de la base de données
- Implémentation actuelle: PostgreSQL (via l’URL `postgresql+psycopg2`).
- Justification implicite: besoin d’intégrité référentielle (ForeignKey), contraintes d’unicité, requêtes analytiques structurées sur OHLCV et prévisions; PostgreSQL est adapté à ces exigences relationnelles.
- Choix PostgreSQL pertinent pour la suite: volume de données attendu important (OHLCV minute / horaire / quotidien + prévisions), besoin de croissance sans modification majeure.
- PostgreSQL gère efficacement:
    - Concurrence élevée (MVCC) si plusieurs opérations d’agrégation / mises à jour simultanées.
    - Transactions fiables pour opérations batch (import massif + agrégations).
- Prépare la montée en charge future (ajout de nouvelles paires, granularités supplémentaires, historisation longue).

## 4. Reproductibilité de l’installation (BD et API)
Étapes (inférées):
1. Créer une base PostgreSQL et un utilisateur avec droits adéquats.
2. Définir le fichier `.env` (variables: `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `CMC_API_KEY`, variables API utilisateur si besoin).
3. Installer les dépendances Python (voir `requirements.txt`).
4. Lancer une initialisation / import: `python init_db_and_data.py --all` ou étapes granulaires (voir section 6 / 7).

## 5. Script(s) d’import – Fonctionnalité
Scripts d’alimentation présents dans `src/C4_database/feed_db`:
- `feed_coinmarketcap.py` : insertion des `Currency` (crypto & fiat) + `Exchange`.
- `feed_cryptodowload.py` : création / association des `TradingPair`, enregistrement des métadonnées CSV (`CryptocurrencyCSV`).
- `feed_csv_data.py` : insertion des données historiques brutes (`CSVHistoricalData`).
- `feed_ohlcv_data.py` : insertion des données agrégées OHLCV par granularité (minute / hourly / daily).
- `feed_user.py` : création d’un utilisateur API initial (authentification future).
Orchestration:
- `init_db_and_data.py` offre des flags: `--extract_files`, `--feed_raw_db`, `--extract_data`, `--aggregate`, `--initiate_api_user`, `--all`.
- Les méthodes CRUD utilisent `bulk_insert_mappings` avec fallback insertion unitaire pour résilience.

## 6. Documentation technique versionnée
- Ce fichier `documentation.md` est placé dans le dossier `C4_database` et versionné dans le même dépôt Git que les scripts d’import.

## 7. Dépendances & environnement
Langage:
- Python (>=3.12 observé via artefacts de bytecode).
Bibliothèques principales:
- `SQLAlchemy` (ORM, définition des modèles, intégrité).
- `psycopg2` (driver PostgreSQL – implicite via URL). 
- `pandas` (formatage DataFrame précédent les insertions OHLCV / historiques).
- `requests` (utilisé pour extractions amont avant import – dépendance indirecte du pipeline).
- `python-dotenv`, `PyYAML` (chargement configuration / secrets).
Commandes d’installation (exemple):
```
pip install -r requirements.txt
```
Variables d’environnement (`.env`):
```
DB_USERNAME=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
DB_NAME=...
CMC_API_KEY=...
```

## 8. Commandes d’exécution (import & pipeline)
Exemples:
- Pipeline complet (extraction + alimentation + agrégation + utilisateur):
```
python init_db_and_data.py --all
```
- Uniquement alimentation brute (CoinMarketCap + CryptoDataDownload):
```
python init_db_and_data.py --feed_raw_db
```
- Extraction des fichiers JSON distance + enregistrement local:
```
python init_db_and_data.py --extract_files
```
- Extraction des données CSV vers historique + agrégation:
```
python init_db_and_data.py --extract_data --aggregate
```
- Création utilisateur API initial:
```
python init_db_and_data.py --initiate_api_user
```
- Mise à jour incrémentale OHLCV Binance:
```
python update_ohlcv.py --frequency hour
python update_ohlcv.py --frequency day
```

## 9. Registre des traitements de données personnelles (RGPD)
- Données personnelles identifiables présentes: table `User` avec `username`, `password_hashed`, `status`, `role`.
- Minimisation: seuls identifiants et rôle sont stockés; mot de passe sous forme hachée (hypothèse basée sur champ `password_hashed`).
- Autres tables (OHLCV, devises, échanges) ne contiennent pas de données personnelles.

## 10. Procédures de tri des données personnelles (mise en conformité RGPD)
Justification: la seule donnée potentiellement personnelle est `username` (pseudonyme possible) et le mot de passe est stocké déjà haché (`password_hashed`). Aucune donnée sensible (email, nom légal, localisation, profil comportemental) n’est conservée. Conformément au principe de minimisation, aucune procédure de tri supplémentaire n’a été mise en place à ce stade.

## 11. Fréquence / automatisation des traitements de conformité RGPD
Même justification que le point 10. Aucune planification spécifique (cron, purge) n’est documentée car l’exposition de données personnelles est quasi nulle. Pas d'informations supplémentaires concernant une fréquence formalisée.