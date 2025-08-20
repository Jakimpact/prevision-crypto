# Documentation Monitoring (C11)

## Introduction
Cette documentation décrit le dispositif de monitoring des modèles de prévision (cryptomonnaies) implémenté dans le dossier `C11_monitoring`. Elle précise les métriques suivies, l'outillage (MLflow), le cycle d'exécution et les limites actuelles. 

## Résumé
À chaque exécution du pipeline ML (`update_models_and_forecasts.py`), une étape de monitoring lance l'évaluation rétrospective de chaque forecaster. Les résultats (paramètres + métriques) sont enregistrés via MLflow dans un stockage local et consultables via l'interface `mlflow ui`. Les métriques suivies (MAPE, MAE, direction_accuracy) permettent d'analyser la précision et la capacité directionnelle des modèles par granularité (hour / day).

## 1. Métriques monitorées
- MAPE (Mean Absolute Percentage Error) : mesure l'erreur relative moyenne ; utile pour comparer des séries à échelles différentes.
- MAE (Mean Absolute Error) : erreur absolue moyenne, sensible à la magnitude réelle des prix.
- Direction Accuracy : proportion de prévisions correctement orientées (hausse/baisse) entre deux pas successifs.
Interprétation : plus MAPE/MAE sont faibles, meilleure est la précision ; plus Direction Accuracy est élevée (proche de 1), meilleure est la capacité à anticiper le sens du mouvement.

## 2. Outils et intégration
- Outil principal : MLflow (tracking expérimental).
- API MLflow utilisée via `mlflow.set_tracking_uri`, `set_experiment`, `start_run`, `log_params`, `log_metrics`.

## 3. Vecteurs de restitution des métriques
- Interface : `mlflow ui` (dashboard temps quasi-réel après exécution du script) ; accessible via le navigateur.

## 4. Accessibilité de la restitution
- MLflow offre une interface web lisible avec tableaux et graphiques standards.

## 5. Chaîne d'exécution et sandbox
- Lancement via : `python update_models_and_forecasts.py --granularity hour|day`.
- Enchaînement : initialisation forecasters -> monitoring (évaluation historique) -> entraînement / prévision -> sauvegarde modèles / prévisions.
- Exécution en environnement de développement local (sandbox implicite).

## 6. État de marche
- Les métriques sont effectivement calculées par `test_forecaster_past_performances` puis enregistrées dans MLflow.
- Tagging des runs : symbol, modèle, granularité.
- Paramètres loggés : symbole, granularité, nom et paramètres du modèle, date d'entraînement normalisée (selon hour/day), fenêtre de test.
- Vérification de persistance : runs répertoriés dans le dossier de tracking configuré (`MLSettings.ml_flow_tracking_uri`).

## 7. Procédure d'installation et d'utilisation
### 7.1 Installation
1. Installer les dépendances Python (requirements du module ML).
2. S'assurer que MLflow est installé (`pip install mlflow`).
3. Configurer `MLSettings.ml_flow_tracking_uri` (fichier de settings) vers un répertoire accessible.
### 7.2 Exécution du monitoring
1. Lancer le pipeline : `python update_models_and_forecasts.py --granularity hour` (ou `day`).
2. Démarrer l'interface : `mlflow ui --backend-store-uri <MLSettings.ml_flow_tracking_uri>`.
3. Ouvrir le navigateur à l'URL locale (par défaut http://127.0.0.1:5000).
4. Filtrer par expérience nommée `<SYMBOL>_training_monitoring`.
### 7.3 Lecture des résultats
- Onglet Metrics : comparer MAPE / MAE / direction_accuracy entre runs.
- Onglet Parameters : vérifier cohérence des hyperparamètres.
- Historiser les dates d'entraînement via le run name (`<granularity>_<training_date>`).

## 9. Conformité accessibilité (documentation)
Cette documentation applique une structuration hiérarchique (titres de niveau varié), un langage simple et des listes thématiques. Aucun élément visuel non textuel n'est utilisé (pas d'images donc pas de besoin d'alternative). Les liens cités sont explicites. L'information n'est pas transmise uniquement par la couleur. Cela répond aux recommandations générales (inspiration WCAG 2.1 niveau AA) pour la lisibilité et la navigation assistée.

## 11. Synthèse
Le monitoring repose sur MLflow pour assurer traçabilité, historisation et analyse des performances des modèles de prévision. Les métriques loggées (MAPE, MAE, direction_accuracy) couvrent précision relative, erreur absolue et justesse directionnelle. La structure actuelle sert de base solide pour itérer vers un dispositif plus riche (alertes, dérive, tableaux externes) sans complexité excessive.