# Chaîne de Livraison Continue ML (Compétence C13) – Version actuelle (Tests uniquement)

## Objectif
Pipeline CI minimaliste pour le dossier `E3-ml` : exécuter automatiquement les tests et publier un rapport de couverture. Les étapes d'entraînement, de monitoring MLflow, de sauvegarde / packaging modèles et de création de Pull Request de release ont été retirées de ce workflow pour simplifier et éviter les dépendances externes.

---
## 1. Contexte & Périmètre
Le workflow actuel couvre UNIQUEMENT la validation (tests) du code ML, API et utilitaires dans `src/C12_tests`. Le script `update_models_and_forecasts.py` reste utilisable manuellement (hors CI) pour lancer un entraînement.

---
## 2. Fichiers de configuration
| Fichier | Rôle |
|---------|------|
| `.github/workflows/e3-ml-cd.yml` | Workflow CI (tests + couverture uniquement) |
| `E3-ml/update_models_and_forecasts.py` | Orchestrateur (utilisation manuelle locale) |
| `E3-ml/requirements.txt` | Dépendances ML / API |
| `E3-ml/src/C12_tests/**` | Tests unitaires et intégration |
| `E3-ml/models/**` | (Non utilisé par le workflow actuel) |

Tous sont versionnés dans le dépôt distant.

---
## 3. Déclencheurs
- `push` modifiant `E3-ml/**` ou le workflow.
- `workflow_dispatch` (exécution manuelle).

---
## 4. Étapes de la chaîne
1. Checkout.
2. Installation Python 3.11 + cache pip.
3. Installation dépendances + libs système (ex: `libgomp1`).
4. Exécution des tests (arrêt sur échec).
5. Génération & upload du rapport de couverture (`coverage.xml`).

---
## 5. Détails du workflow `e3-ml-cd.yml`
Points importants (version tests only) :
- Un seul job `tests` (plus de matrix par granularité).
- `PYTHONPATH=./src` pour les imports.
- Artefact unique de couverture (`e3-ml-coverage`).
- Aucune interaction réseau (MLflow / API d'entraînement) intégrée dans ce pipeline.

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
## 7. Entraînement & Validation (hors workflow)
Le workflow n’exécute plus l’entraînement. Pour lancer manuellement :
```
cd E3-ml
python update_models_and_forecasts.py --granularity hour
python update_models_and_forecasts.py --granularity day
```
Pour éviter les erreurs MLflow, soit lancer un serveur MLflow, soit définir `MLFLOW_TRACKING_URI=./mlruns` (file store local).

---
## 8. Artefact produit
| Artefact | Contenu |
|----------|---------|
| `e3-ml-coverage` | Rapport de couverture XML (coverage.xml) |

Téléchargeable depuis l’onglet Actions.

---
## 9. Exécution locale complète (tests + entraînement manuel)
```
cd E3-ml
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
# (Optionnel) Entraînement manuel
python update_models_and_forecasts.py --granularity hour
python update_models_and_forecasts.py --granularity day
```
Modèles générés dans `models/hour_models` et `models/day_models`.

---
## 11. Accessibilité du document
- Titres hiérarchisés.
- Listes / tableaux pour structurer.
- Pas de code couleur seul.
- Phrases concises.