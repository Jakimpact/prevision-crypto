# Documentation C5 – API REST

---
## 1. Périmètre général
L’API expose des opérations de lecture (données de marché OHLCV agrégées, prévisions, métadonnées de paires) et d’écriture limitée (création de prévisions) sous préfixe `/api/v1`. Le serveur est déclaré dans `api.py` (FastAPI) avec métadonnées OpenAPI (title, description, version). FastAPI génère automatiquement la spécification OpenAPI consultable via `/docs` (Swagger UI) ou `/redoc`.

---
## 2. Authentification & Autorisation
Mécanisme: JWT Bearer Token.
- Endpoint de récupération du token: `POST /api/v1/login` (OAuth2PasswordRequestForm: fields `username`, `password`).
- Durée de vie: 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Secret & algorithme: variables d’environnement (`API_SECRET_KEY`, `API_ALGORITHM`).
- Injection: dépendance `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")`.
- Décodage: `decode_access_token` (gestion `JWTError`).
- Récupération utilisateur: `get_current_user` (vérification `sub` puis recherche en BD). 
- Autorisation fine:
  - Rôle `script` exigé pour la création de prévisions (`require_role_script`).
  - Rôle basique (ex: `user`) suffisant pour la lecture (trading_pairs, ohlcv, forecast GET).

Codes d’erreur typiques:
- 401: Absence ou invalidité du token.
- 403: Accès interdit (rôle insuffisant) – création de prévisions.
- 404: Utilisateur introuvable.

---
## 3. Standards & Conformité OpenAPI
FastAPI génère automatiquement:
- Schéma OpenAPI JSON: `/openapi.json`.
- Documentation interactive: `/docs` (Swagger) / `/redoc`.
- Déclarations de sécurité: schéma OAuth2 password + bearer token.
Chaque endpoint est documenté via docstring concise (Args / Returns). Le modèle de données renvoyé correspond aux objets ORM sérialisés.

---
## 4. Endpoints (Résumé Fonctionnel)
Préfixe global: `/api/v1`

### 4.1 Authentification
| Méthode | URI | Auth requise | Description | Corps | Réponse (succès) |
|---------|-----|--------------|-------------|-------|------------------|
| POST | `/authentification/login` | Non | Obtenir un JWT | form-data (`username`, `password`) | `{access_token, token_type, role}` |
| POST | `/authentification/register` | Non | Créer un utilisateur (role=user) | JSON `{username, password}` | `{id, username, role}` |

### 4.2 Trading Pairs
| Méthode | URI | Auth | Description | Paramètres | Réponse |
|---------|-----|------|-------------|------------|---------|
| GET | `/trading_pairs/trading_pairs_by_base_currency_symbol/{symbol}` | Oui | Liste des paires dont la base = symbol | path: symbol | Liste JSON (peut être vide) |
| GET | `/trading_pairs/trading_pair_by_currency_symbols/{base_symbol}/{quote_symbol}` | Oui | Paire unique base/quote | path: base_symbol, quote_symbol | Objet JSON ou null |

### 4.3 OHLCV
| Méthode | URI | Auth | Description | Query | Réponse |
|---------|-----|------|-------------|-------|---------|
| GET | `/ohlcv/minute_by_trading_pair_id/{trading_pair_id}` | Oui | OHLCV minute | `start_date` optionnel | Liste JSON |
| GET | `/ohlcv/hourly_by_trading_pair_id/{trading_pair_id}` | Oui | OHLCV horaire | `start_date` optionnel | Liste JSON |
| GET | `/ohlcv/daily_by_trading_pair_id/{trading_pair_id}` | Oui | OHLCV journalier | `start_date` optionnel | Liste JSON |

### 4.4 Forecast
| Méthode | URI | Auth | Description | Query / Corps | Réponse |
|---------|-----|------|-------------|---------------|---------|
| GET | `/forecast/minute_by_trading_pair_id/{trading_pair_id}` | Oui | Prévisions minute | `start_date` optionnel | Liste JSON |
| GET | `/forecast/hourly_by_trading_pair_id/{trading_pair_id}` | Oui | Prévisions horaire | `start_date` optionnel | Liste JSON |
| GET | `/forecast/daily_by_trading_pair_id/{trading_pair_id}` | Oui | Prévisions journalières | `start_date` optionnel | Liste JSON |
| GET | `/forecast/last_minute_by_trading_pair_id/{trading_pair_id}` | Oui | Dernière prévision minute | - | Objet JSON ou null |
| GET | `/forecast/last_hourly_by_trading_pair_id/{trading_pair_id}` | Oui | Dernière prévision horaire | - | Objet JSON ou null |
| GET | `/forecast/last_daily_by_trading_pair_id/{trading_pair_id}` | Oui | Dernière prévision journalière | - | Objet JSON ou null |
| POST | `/forecast/minute` | Oui (rôle=script) | Créer prévision minute | JSON payload | Objet créé |
| POST | `/forecast/hourly` | Oui (rôle=script) | Créer prévision horaire | JSON payload | Objet créé |
| POST | `/forecast/daily` | Oui (rôle=script) | Créer prévision journalière | JSON payload | Objet créé |

Payload prévision attendu (exemple):
```json
{
  "trading_pair_id": 1,
  "date": "2025-01-01T12:00:00",
  "value": 42000.5,
  "model_name": "prophet_v1",
  "model_version": "1.0.0"
}
```

---
## 5. Formats & Sérialisation
Les objets retournés sont des instances ORM converties implicitement en dict via FastAPI. (Amélioration future: schémas Pydantic pour contrôle strict et documentation précise des champs.)

Dates: format ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)

---
## 6. Sécurité & Bonnes Pratiques
- JWT court (30 min) limite risque d’usage détourné.
- Vérification rôle spécifique pour endpoints d’écriture (prévisions) via `require_role_script`.
- Hachage mots de passe avec bcrypt (`passlib` context).
- Aucune donnée personnelle sensible exposée dans les réponses.

Améliorations possibles:
- Refresh token + rotation.
- Limitation de taux (rate limiting) côté reverse proxy.
- Ajout de scopes OAuth2 pour granularité (lecture vs écriture). 

---
## 7. Commandes de démarrage
Exécution locale (exemple):
```
python -m src.C5_api.api
```
Ou avec uvicorn direct:
```
uvicorn src.C5_api.api:app --host 0.0.0.0 --port 8000
```