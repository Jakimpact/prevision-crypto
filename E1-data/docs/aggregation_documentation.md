# Documentation C3 - Agrégation des données OHLCV

## Objectif

Dans ce projet, l'agrégation consiste à transformer des enregistrements OHLCV bruts issus de fichiers CSV (référencés dans la base après extraction) en séries consolidées par paire de trading et par date/intervalle temporel (`minute`, `hour`, `day`). Le résultat est stocké dans les tables OHLCV correspondantes pour servir de fondation aux étapes ultérieures (mise à jour incrémentale, modélisation, API, etc.).

## Périmètre traité
- Source amont: table `CSVHistoricalData` (chargée préalablement à partir des CSV téléchargés via CryptoDataDownload + filtrage par paires/timeframes configurés).
- Cible: tables OHLCV agrégées (minute, hourly, daily) accessibles via les objets CRUD (`db.ohlcv_minute`, `db.ohlcv_hourly`, `db.ohlcv_daily`).
- Granularités prises en charge: `day`, `hour`, et variantes de timeframes minute (chaînes finissant par `minute`).

## Fichier principal
Fichier: `aggregate_ohlcv.py`
- `aggregate_all_ohlcv()`: orchestrateur. Pour chaque (paire, timeframe) disponible dans l'historique CSV, récupère les enregistrements, les agrège et persiste le DataFrame résultant.
- `aggregate_ohlcv_data(ohlcv_data, trading_pair, timeframe)`: logique d'agrégation et de normalisation (voir docstring enrichi dans le code). 

## Dépendances & modules utilisés
- `pandas`, `numpy`: manipulation et agrégation vectorisée des données tabulaires.
- Couche requête (`src/C2_query.query_historical_ohlcv`): récupération des données brutes et de la liste des paires/timeframes à traiter.
- Couche base de données (`src.C4_database.database`, `feed_ohlcv_data_to_db`): session et persistance des lignes agrégées.
- `logging` via `src.settings.logger`: traçabilité des étapes et erreurs.

## Commande / Point d'entrée
L'agrégation est déclenchée:
1. Par le pipeline global: `python init_db_and_data.py --aggregate` (ou `--all`).
2. Indirectement après extraction des CSV: étape alignée dans le pipeline E1.

## Enchaînement logique détaillé
1. Ouverture d'une session BD (`with Database() as db`).
2. Récupération de toutes les combinaisons (paire, timeframe) présentes dans `CSVHistoricalData`.
3. Pour chaque combinaison:
   - Chargement des enregistrements bruts (colonnes: date, open, high, low, close, volume_quote).
   - Passage à `aggregate_ohlcv_data`.
   - Sélection de la table cible selon le timeframe.
   - Persistance via `save_ohlcv_data_to_db` (insertion en BD, gestion des conflits éventuels selon implémentation de la fonction feed).
4. Journalisation des avertissements en cas d'absence de données.

## Règles de nettoyage et d'homogénéisation
Actuellement implémenté:
- Fusion des doublons temporels: groupby sur `(trading_pair_id, date)` pour créer une ligne unique.
- Normalisation des prix d'ouverture/fermeture: moyenne pondérée par `volume_quote`; fallback en moyenne simple si volume total nul (évite division par zéro et assure une valeur cohérente).
- Consolidation des extrêmes: `high = max`, `low = min` pour préserver l'enveloppe de volatilité intra-période.
- Agrégation additive du volume: somme de `volume_quote`.
- Production d'un schéma de colonnes homogène pour toutes les granularités: `[trading_pair_id, date, open, close, volume_quote, high, low]`.

 Validation / filtrage implicites présents ailleurs (couche `C4_database`):
 - Contraintes d'intégrité SQLAlchemy / base: colonnes `nullable=False` (empêche insertion de valeurs manquantes pour open/high/low/close/volume/date), contraintes d'unicité sur `(csv_file_id, date)` et `(trading_pair_id, date)` (évite doublons bruts et agrégés).
 - Gestion des conflits d'insertion: méthode `create_many` (fallback insertion individuelle) capture les `IntegrityError`; les enregistrements invalides ou dupliqués sont listés et journalisés (fichiers `failed_*.json`).
 - Filtrage des paires non conformes dans `feed_cryptodowload.get_trading_pair`: parsing symbol / validation du quote dans une liste blanche (`USDT`, `USDC`, `DAI`, `BTC`, `ETH`, `BNB`, `USD`, `EUR`) -> exclusion des paires atypiques ou mal formées.
 - Normalisation amont (hors C4 mais complémentaire): dans l'extraction CSV (`extract_csv_data.read_csv_data`) les dates invalides sont écartées (`dropna` après conversion) avant insertion.

 Conséquence: une partie du « nettoyage » est distribuée entre parsing amont, contraintes structurelles de la base et journalisation des échecs, même si aucune fonction dédiée de "validation métier" centralisée n'est encore implémentée.

## Choix techniques justifiés
- Pandas groupby pour performance et lisibilité sur des volumes historiquement raisonnables (OHLCV crypto minute/heure/jour).
- Calcul pondéré open/close: reflète mieux le prix représentatif lorsque plusieurs enregistrements partiels existent.
- Fallback sur moyenne simple: garante d'une valeur sans erreur lorsque `volume_quote == 0`.
- Journalisation plutôt qu'exception bloquante: permet de poursuivre le traitement d'autres paires même si une paire/timeframe échoue.

## Gestion des erreurs
- Bloc try/except dans `aggregate_ohlcv_data`: capture toute exception inattendue, log contextuel (paire + timeframe), retourne `None`.

## Exemple simplifié de flux
1. Ligne brute 1 (BTC/USDT, 2024-01-01, open=42000, close=42100, vol=10, high=42200, low=41950)
2. Ligne brute 2 (BTC/USDT, 2024-01-01, open=42100, close=42050, vol=5, high=42250, low=42000)
3. Agrégation:
   - volume_quote total = 15
   - open pondéré = (42000*10 + 42100*5)/15 = 42033.33
   - close pondéré = (42100*10 + 42050*5)/15 = 42083.33
   - high = max(42200, 42250) = 42250
   - low = min(41950, 42000) = 41950
4. Résultat inséré: ligne unique normalisée.

## Validation fonctionnelle
- Une exécution produit une ligne unique par (paire, date, timeframe) dans les tables OHLCV cibles.
- Les prix agrégés reflètent l'intensité (volume) lorsque disponible.
- L'absence de volume n'interrompt pas le processus ni ne crée d'erreur.
