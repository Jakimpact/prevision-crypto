# Documentation Applicative – Plateforme de prévision crypto (E4)

## Objectif
Ce document atteste que l'application Flask (dossier `E4-app`) respecte les spécifications fonctionnelles et techniques définies dans le cadre du projet et fournit les informations nécessaires à sa prise en main, à son exploitation et à son maintien. Le format est structuré, lisible, et suit des recommandations d’accessibilité (titres hiérarchisés, listes, phrases courtes, absence de couleurs dépendantes pour le sens, langage clair).

---
## 1. Conformité de l’environnement de développement
- Le projet cible Python 3.11+ (voir `requirements.txt`).
- Les dépendances installées couvrent Flask, monitoring, appels API, gestion JWT, tests (`pytest`, `pytest-cov`).
- Le chargement des variables d’environnement se fait via `.env` (lib `python-dotenv`).
- L’architecture correspond aux spécifications : séparation claire `services/`, `utils/`, `templates/`, `tests/`, `docs/`.
- Le pipeline CI (GitHub Actions – fichier `.github/workflows/tests.yml`) exécute automatiquement les tests.

Conclusion : L’environnement de développement respecte les spécifications techniques.

---
## 2. Interfaces utilisateur et conformité aux maquettes
- Pages principales : `index` (connexion), `register` (inscription), `dashboard`, `forecast`, `charts`.
- Les templates dans `templates/` structurent l’héritage (`base.html`) et les vues fonctionnelles (`dashboard.html`, `forecast.html`, etc.).
- Les formulaires (login, register, forecast) appliquent des validations côté serveur (champs requis, longueur minimale mot de passe, horizon de prévision borné).
- L’agencement et la navigation respectent les flux prévus (connexion → dashboard → fonctionnalités). 

Conclusion : Les interfaces sont intégrées et respectent les maquettes et comportements fonctionnels (navigation, validations basiques, messages flash).

---
## 3. Comportements des composants d’interface / Navigation
- Validation des formulaires : 
  - Connexion / inscription : champs requis, longueur minimale.
  - Prévision : vérification cohérence `pair / granularity / horizon` via le service métier (refus si paramètres hors plage).
- Messages utilisateurs : utilisation des `flash()` pour retour d’état (succès / erreur / avertissement).
- Protection des routes : décorateur `@require_valid_token` (redirection ou JSON 401 pour /api/).
- Navigation logique :
  - Utilisateur non connecté redirigé vers `/`.
  - Utilisateur connecté se voit refuser les accès si token expiré (nettoyage session).

Conclusion : Les comportements d’interface et la navigation suivent les spécifications fonctionnelles.

---
## 4. Composants métier
Principaux services :
- `services/auth.py` : Authentification / inscription via API E1.
- `services/forecast.py` : Obtention d’un token E3 et récupération des prévisions.
- `services/ohlcv.py` : Récupération et formatage des données OHLCV et prévisions historiques / futures.
- `utils/auth.py` : Gestion session, validation / décodage basique JWT, décorateur d’accès.
- `utils/datetime.py` : Conversion et formatage des dates (UTC → Europe/Paris).
- `utils/alerts.py` : Détection des dépassements de latence et émission d’alertes JSONL.
- `utils/logger.py` : Journalisation centralisée avec rotation.

Tests associés (voir section 9) confirment la logique métier essentielle (validation des paramètres, formatage des données, calcul de variation de prix, gestion d’accès).

Conclusion : Les composants métier sont développés et fonctionnels conformément aux spécifications.

---
## 5. Gestion des droits d’accès
- Contrôle d’accès basé sur la session (présence et validité temporelle d’un JWT stocké).
- Décorateur `@require_valid_token` :
  - Pour les routes Web → redirection + message flash.
  - Pour les endpoints API (`/api/…`) → réponse JSON `{error: ...}` avec code 401.
- Invalidation automatique de la session si token expiré ou corrompu (`check_token_validity`).
- Stockage minimal en session : `user_id`, `username`, `access_token`, `token_type`, `user_role`.

Conclusion : La gestion des droits correspond aux exigences fonctionnelles (protection des vues et API, session nettoyée si invalide).

---
## 6. Flux de données
- Flux E1 : authentification / inscription / récupération des paires, OHLCV, prévisions persistées.
- Flux E3 : obtention de prévisions en direct (modèles IA) après authentification technique.
- Formatage des données graphiques : normalisation + conversion timezone (`format_chart_data`).
- Alerte latence : mesures sur appels critiques (`forecast`, `chart-data`) → déclenchement éventuel d’alertes (fichier `logs/alerts.jsonl`).

Conclusion : Les flux de données respectent les spécifications techniques et fonctionnelles (séparation historique vs prévisions, validation paramètres, métriques de performance basiques).

---
## 7. Éco‑conception
Pratiques mises en œuvre :
- Pas de dépendances lourdes inutiles (librairies ciblées).
- Réutilisation de conversions de dates simples (pas de sur-traitement côté client).
- Limitation des logs verbeux en production (niveau configurable via variables env → réduction I/O disque).
- Fichiers de logs avec rotation (évite croissance illimitée).
- Possibilité future : cache léger ou pagination (ajoutable) – laissé en amélioration.

Conclusion : Les choix actuels suivent des recommandations d’éco‑conception basiques (sobriété dépendances, limitation I/O, structure claire). 

---
## 8. Sécurité – Alignement OWASP Top 10 (principaux points)
| Aspect | Implémentation / Remarque |
|--------|---------------------------|
| Broken Access Control | Décorateur d’accès, nettoyage session si token invalide. |
| Cryptographic Failures | JWT décodé sans signature (contrainte projet) – À renforcer (vérif. signature) en production réelle. |
| Injection | Entrées utilisateur nettoyées côté serveur, pas d’assemblage SQL direct (toutes données passent par APIs). |
| Insecure Design | Séparation claire services / utils, étapes de validation centralisées. |
| Security Misconfiguration | Variables d’environnement externalisées; rotation des logs; DEBUG contrôlé. |
| Vulnerable Components | Versions épinglées dans `requirements.txt`. |
| Identification & Auth | Flux d’auth centralisé via API E1 + gestion session. |
| Logging & Monitoring | Journalisation centralisée + métriques latence + alertes JSONL. |
| SSRF / XSS | Pas d’injection dynamique non échappée dans les templates (Flask auto-escape). |
| Data Integrity | Manipulation lecture seule côté client; pas de stockage local non chiffré. |

Améliorations futures possibles : vérification signature JWT, rate limiting, Content Security Policy renforcée.

Conclusion : Les préconisations OWASP critiques applicables au périmètre sont prises en compte dans la mesure des contraintes du projet.

---
## 9. Tests (unitaires et intégration)
- Répertoires : `tests/unit/` et `tests/integration/`.
- Couverture ciblée :
  - Métier : validation des paramètres de prévision, formatage des données OHLCV/prévisions, calcul variations.
  - Accès : authentification simulée, contrôle d’accès des routes protégées, réponses API sans token.
  - Routes critiques : `/forecast`, `/api/chart-data`, `/dashboard`.
- Lancement : `pytest -q` ou `python run_tests.py` (script simple).
- CI : exécution automatique sur push / PR (workflow GitHub Actions).

Conclusion : Les composants métier et la gestion des accès sont couverts comme exigé.

---
## 10. Versionnement & Dépôt Git
- Dépôt Git distant (GitHub) avec branche `E4` active.
- Fichiers de configuration CI présents.
- Historique permettant le suivi incrémental des ajouts (tests, docs, services).

Conclusion : Les sources sont versionnées et accessibles.

---
## 11. Architecture applicative (vue synthétique)
```
E4-app/
  app.py                # Point d’entrée Flask
  config.py             # Configuration (URLs, logging, seuils latence)
  services/             # Clients externes (auth, forecast, ohlcv)
  utils/                # Auth, dates, logger, alertes
  templates/            # Interfaces HTML
  logs/                 # Journaux + alertes JSONL
  tests/                # Unit & Integration
  docs/                 # Documentation
  requirements.txt      # Dépendances
```
Flux principal : Utilisateur → (auth) → dashboard → (forecast / chart-data) → services (E1 / E3) → résultats formatés → interface.

---
## 12. Installation & Exécution
### Prérequis
- Python 3.11+
- Git

### Étapes
1. Cloner le dépôt.
2. Créer un environnement virtuel.
3. Installer les dépendances.
4. Configurer le fichier `.env`.
5. Lancer l’application.

### Exemple (PowerShell Windows)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# Créer .env avec URLs et identifiants API
python app.py
```

### Lancement des tests
```
pytest -q
# ou
python run_tests.py
```

---
## 13. Dépendances principales
| Package | Rôle |
|---------|------|
| Flask | Framework web |
| flask-monitoringdashboard | Monitoring applicatif |
| requests | Appels HTTP vers APIs E1 / E3 |
| python-jose | Décodage basique JWT |
| pytz | Gestion des fuseaux horaires |
| pytest / pytest-cov | Tests automatisés |

---
## 14. Accessibilité de la documentation
- Structuration avec titres hiérarchiques (`h1` → `h2` → `h3`).
- Listes à puces pour favoriser la lisibilité.
- Langage clair et concis ; phrases courtes.
- Absence de dépendance aux couleurs pour la compréhension.
- Tableaux avec en-têtes simples.
- Compatible lecteurs d’écran (texte brut Markdown, pas d’images décoratives sans alternative).