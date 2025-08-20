# Documentation du pipeline de modèles de prévision (C9_model)

Ce document décrit le pipeline exécuté par `update_models_and_forecasts.py`. Il suit l'ordre logique d'exécution et se limite strictement aux fonctions effectivement utilisées.

## Vue d'ensemble
Le pipeline ML automatise :
1. L'initialisation des forecasters pour chaque paire et granularité (`initialize_pair_forecasters_by_granularity`).
2. L'entraînement incrémental des modèles et la génération de prévisions (`make_forecasts`).
3. La sauvegarde des prévisions en base via l'API E1 (`save_forecasts_to_db`).
4. La sauvegarde des artefacts modèles sur disque (`save_forecasters_models`).
5. Le monitoring des performances à l'entraînement (`monitor_trainings`).

Chaque étape est journalisée via `logger` pour assurer traçabilité et supervision.

## 1. Initialisation des forecasters
Fonction appelée : `initialize_pair_forecasters_by_granularity(granularity)` (fichier `initiate_forecaster.py`).

Objectif : préparer une liste de forecasters prêts à être entraînés pour la granularité choisie (`hour` ou `day`).

Étapes :
- Sélection du jeu de configuration (`HourModelsSettings.pair_models` ou `DayModelsSettings.pair_models`).
- Instanciation d'un `TradingPairForecaster` par paire.
- Récupération des données historiques via `get_data_for_pair_forecaster` (module data faisant appel à l'API de E1).
- Tri et indexation temporelle (`date` en index).
- Transformation en objet `TimeSeries` (Darts) via `time_series_transformation_steps` :
  - Suppression de la colonne `trading_pair_id` (non utile pour l'apprentissage).
  - Construction `TimeSeries.from_dataframe` avec la fréquence cible.
  - Remplissage automatique des valeurs manquantes (`fill_missing_values`).

Résultat : une liste d'objets forecasters contenant : dataframe historique, série temporelle normalisée, fréquence, identités de paire.

## 2. Génération des prévisions
Fonction appelée : `make_forecasts(pair_forecasters)` (fichier `predict_model.py`).

Logique : pour chaque forecaster :
- Récupération de la dernière date historique disponible.
- Lecture éventuelle de la dernière prévision enregistrée (`get_last_forecast_for_pair_forecaster`).
- Deux cas :
  - Aucun historique de prévision : entraînement initial puis première prédiction (1 pas de temps).
  - Historique existant : boucle incrémentale jusqu'à rattraper la dernière date historique.

Détails techniques :
- Entraînement réalisé par `train_model(model, ts, freq, training_end)` :
  - Ajustement de la borne de fin (exclusion).
  - Sélection de la cible : série `close`.
  - `model.fit` sur la fenêtre historique.
- Prédiction unitaire : `model.predict(1)` (stratégie pas-à-pas pour cohérence et recalibrage continu).
- Ajout des prévisions dans la structure interne via `forecaster.add_forecast_to_df`.

Avantage : approche incrémentale limitant la dérive et exploitant toute nouvelle donnée au fil de l'eau.

## 3. Sauvegarde des prévisions
Fonction appelée : `save_forecasts_to_db(pair_forecasters)` (fichier `send_data.py`).

Mécanisme :
- Récupération d'un token JWT (`get_jwt_token`).
- Pour chaque prévision courante : envoi POST vers l'API E1 (`post_data`).
- Payload : identifiant de la paire, date, valeur prédite.
- Gestion simple d'erreur HTTP (affichage code et message si != 200).

Objectif : rendre les prévisions disponibles pour consultation / exploitation.

## 4. Sauvegarde des modèles
Fonction appelée : `save_forecasters_models(pair_forecasters, granularity)` (fichier `save_model.py`).

Étapes :
- Construction du répertoire cible : `<models_dir_path>/<granularity>_models`.
- Création du dossier si nécessaire.
- Sauvegarde sérialisée de chaque modèle (`model_instance.save`).

But : persistance des artefacts pour réutilisation (inférence future, audit, versionning).

## 5. Monitoring des entraînements
Fonction appelée : `monitor_trainings(pair_forecasters, granularity)` (fichier `monitor_training.py`).

Rôle : suivre l'exécution et collecter des métriques (ex : erreurs de prévision à l'entraînement). Les détails internes ne sont pas redéveloppés ici mais l'appel garantit l'intégration monitoring dans le pipeline.

## Orchestration : `update_models_and_forecasts.py`

Séquence :
1. Parsing argument `--granularity`.
2. Initialisation des forecasters.
3. Monitoring des phases d'entraînement.
4. Entraînement + prévisions incrémentales.
5. Sauvegarde des prévisions en base.
6. Sauvegarde des modèles.
7. Journalisation de fin.

Robustesse assurée par : modularité, journalisation, exécution séquentielle contrôlée.

## Résumé
Le pipeline met en œuvre une chaîne reproductible : préparation des données, construction des séries temporelles, entraînement adaptatif, génération de prévisions, publication et persistance des modèles. Chaque composant est isolé, testable et substituable.
