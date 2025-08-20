 # Prévision Crypto

## Objectif du projet
Ce dépôt fournit une plateforme complète de collecte, préparation, modélisation et exposition de données liées aux crypto‑actifs (ex: Bitcoin, Ethereum). L'objectif principal est de construire une chaîne cohérente allant de l'extraction brute des données marché jusqu'à la génération de prévisions exploitables via une application web et des services internes.

## Architecture fonctionnelle (4 couches principales)
Le projet est structuré en quatre domaines (dossiers racines) reflétant une séparation de responsabilités claire :

| Couche | Dossier | Rôle principal |
|--------|---------|----------------|
| Données fondamentales | `E1-data` | Extraction, validation, stockage (SQLite), requêtes & agrégations de base. |
| Veille & Services externes | `E2-veille` | Intégration de services tiers (ex: Token Metrics – Trading Signals) et expérimentations de connecteurs. |
| Machine Learning | `E3-ml` | Entraînement, versioning (MLflow), mise à jour automatisée des modèles, génération de prévisions. |
| Application & Exposition | `E4-app` | Application Flask, services d'accès (auth, forecast, ohlcv), dashboards, monitoring et tests. |

Chaque dossier possède sa propre documentation détaillée (README + docs spécialisés) pour favoriser l'évolutivité et l'onboarding.

## Documentation par domaine
Accéder aux points d'entrée de chaque couche :
- [README E1-data](E1-data/README.md) – Base de données & ingestion.
- [README E2-veille](E2-veille/README.md) – Connecteurs externes & scripts de démonstration.
- [README E3-ml](E3-ml/README.md) – Pipeline Machine Learning & modèles.
- [README E4-app](E4-app/README.md) – Application web & services.

## Composants clés
- Scripts d'initialisation et mise à jour OHLCV : `E1-data/init_db_and_data.py`, `E1-data/update_ohlcv.py`.
- Intégration API externe Token Metrics : `E2-veille/parametrage.py`.
- Pipeline ML automatisé : `E3-ml/update_models_and_forecasts.py`.
- Application Flask : `E4-app/app.py`.
- Tests (unitaires / intégration) : `E4-app/tests/`, `E3-ml/src/C12_tests/`.
- Tracking expériences : `E3-ml/mlruns/` (MLflow).

## Gestion des secrets
- Clés API et paramètres sensibles stockés dans des fichiers `.env` (non commit).

## Qualité & Tests
- Tests ML (E3-ml) : validation cohérence modèle & métriques minimales.
- Tests d'application web (E4-app) : vérification des routes et services.

## Monitoring (état actuel)
- Dashboard MLflow pour le pipeline de machine learning.
- Logs applicatifs (`E4-app/logs/`).
- Tableau de bord interne Flask Monitoring Dashboard.

## Démarrage rapide (vue globale)
1. Cloner le dépôt.
2. Créer un environnement Python.
3. Installer les dépendances pour l'ensemble du projet (`pip install -r requirements.txt`) par domaine (ex: `pip install -r E1-data/requirements.txt`, etc.).
4. Renseigner les fichiers `.env` nécessaires (API / config service).
5. Initialiser les données de base : `python E1-data/init_db_and_data.py`.
6. Mettre à jour / enrichir : `python E1-data/update_ohlcv.py`.
8. Lancer pipeline ML pour initialisation des modèles : `python E3-ml/update_models_and_forecasts.py` (lancer l'API E1 auparavant).
7. Lancer l'app : `python E4-app/app.py` (lancer les API E1 et E3 pour accès aux fonctionnalités).

## 🗺️ Schéma conceptuel (résumé textuel)
```
[Sources externes] -> [E1-data Ingestion] -> [Base locale / vues] -> [E3-ml Features] -> [Modèles & Prévisions] -> [E4-app Services & UI]
									^                                      |
									|-----------[E2-veille Signaux]---------|
```

## ♿ Accessibilité documentaire
- Usage de titres hiérarchiques, langage clair, liens explicites.
- Pas de dépendance exclusive à la couleur pour transmettre une information.
- Diagrammes fournis avec description textuelle lorsqu'employés.

## 🛡️ Sécurité (principes de base)
- Isolation des secrets (.env), pas de commit de clés.
- Validation simple des entrées (à renforcer).

## 📝 Licence
Voir le fichier `LICENSE` à la racine.

## Révision
- Version : 1.0