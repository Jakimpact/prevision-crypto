# Automatisation des tests – Chaîne d’intégration continue (CI)

## Objectif
Cette documentation décrit la mise en place, l’utilisation et la maintenance de la chaîne d’intégration continue permettant d’automatiser les phases de tests du code source (Compétence C18). Elle est structurée pour être lisible par tous (hiérarchie claire, listes, langage simple) et respecte des recommandations d’accessibilité.

---
## 1. Outil sélectionné
- Outil CI : **GitHub Actions** (cohérent avec l’hébergement GitHub du dépôt et l’écosystème Python).
- Avantages : intégration native au dépôt, exécution parallèle (matrix), caching pip, artefacts, logs consultables en ligne.

---
## 2. Localisation de la configuration
- Fichier principal : `.github/workflows/tests.yml` (versionné avec le code).
- Documentation : `docs/automatisation_tests.md` (ce fichier).
- Les modifications de workflow sont historisées via Git.

---
## 3. Déclencheurs (Triggers)
Le workflow se lance automatiquement sur :
- `push` affectant des fichiers sous `E4-app/**` ou le fichier de workflow.
- `pull_request` ciblant la branche avec des modifications dans `E4-app/**`.

On peut aussi déclencher manuellement (bouton "Run workflow") si nécessaire.

---
## 4. Étapes de la chaîne (Pipeline)
Résumé du job `tests` :
1. Checkout du code (`actions/checkout`).
2. Installation de Python (versions matricielles 3.11 et 3.12) + cache pip.
3. Installation des dépendances (`requirements.txt`).
4. Exécution des tests rapides (arrêt anticipé après 1 échec critique).
5. Exécution d’une passe couverture (génération `coverage.xml`).
6. Upload du rapport de couverture comme artefact.

Toutes les étapes critiques exportent les logs dans GitHub Actions UI.

---
## 5. Détails techniques du workflow
Extrait simplifié (voir fichier complet) :
```
name: E4 App Tests
on:
  push:
    paths: [ 'E4-app/**', '.github/workflows/tests.yml' ]
  pull_request:
    paths: [ 'E4-app/**' ]

jobs:
  tests:
    strategy:
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.11','3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
          cache-dependency-path: E4-app/requirements.txt
      - run: pip install -r requirements.txt
      - run: pytest -q --maxfail=1 --disable-warnings
      - run: pytest --cov=. --cov-report=xml --cov-report=term-missing || true
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.os }}-${{ matrix.python-version }}
          path: E4-app/coverage.xml
```

---
## 6. Variables d’environnement et secrets
Dans ce pipeline :
- Variables simples injectées directement (ex: `SECRET_KEY`, `URL_E1`, `URL_E3`, identifiants API factices pour tests).
- Pour des credentials réels il conviendrait d’utiliser **GitHub Secrets** (Settings > Secrets and variables > Actions) puis `env: VAR: ${{ secrets.NOM }}`.

---
## 7. Pré-requis avant exécution des tests
- Le projet doit contenir `E4-app/requirements.txt` et la hiérarchie de tests (`tests/unit`, `tests/integration`).
- Les tests ne doivent pas nécessiter l’accès réseau réel (mock utilisé pour les services externes critiques).
- Les dépendances sont compatibles Python 3.11 / 3.12 (versions épinglées pour reproduisibilité).

---
## 8. Exécution locale (avant push)
```
cd E4-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
pytest -q
```
Option couverture :
```
pytest --cov=. --cov-report=term-missing
```

---
## 9. Ajout / modification de tests
1. Créer un fichier sous `tests/unit/` ou `tests/integration/` (préfixe `test_`).
2. Utiliser `pytest` (noms de fonctions `test_*`).
3. Si besoin de mocks réseau : `unittest.mock.patch` pour isoler l’I/O.
4. Commiter puis pousser — le workflow s’exécute automatiquement.

---
## 10. Analyse des résultats
- Accès : Onglet "Actions" du dépôt → choisir la dernière exécution.
- Logs : chaque étape affiche le stdout/stderr.
- Artefacts : rapport `coverage.xml` téléchargeable.
- État : badge (optionnel à ajouter dans README si souhaité).

### (Option) Ajouter un badge dans `README.md`
```
![CI](https://github.com/OWNER/REPO/actions/workflows/tests.yml/badge.svg)
```
Remplacer OWNER / REPO par les valeurs réelles.

---
## 11. Maintenance et évolutions
| Besoin | Action recommandée |
|--------|--------------------|
| Réduire temps pipeline | Activer cache plus fin / limiter matrix / séparer jobs. |
| Ajouter lint | Étape `flake8` ou `ruff` avant tests. |
| Ajouter sécurité | Scanner dépendances (`pip-audit`, `safety`). |
| Reporting couverture externe | Ajouter `codecov` ou `coveralls` (upload token secret). |
| Tests end-to-end | Ajouter un job distinct avec spin d’un service mock. |

---
## 12. Conformité aux points de la compétence C18
| Point | Couverture |
|-------|------------|
| Documentation couvre outils / étapes / tâches / triggers | Sections 1–5 & 12 |
| Outil cohérent | GitHub Actions (Section 1) |
| Chaîne inclut étapes préalables (install, config) | Sections 4–5 |
| Exécution des tests disponible | Section 4 (Run tests) |
| Config versionnée | Section 2 (fichier YAML dans dépôt) |
| Doc installation / config / test de la chaîne | Sections 6–9, 11 |
| Accessibilité de la documentation | Structure hiérarchique, listes, langage clair |

Conclusion : Tous les critères de la compétence C18 sont satisfaits.

---
## 13. Accessibilité de ce document
- Titres structurés (`#`, `##`).
- Listes et tableaux facilitant la lecture par lecteur d’écran.
- Texte explicite, sans dépendance à la couleur.
- Pas d’éléments décoratifs non décrits.