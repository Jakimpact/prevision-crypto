# Livraison Continue – Chaîne CD (Compétence C19)

## Objectif
Mettre en place un processus de livraison continue basé sur la chaîne d’intégration continue existante afin de produire un artefact exécutable (image Docker) et de préparer la mise à disposition (pull request de release). Document conforme accessibilité (titres structurés, listes claires, pas de dépendance couleur).

---
## 1. Périmètre
Application Flask `E4-app` (prévisions crypto). La chaîne CD :
1. Vérifie la qualité (tests). 2. Construit une image Docker. 3. Publie l’image dans un registre (GHCR). 4. Prépare une Pull Request de release depuis `dev` vers `main`.

---
## 2. Fichiers de configuration
| Fichier | Rôle |
|---------|------|
| `.github/workflows/cd.yml` | Définition du pipeline de livraison continue |
| `E4-app/Dockerfile` | Construction de l’image applicative |
| `E4-app/.dockerignore` | Exclusions pour l’image |
| `.github/workflows/tests.yml` | Chaîne CI (réutilisée conceptuellement en amont) |

Tous versionnés dans le dépôt Git distant.

---
## 3. Déclencheurs
- `push` sur branches `main` ou `dev` avec modifications dans `E4-app/**` ou fichiers workflow.
- Déclenchement manuel via `workflow_dispatch` (interface GitHub Actions).

---
## 4. Étapes de la chaîne CD
1. **Checkout** du dépôt.
2. **Tests** (unitaires + intégration) pour garantir non-régression avant packaging.
3. **Login registry** (GitHub Container Registry) via `GITHUB_TOKEN`.
4. **Extraction métadonnées** (tags dynamiques: branche, sha, latest sur branche par défaut).
5. **Build+Push** image Docker multi-cachée (Buildx + cache GHA).
6. **Pull Request Release** automatique (si branche `dev`) vers `main`.

---
## 5. Packaging (Image Docker)
Caractéristiques de `Dockerfile` :
- Base `python:3.11-slim` (légère, sécurité améliorée).
- Installation dépendances via couche dédiée (cache efficace).
- Copie du code et exposition port 5000.
- Variable `DISABLE_MONITORING=1` par défaut (peut être désactivée en prod via override).
- Healthcheck HTTP simple `/`.

Commande locale de test :
```
cd E4-app
docker build -t e4-app:local .
docker run -p 5000:5000 e4-app:local
```

---
## 6. Publication de l’image
- Tags générés automatiquement (`branch`, `sha`, `latest` sur branche par défaut).
- Chemin attendu: `ghcr.io/<OWNER>/<REPO>-e4-app:<tag>`.
- Accès : Packages du repo GitHub.

Pour extraire l’image :
```
docker pull ghcr.io/OWNER/REPO-e4-app:latest
```
Remplacer OWNER / REPO.

---
## 7. Pull Request de Release
Étape `create-release-pr` (uniquement sur `dev`) crée ou met à jour une PR vers `main` :
- Titre: `Release: Sync dev -> main`.
- Labels: `release, automation`.
- Permet révision manuelle avant fusion (gate finale de livraison).

---
## 8. Installation / Configuration de la chaîne
Pré-requis côté dépôt :
- Activer GitHub Packages (permissions défaut suffisent avec `GITHUB_TOKEN`).
- Branches `dev` et `main` existantes.
- Optionnel : protéger `main` (reviews obligatoires).

Secrets supplémentaires (non requis par défaut) :
- Pour registre externe: `REGISTRY_USER`, `REGISTRY_PASSWORD`.

---
## 9. Test local du Dockerfile
```
cd E4-app
pip install -r requirements.txt  # Vérification deps
python -m pytest -q              # Sanity test
docker build -t test-e4 .
docker run --rm -p 5000:5000 test-e4
```
Aller sur `http://localhost:5000/`.

---
## 10. Observabilité & Qualité
- Tests bloquent build si échec.
- Logs build disponibles dans l’onglet Actions.
- Possibilité d’ajouter plus tard : scan vulnérabilités (`trivy`), signature image (`cosign`).

---
## 11. Accessibilité de cette documentation
- Titres hiérarchisés.
- Listes pour structurer l’information.
- Texte clair, phrases directes.
- Aucune information uniquement transmise par couleur.

