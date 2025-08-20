# Documentation globale du dossier `C2_query`

Ce dossier regroupe les fonctions d'accès aux données pour les objets principaux du projet (OHLCV, TradingPair, Currency, Exchange, CSV historiques). Les fonctions sont organisées par type d'objet et par granularité temporelle.

## Patterns communs

- **Filtrage ciblé** : Toutes les fonctions utilisent des filtres précis sur les identifiants, noms, symboles ou timeframes pour limiter la recherche aux données pertinentes.
- **Jointures** : Les fonctions qui nécessitent des relations entre tables (ex : historique OHLCV) utilisent des jointures explicites pour accéder aux données liées.
- **Tri et sélection** : Pour obtenir la dernière entrée (minute, hourly, daily), les fonctions trient par date décroissante et utilisent `.first()` pour optimiser la récupération.
- **Recherche partielle** : Certaines fonctions utilisent `.ilike` pour permettre une recherche flexible sur les chaînes de caractères (ex : timeframe).
- **Optimisation** : Les requêtes sont construites pour limiter le volume de données retourné (filtrage, tri, jointure, distinct, .first()).

## Regroupement des fonctions similaires

### OHLCV (Minute, Hourly, Daily)
- `get_last_ohlcv_minute_by_pair_id`
- `get_last_ohlcv_hourly_by_pair_id`
- `get_last_ohlcv_daily_by_pair_id`

**Pattern** :
- Filtrage sur `trading_pair_id`
- Tri décroissant sur la date
- Sélection du dernier enregistrement avec `.first()`

### Historique OHLCV CSV
- `get_pairs_and_timeframes_from_historical_data` : jointure multiple, distinct, retourne toutes les paires et timeframes disponibles.
- `get_historical_ohlcv_by_pair_id_and_timeframe` : jointure, filtrage sur pair et timeframe.

### Currencies
- `get_currency_by_name` : filtrage sur le nom, `.first()`
- `get_currency_by_symbol` : filtrage sur le symbole, `.first()`

### TradingPair
- `get_trading_pair_by_currencies` : filtrage sur base et quote, `.first()`

### Crypto CSV
- `search_crypto_csvs_by_trading_pair_and_timeframe` : filtrage sur pair, recherche partielle sur timeframe avec `.ilike`

### Exchanges
- `get_exchange_by_name` : filtrage sur le nom, `.first()`

## Optimisations appliquées

- Utilisation systématique de `.first()` pour limiter la récupération à un seul objet lorsque pertinent.
- Filtrage précis pour éviter le chargement de données inutiles.
- Jointures explicites pour accéder aux données liées sans requêtes multiples.
- Utilisation de `.distinct()` pour éviter les doublons lors des jointures.
- Recherche partielle avec `.ilike` pour plus de flexibilité utilisateur.

## Bonnes pratiques

- Toujours filtrer sur les identifiants ou champs uniques pour optimiser la performance.
- Privilégier `.first()` ou `.limit()` pour éviter de charger des listes complètes si un seul résultat est attendu.
- Utiliser des jointures pour accéder aux données liées en une seule requête.
- Documenter chaque fonction pour expliciter le filtrage, la jointure et l’optimisation réalisée.

---

Pour plus de détails, se référer aux docstrings harmonisés dans chaque fichier du dossier.
