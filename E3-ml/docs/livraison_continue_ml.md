# Chaîne de Livraison Continue Modèles ML (Compétence C13)

## Objectif
Mettre en place une chaîne de livraison continue (approche MLOps) pour le dossier `E3-ml`, automatisant tests, entraînement, validation basique et packaging des modèles (sérialisation), puis création d’une Pull Request de release.

---
## 1. Contexte & Périmètre
La pipeline s’applique aux modèles de prévision crypto. Le script principal d’entraînement/forecast est `update_models_and_forecasts.py` (argument `--granularity hour|day`). Les tests existent sous `src/C12_tests` et couvrent API, app et logique ML.

---
## 2. Fichiers de configuration
| Fichier | Rôle |
|---------|------|
| `.github/workflows/e3-ml-cd.yml` | Pipeline CI/CD ML |
| `E3-ml/update_models_and_forecasts.py` | Orchestrateur entraînement + prévision + sauvegarde |
| `E3-ml/requirements.txt` | Dépendances ML / API |
| `E3-ml/src/C12_tests/**` | Tests unitaires et intégration |
| `E3-ml/models/**` | Sortie des modèles sérialisés (par granularité) |

Tous sont versionnés dans le dépôt distant.

---
## 3. Déclencheurs
- `push` modifiant `E3-ml/**` ou le workflow.
- `workflow_dispatch` (exécution manuelle).

---
## 4. Étapes de la chaîne
1. Checkout.
2. Installation Python 3.11 + cache pip.
3. Installation dépendances + libs système (ex: `libgomp1` pour Darts / Torch backend si requis).
4. Exécution des tests (tous répertoires C12_tests). Échec = arrêt.
5. Couverture (facultative) exportée en artefact.
6. Entraînement + génération de prévisions pour chaque granularité du matrix (`hour` puis `day`).
7. Sauvegarde des modèles sérialisés (fichiers `.pkl`) déjà orchestrée par le script.
8. Publication des répertoires `models/hour_models` et `models/day_models` comme artefacts.
9. Si branche `dev` → création d’une Pull Request de release vers `main`.

---
## 5. Détails du workflow `e3-ml-cd.yml`
Points importants :
- Stratégie matrix sur `granularity` pour réutiliser pipeline.
- Variables `PYTHONPATH` positionnées (tests importent modules sous `src`).
- Packaging = artefacts modèles ; déploiement logique = mise à disposition via PR.
- Release PR: branche éphémère `release/e3-ml-dev-to-main`.

---
## 6. Tests intégrés
- Tests de données & structure: via suites `unit/` et `integration/` dans `src/C12_tests`.
- Pour ajouter un test: créer fichier `test_*.py` dans la hiérarchie correspondante.
- Commande locale :
```
cd E3-ml
pytest -q
```

---
## 7. Entraînement & Validation du modèle
Le script `update_models_and_forecasts.py`:
1. Initialise les forecasters (`initialize_pair_forecasters_by_granularity`).
2. Monitor training (`monitor_trainings`) pour collecte métriques.
3. Entraîne et produit des prévisions (`make_forecasts`).
4. Sauvegarde prévisions en base (simulation / opération réelle selon config).
5. Sérialise les modèles (`save_forecasters_models`).

Validation implicite: 
- Si une étape échoue (exception non gérée), le job échoue → pas de PR.
- Possibilité d’étendre avec un script d’évaluation (ex: seuil de MAPE) et `exit 1` si non conforme (amélioration future section 12).

---
## 8. Artefacts produits
| Artefact | Contenu |
|----------|---------|
| `e3-ml-coverage-<granularity>` | Rapport couverture XML |
| `models-<granularity>` | Répertoire des modèles sérialisés pour la granularité |

Téléchargeables depuis l’onglet Actions après exécution.

---
## 9. Exécution locale complète
```
cd E3-ml
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python update_models_and_forecasts.py --granularity hour
python update_models_and_forecasts.py --granularity day
```
Modèles générés dans `models/hour_models` et `models/day_models`.

---
## 10. Dépannage
| Problème | Cause possible | Piste |
|----------|----------------|-------|
| Module introuvable | PYTHONPATH absent | Exporter `PYTHONPATH=./src` |
| Erreur dépendance Torch/Darts | Lib système manquante | Installer `libgomp1` (déjà dans workflow) |
| Artefact vide | Entraînement non exécuté | Vérifier logs étapes training |
| PR non créée | Branche ≠ dev | Lancer depuis `dev` ou déclencheur manuel |

---
## 11. Accessibilité du document
- Titres hiérarchisés.
- Listes / tableaux pour structurer.
- Pas de code couleur seul.
- Phrases concises.