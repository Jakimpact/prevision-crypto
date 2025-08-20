# Documentation de l'API de Prévision (C9)

## Introduction
Cette documentation décrit l'API REST exposant les modèles de prévision de cours de cryptomonnaies. Elle suit le parcours logique des points de terminaison réellement présents dans le code (`login`, `forecast_hourly`, `forecast_daily`). Elle couvre l'authentification, les usages, et les aspects de sécurité implémentés. 

## Résumé
L'API fournit un mécanisme d'authentification par jeton (JWT), puis expose deux points de prévision (horaire et journalier) protégés. Les modèles sont chargés dynamiquement depuis des fichiers sérialisés et exécutent des prévisions contrôlées en nombre de pas. 

---
## 1. Accès et authentification
- Méthode : OAuth2 Password Flow simplifié avec un mot de passe statique vérifié côté serveur (`verify_password`).
- Obtention du token : POST `/api/v1/authentification/login` (form-data: username, password). Le mot de passe valide retourne un access token JWT.
- Utilisation : Inclure `Authorization: Bearer <token>` dans les requêtes protégées.
- Expiration : 30 minutes (valeur par défaut dans `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Décodage : réalisé via `decode_access_token`, échec => 401.

## 2. Points de terminaison
### 2.1 Authentification
POST `/api/v1/authentification/login`
- Corps (form-data OAuth2): `username`, `password`.
- Réponse : `{ access_token, token_type }`.
- Erreurs : 401 si mot de passe incorrect.

### 2.2 Prévision horaire
POST `/api/v1/forecast/forecast_hourly`
- Corps JSON :
```json
{
  "trading_pair_symbol": "BTC-USD",
  "num_pred": 12
}
```
- Règles : `num_pred` ∈ [1,24].
- Réponse : symbole, nombre de pas, liste des valeurs prédites, liste des dates.
- Sécurité : nécessite un jeton JWT valide.
- Erreurs : 400/422 si `num_pred` hors bornes, 401 si auth invalide.

### 2.3 Prévision journalière
POST `/api/v1/forecast/forecast_daily`
- Corps JSON :
```json
{
  "trading_pair_symbol": "BTC-USD",
  "num_pred": 5
}
```
- Règles : `num_pred` ∈ [1,7].
- Réponse : identique au point précédent.
- Sécurité : JWT requis.

## 3. Modèles et chargement
- Fonction utilisée : `load_model(model_name, granularity)`.
- Stockage : fichiers pickle dans un répertoire structuré par granularité (`hour_models`, `day_models`).
- Gestion d'erreurs : `FileNotFoundError` si le modèle demandé n'existe pas.

## 4. Sécurité (OWASP / bonnes pratiques)
Implémenté :
- Authentification par jeton (contrôle d'accès basique) et endpoints de prévision protégés.
- API non exposée publiquement : usage prévu uniquement par des applications internes/contrôlées, réduisant la surface d'attaque.
- Limitation fonctionnelle des entrées (`num_pred` borné) pour réduire les abus (prévention de charge excessive / injection de paramètres).
- Gestion des codes d'erreur HTTP explicites (401 pour credentials invalides, 422 pour validation Pydantic).
- Validation des schémas via Pydantic (réduit les risques d'injection et de type confusion).

## 5. Tests
La suite de tests est organisée en deux volets : unitaires (authentification et prévision) et intégration.

### 5.1 Tests unitaires Authentication (`test_api_auth.py`)
Cas couverts :
- Connexion réussie (retour token JWT et type bearer)
- Mot de passe invalide (401 + message `Incorrect password`)
- Absence totale de credentials (422)
- Username sans mot de passe (422)
Ces tests valident la robustesse de la validation d'entrée et la génération du token.

### 5.2 Tests unitaires Forecast (`test_api_forecast.py`)
Cas couverts :
- Prévision horaire et journalière réussies (mock du modèle, vérification structure réponse)
- Limites invalides : `num_pred` > bornes (24 / 7) et `num_pred` = 0 (exception attendue)
- Appels non authentifiés (401)
- Payload invalide (champ manquant) et payload vide (422)
Ils garantissent la validation des paramètres, le contrôle d'accès et la cohérence de la réponse.

### 5.3 Tests d'intégration (`test_api_integration.py`)
Cas couverts :
- Démarrage de l'application (accessibilité `/docs`)
- Workflow complet : login -> appel prévision avec token valide
- Accès à la documentation OpenAPI (`/openapi.json`, `/docs`, `/redoc`)
- Vérification basique des headers (CORS potentiel)

### 5.4 Interprétation
Les tests confirment :
- L'authentification protège effectivement les endpoints sensibles.
- Les contrôles de bornes sur `num_pred` empêchent des usages abusifs.
- Les schémas de réponse respectent le contrat fonctionnel (structure prévisions + dates).
- Les erreurs renvoient des statuts HTTP adaptés (401, 422).

## 6. Conformité documentation / standards
- Architecture REST respectée (ressources + actions POST).
- Description OpenAPI générée automatiquement par FastAPI (schéma interactif disponible via `/docs`).
- Documentation formelle fournie dans ce fichier.
- Standard supplémentaire (ex: versionnage d'API) : préfixe `/api/v1` utilisé.

## 7. Règles d'autorisation
- Accès libre uniquement pour `/authentification/login`.
- Accès protégé pour tous les endpoints de prévision via dépendance `get_current_user` (vérification token OAuth2 Bearer).
- Rôles / permissions avancés : Pas d'informations concernant ce point.

## 8. Accessibilité
La documentation applique une structure hiérarchique claire (titres gradués), un langage simple et explicite, l'usage de listes uniquement lorsque nécessaire, et des blocs de code formatés pour faciliter la lecture assistée. Aucun contenu visuel non textuel n'est utilisé (pas d'images, donc pas de besoin d'alternative). Les endpoints sont nommés de manière descriptive, évitant les formulations ambiguës.