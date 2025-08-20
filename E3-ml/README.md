# Dossier E3-ml – Vue d'ensemble

## Résumé
Le dossier **E3-ml** regroupe la couche Machine Learning du projet : préparation des données de features, entraînement, versioning des modèles, génération des prévisions et exposition/utilisation de ces modèles par des services internes (API / application). Ce README fournit une entrée rapide et renvoie vers les documentations spécialisées situées dans `docs/`.

## Objectifs principaux
- Centraliser la logique de modélisation (jour / heure / autres horizons).
- Standardiser l'entraînement et la mise à jour automatique des modèles (script `update_models_and_forecasts.py`).
- Gérer le suivi des expériences et artefacts (répertoire `mlruns/` – MLflow).
- Produire des prévisions exploitables pour l'application et les dashboards.
- Assurer la qualité par des tests dédiés et une intégration continue.

## Structure simplifiée
- `update_models_and_forecasts.py` : Script d'automatisation (rafraîchissement modèles + prédictions).
- `main.py` : Point d'entrée éventuel (exécution générale / orchestration).
- `config/` : Paramètres (données, modèles journaliers, horaires, pipeline global).
- `models/` : Modèles produits (exportés / sérialisés).
- `mlruns/` : Tracking des expériences (MLflow).
- `src/` : Code source (sous-modules data, model, API interne, app, tests, utils, monitoring...).
- `docs/` : Documentation détaillée (voir liens ci-dessous).

## Flux ML (haut niveau)
1. Chargement des données (provenant de `E1-data` ou sources dérivées).
2. Pré-traitements / feature engineering.
3. Entraînement et validation (journalisation MLflow).
4. Sélection / enregistrement des modèles.
5. Génération et stockage des prévisions.
6. Mise à disposition pour l'API ou l'application.

## Références vers les documentations détaillées
Utiliser les liens explicites :
- [Documentation du pipeline ML](docs/pipeline_ml_documentation.md)
- [Documentation applicative interne (composants / structure)](docs/app_documentation.md)
- [Documentation API (exposition et intégration)](docs/api_documentation.md)
- [Documentation Monitoring (métriques / supervision)](docs/monitoring_documentation.md)
- [Documentation Livraison Continue ML (CI/CD, déploiement)](docs/livraison_continue_documentation.md)
- [Documentation Tests (stratégie, types, couverture)](docs/tests_documentation.md)

## Données consommées / produites
- Entrées : séries temporelles cryptos (OHLCV, dérivés) issues de `E1-data`.
- Sorties : artefacts modèles (fichiers sérialisés), prévisions chiffrées, métriques d'évaluation.
- Pas de données personnelles traitées.

## Outils et dépendances clés (attendu)
- MLflow (tracking expériences).
- pandas / numpy / bibliothèques ML (dépendances exactes : voir `requirements.txt`).
- Scripts orchestrateurs (cron / pipeline CI) côté infrastructure (non décrit ici si absent).

## Qualité / Fiabilité
- Tests dédiés dans `src/C12_tests/` (à compléter / étendre si nécessaire).
- Recommandé : ajouter validation automatique des performances minimales avant promotion d'un modèle.

## Accessibilité documentaire
- Titres hiérarchisés et langage direct.
- Liens explicites (pas de "cliquez ici").
- Aucun contenu qui repose uniquement sur la couleur.

## Révision
- Version : 1.0

Pour approfondir un sujet précis, consulter les documents de la section "Références".
