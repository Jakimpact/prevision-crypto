# Documentation Tests (C12)

## Introduction
Cette documentation présente la stratégie de tests automatisés du projet pour la compétence C12. Elle couvre la structure, les types de tests (unitaires / intégration), les outils employés, l'exécution, la portée fonctionnelle et les bonnes pratiques adoptées. 

## Résumé
Les tests sont organisés par domaine (API, Application, Pipeline ML) et par niveau (unitaire vs intégration). Ils valident : authentification, prévisions, logique d'interface, transformation et validation des données, entraînement, évaluation et prédiction des modèles. L'exécution est centralisée via un script (`run_tests.py`) permettant la sélection ciblée des suites. Les outils principaux sont `pytest`, `unittest.mock`, et des fixtures spécialisées pour isoler les dépendances.

## 1. Cas à tester : périmètre et stratégie
- Domaine API : endpoints d'authentification et de prévision. Stratégie : tests unitaires (réponses, erreurs, sécurité) + intégration (workflow login -> forecast, accessibilité documentation).
- Domaine Application (Streamlit) : fonctions utilitaires (JWT, forecast), logique de sélection, workflows complets. Stratégie : mocks HTTP, vérification des paramètres transmis et gestion erreurs.
- Domaine ML : validation des données OHLCV, entraînement (structure temporelle, paramètres), évaluation (métriques MAPE/MAE/direction), prédiction (horizon, continuité), pipeline complet. Stratégie : génération de données synthétiques cohérentes + isolation des modèles via mocks.
- Gestion des erreurs : tests dédiés aux exceptions (ValueError, HTTPError, 401/422 API) et scénarios de récupération.
- Tests de résilience : multiples appels forecast sur même token, récupération après échec API, validation des limites des hyperparamètres.

## 2. Outils de test
- Framework : `pytest` (marqueurs : unit, integration, api, app, ml).
- Mocking : `unittest.mock.patch`, `MagicMock` (modèles, TimeSeries, requêtes externes).
- Configuration : `pytest.ini` (variables d'environnement, options), `conftest.py` (fixtures globales + spécifiques). 
- Exécution orchestrée : `run_tests.py` (sélection par domaine et niveau).

## 3. Intégration et couverture
- Organisation par dossiers : `api/`, `app/`, `ml/` avec sous-dossiers `unit/` et `integration/`.
- Couverture fonctionnelle : authentification, prévision, composants & workflows Streamlit, validation / entraînement / évaluation / prédiction ML et pipeline bout‑en‑bout.
- Couverture chiffrée ("couverture souhaitée" réaliste basée sur l'existant) :
	- Global (lignes) ≥ 50 % (atteint)
	- Domaine API (auth + deps) ≥ 80 % (atteint)
	- Domaine ML cœur (initiation / prédiction / évaluation) ≥ 60 % (atteint)
	- Modules secondaires (I/O data, sauvegarde modèle, utilitaires génériques) : hors seuils contraignants dans cette phase (priorité fonctionnelle démonstration)
	- Exclusions des objectifs : fichiers d'initialisation `__init__.py`, configuration (`settings.py`, `config/`), script `run_tests.py`, répertoire de tests, caches.
- Justification : priorisation sur couches métier critiques (sécurité + pipeline prévision) sans ajouter de nouveaux tests.

Snapshot de référence (exécution locale) : total global 52 % avec pics élevés sur `auth.py` (90 %) et `deps.py` (82 %), ML cœur entre 63 % et 71 %, couches utilitaires plus faibles (choix assumé).

## 4. Exécution des tests
### Script dédié
```bash
python src/C12_tests/run_tests.py              # Tous les tests
python src/C12_tests/run_tests.py --api --unit # Sous-ensemble ciblé
python src/C12_tests/run_tests.py --ml --integration
```
### Pytest direct
```bash
pytest src/C12_tests -v
pytest src/C12_tests/api -m unit -v
pytest src/C12_tests/ml -m integration -v
```
### Calcul de couverture
Outil : `pytest-cov` (activable via script).

1. Installation (dépendance déjà listée) :
	```bash
	pip install -r requirements.txt
	```
2. Exécution globale avec couverture :
	```bash
	python src/C12_tests/run_tests.py --coverage
	```
3. Exécution ciblée (ex: tests ML uniquement avec couverture) :
	```bash
	python src/C12_tests/run_tests.py --ml --coverage
	```
4. Analyse :
	- Terminal : pourcentage global + fichiers et lignes manquantes (option `term-missing`).
	- Les seuils peuvent être appliqués :
	```bash
	python src/C12_tests/run_tests.py --coverage --fail-under 50
	```
5. Exclusions & règles : définies dans `.coveragerc` (sources `src`, exclusions config/tests/caches, branches activées). Lignes spécifiques ignorables via `# pragma: no cover`.
6. Validation des objectifs : vérifier que global ≥ 50 %, API critiques ≥ 80 %, ML cœur ≥ 60 %. Régressions : cibler d'abord branches d'erreurs / validations, ensuite portions utilitaires.

Optionnel (non activé par défaut) : ajouter `--cov-report=html` ou `--cov-report=xml` à la commande pour générer des artefacts si besoin CI.

## 5. Installation de l'environnement de test
1. Cloner le dépôt Git (versionnage assuré).  
2. Installer les dépendances : `pip install -r requirements.txt`.  
3. Vérifier `pytest.ini` pour les variables sensibles (ex : `API_E3_PASSWORD`, `SECRET_KEY`).  
4. Lancer les tests via script ou commande pytest.

## 6. Tests en environnement de test
- Exécution : Environnement local ou CI (GitHub Actions possible).  
- Stabilité : Pas d'erreurs d'exécution recensées dans les suites nominales.  
- Sandbox ML : données synthétiques contrôlées pour isolement.  

## 7. Détails par domaine
### 7.1 API (unit)
- Auth : succès, mot de passe invalide, credentials absents/incomplets.
- Forecast : succès (horaire / journalier), bornes invalides, unauthorized, payload invalide.
### 7.2 API (intégration)
- Workflow complet login + forecast.
- Accessibilité documentation (`/openapi.json`, `/docs`, `/redoc`).
### 7.3 Application (unit)
- Récupération JWT (succès, échec HTTP, custom args ignorés).
- Forecast : succès, différentes paires, token arbitraire, échec.
### 7.4 Application (intégration)
- Workflows complets (hourly / daily).
- Scénarios d'échec (auth, prévision, récupération).
- Multiples prévisions sur même token.
### 7.5 ML (unit)
- Data : cohérence OHLCV, continuité, valeurs manquantes.
- Train : fréquences, découpage, paramètres, erreurs.
- Evaluate : calcul MAPE/MAE/direction accuracy, index dupliqués.
- Predict : horizons multiples, continuité série, tendances.
### 7.6 ML (intégration)
- Pipeline complet (préparation -> entraînement -> évaluation -> prédiction). 
- Auth API mockée et persistance simulée.

## 8. Fixtures & isolation
- Fixtures globales : client HTTP, auth headers, tokens.
- Fixtures ML : données OHLCV synthétiques, modèles mocks, forecasters paramétrés.
- Fixtures App : configuration URLs, injection credentials.
- Isolation : chaque test recrée ses dépendances mockées ; pas d'effets de bord persistants.

## 9. Accessibilité de la documentation
Cette documentation applique : titres hiérarchisés, listes structurées, langage simple, absence d'images décoratives (donc pas d'alt requis), liens internes explicites si ajoutés, absence de transmission d'information uniquement par couleur. Elle suit les bonnes pratiques générales (référentiel WCAG 2.1 inspiration) pour faciliter lecture et navigation.

## 10. Résultats et interprétation
- Succès attendus : réponses HTTP correctes, structures de données conformes, métriques calculables.
- Erreurs gérées : ValueError, HTTPError, 401/422, prédictions invalides.
- Analyse : les tests valident la robustesse des couches (API, UI, ML) et la cohérence inter-composants.
- Rapports de test (XML/HTML) : Pas d'informations concernant ce point.

## 12. Synthèse
Le dispositif de tests couvre l'ensemble des axes critiques : sécurité basique (auth), logique métier (prévisions et limites), pipeline ML (du nettoyage aux prédictions), et intégration bout-en-bout. La structure modulaire + le script d'orchestration facilitent l'évolution continue. Les tests renforcent la confiance dans la qualité avant intégration continue et offrent une base solide pour étendre la couverture (performance, robustesse avancée) ultérieurement.