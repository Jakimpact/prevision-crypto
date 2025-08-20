# Dossier E4-app – Vue d'ensemble

## Résumé
Le dossier **E4-app** contient l'application utilisateur (Flask) qui expose les fonctionnalités de consultation, visualisation et interaction (authentification, tableaux de bord, prévisions) autour des données et modèles produits par les autres couches du projet (E1-data, E3-ml). Ce README sert de point d'entrée rapide et renvoie vers les documentations spécialisées dans `docs/`.

## Objectifs principaux
- Fournir une interface web pour:
  - Visualiser les séries OHLCV et métriques.
  - Consulter les prévisions générées (service `forecast`).
  - Gérer l'authentification / inscription basique.
  - Donner accès à des tableaux de bord synthétiques.
- Servir de façade unifiée pour les services internes (données, modèles, monitoring).
- Centraliser la journalisation applicative.

## Structure simplifiée
- `app.py` : Point d'entrée Flask principal.
- `config.py` : Paramètres d'application (environnement, chemins, logs, sécurité).
- `services/` : Couche fonctionnelle (auth, forecast, ohlcv).
- `templates/` : Pages HTML (Jinja2) – vues utilisateur.
- `utils/` : Outils (logger, auth helpers, gestion datetime, alertes).
- `logs/` : Fichiers de logs applicatifs (`app.log`, `error.log`).
- `monitoring/` : Configuration & base pour dashboard de performance.
- `tests/` : Tests unitaires et d'intégration (`run_tests.py`, sous-dossiers `unit/`, `integration/`).
- `Dockerfile` : Conteneurisation pour déploiement.
- `docs/` : Documentation détaillée (liste ci-dessous).

## Flux fonctionnel (haut niveau)
1. Requête utilisateur (navigateur) → `app.py` (route Flask).
2. Appel interne à un service (ex: `services/forecast.py`) pour obtenir les données.
3. Rendu d'un template (Jinja2) avec les données.
4. Journalisation de la requête et potentielle métrique de performance.
5. (Optionnel) Exposition future d'API REST / endpoints JSON.

## Références vers les documentations détaillées
Utiliser les liens explicites :
- [Documentation Application (architecture interne)](docs/app_documentation.md)
- [Documentation Livraison Continue (CI/CD)](docs/livraison_continue_documentation.md)
- [Documentation Monitoring & Journalisation (vue générale)](docs/monitoring_et_journalisation_documentation.md)
- [Documentation Métriques & Journalisation (détails techniques)](docs/metriques_journalisation_documentation.md)
- [Documentation Automatisation des Tests](docs/automatisation_tests_documentation.md)
- [Journal / Gestion des Incidents Techniques](docs/incident_technique_documentation.md)

## Données consommées / produites
- Consomme : données OHLCV, prévisions, métadonnées, signaux.
- Produit : logs applicatifs (accès, erreurs), éventuelles métriques de performance.
- Ne stocke pas directement de données marché persistées (délégué aux couches Data / ML).

## Dépendances (extrait)
- Flask + extensions (monitoring dashboard si activé).
- Bibliothèques internes (services, utils).
- Configuration via variables d'environnement (recommandé) ou fallback `config.py`.

## Qualité / Tests
- Tests présents dans `tests/` (à enrichir si couverture partielle).
- Stratégie: séparation tests unitaires (services isolés) / intégration (routes Flask).

## Sécurité (état de base)
- Authentification simple (vérifier robustesse hashing / sessions).
- Recommandé : ajouter protections CSRF, durcir headers HTTP, utiliser HTTPS en production.

## Monitoring & Observabilité
- Logs structurés disponibles dans `logs/`.
- Dossier `monitoring/` contient configuration d'outils tiers (ex: Flask Monitoring Dashboard).
- Améliorations possibles : métriques Prometheus, traçage distribué.

## Accessibilité
- Templates à auditer (contraste, attributs ARIA, alt text sur images).
- Recommandé : ajouter vérification automatique (ex: axe-core) durant CI.

## Démarrage rapide (exemple indicatif)
```bash
# Installer dépendances (exemple; adapter selon gestion globale du projet)
pip install -r requirements.txt

# Lancer l'application (développement)
python app.py
```

## Révision
- Version : 1.0 (création initiale README)

Pour approfondir un sujet précis, consulter les documents listés dans la section "Références".
