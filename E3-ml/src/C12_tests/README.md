# Tests API E3-ml

## Structure des tests

La structure des tests est organisée de manière hiérarchique pour séparer les tests unitaires et d'intégration :

```
src/C12_tests/
├── conftest.py                    # Configuration globale des fixtures pytest
├── run_tests.py                   # Script principal d'orchestration des tests
├── unit/                          # Tests unitaires
│   ├── __init__.py
│   ├── test_api_auth.py          # Tests des endpoints d'authentification
│   └── test_api_forecast.py      # Tests des endpoints de prévision
└── integration/                   # Tests d'intégration
    ├── __init__.py
    └── test_api_integration.py    # Tests d'intégration de l'API complète
```

### Fichiers principaux

- `conftest.py` : Configuration globale des fixtures pytest (TestClient, tokens JWT, headers d'auth)
- `run_tests.py` : Script simplifié pour orchestrer l'exécution des tests avec gestion des variables d'environnement

## Lancement des tests

### Tous les tests
```bash
python src/C12_tests/run_tests.py
```

### Tests unitaires uniquement
```bash
python src/C12_tests/run_tests.py --unit
```

### Tests d'intégration uniquement
```bash
python src/C12_tests/run_tests.py --integration
```

### Directement avec pytest
```bash
# Tous les tests
pytest src/C12_tests/ -v

# Tests unitaires seulement
pytest src/C12_tests/unit/ -v

# Tests d'intégration seulement
pytest src/C12_tests/integration/ -v

# Tests avec marqueurs
pytest src/C12_tests/ -v -m "unit"
pytest src/C12_tests/ -v -m "integration"
```

## Configuration CI/CD

Les tests sont configurés pour fonctionner avec GitHub Actions via le fichier `pytest.ini` :

### Configuration pytest (`pytest.ini`)
- **Génération de rapports** : Support pour XML et coverage
- **Marqueurs** : `unit`, `integration`, `slow` pour catégoriser les tests
- **Variables d'environnement** : Configuration automatique pour les tests
  - `API_E3_PASSWORD=test_password`
  - `SECRET_KEY=test_secret_key_for_jwt_signing_in_tests_only`
  - `API_E3_ALGORITHM=HS256`

### Script d'orchestration (`run_tests.py`)
- **Exécution simplifiée** : Gestion automatique des variables d'environnement
- **Sélection de tests** : Options `--unit` et `--integration`
- **Compatibilité CI** : Codes de sortie appropriés pour les pipelines

## Mocking et isolation des tests

### Stratégie de mocking
Les tests utilisent `unittest.mock` pour isoler les dépendances :

#### Tests de prévision
- **Mock de `load_model`** : Simulation des modèles ML sans fichiers réels
- **Chemin de mock** : `src.C9_api.routes.forecast.load_model` (où la fonction est importée)
- **Objets mockés** : Modèles avec méthodes `predict()` retournant des données de test

#### Tests d'authentification
- **Mock des variables d'environnement** : `monkeypatch` pour les credentials
- **Isolation JWT** : Tokens de test générés avec clés dédiées

#### Gestion des exceptions
- **ValueError** : Utilisation de `pytest.raises` pour les validations d'entrée
- **HTTPException** : Tests des codes de statut HTTP pour les erreurs API

## Tests couverts

### Tests unitaires

#### Authentification (`unit/test_api_auth.py`)
- ✅ Login réussi avec mot de passe valide
- ✅ Login échoué avec mot de passe invalide  
- ✅ Login sans credentials
- ✅ Login avec username mais sans mot de passe
- ✅ Mock des variables d'environnement avec `monkeypatch`

#### Prévisions (`unit/test_api_forecast.py`)
- ✅ Prévision horaire réussie avec mock des modèles
- ✅ Prévision journalière réussie avec mock des modèles
- ✅ Validation des limites `num_pred` (ValueError)
- ✅ Tests sans authentification (401 Unauthorized)
- ✅ Tests avec payload invalide
- ✅ Mock de `load_model` avec objets simulés
- ✅ Gestion des exceptions avec `pytest.raises`

### Tests d'intégration

#### Workflow complet (`integration/test_api_integration.py`)
- ✅ Démarrage de l'application FastAPI
- ✅ Workflow complet : login → authentification → prévision
- ✅ Accessibilité de la documentation API (`/docs`)
- ✅ Tests end-to-end avec état partagé
- ✅ Mock des dépendances externes (modèles ML)

## Fixtures pytest

### Fixtures globales (`conftest.py`)
- `client` : Instance TestClient pour les requêtes HTTP
- `valid_token` : Token JWT valide pour l'authentification
- `auth_headers` : Headers d'autorisation formatés

### Gestion des dépendances
- **Isolation** : Chaque test utilise un client frais
- **Mocking** : Isolation des modèles ML et de la base de données
- **Variables d'env** : Configuration automatique pour les tests

## Prérequis et dépendances

### Packages Python requis
Les tests nécessitent les dépendances suivantes (définies dans `requirements.txt`) :

```
pytest>=6.0
fastapi[all]
python-jose[cryptography]
uvicorn
```

### Installation
```bash
# Installation des dépendances depuis le répertoire E3-ml
pip install -r requirements.txt
```

## Résolution des problèmes courants

### Erreurs de mocking
- **FileNotFoundError** : Vérifier que le chemin de mock correspond à l'import dans le code cible
- **Mock non appliqué** : S'assurer d'utiliser le bon chemin (où la fonction est importée, pas définie)

### Exemples de chemins de mock corrects
```python
# ✅ Correct - où la fonction est importée
@patch('src.C9_api.routes.forecast.load_model')

# ❌ Incorrect - où la fonction est définie  
@patch('src.C9_api.utils.functions.load_model')
```

### Variables d'environnement
Les variables sont automatiquement configurées par `pytest.ini` et `run_tests.py`. 
En cas de problème, vérifier que les valeurs correspondent entre les deux fichiers.

## Structure pour CI/CD

Les tests sont prêts pour GitHub Actions avec :
- **Codes de sortie** : 0 pour succès, 1 pour échec
- **Variables d'environnement** : Configuration automatique
- **Rapports** : Support XML pour les rapports de test
- **Isolation** : Tests indépendants sans effets de bord

### Exemple de commande CI
```bash
# Exécution complète pour CI/CD
python src/C12_tests/run_tests.py
echo "Exit code: $?"
```
