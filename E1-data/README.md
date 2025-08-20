# Dossier E1-data – Documentation Générale

## Résumé
Le dossier **E1-data** contient l'ensemble des composants responsables de l'acquisition, la structuration, le stockage et la mise à disposition des données crypto nécessaires aux autres couches du projet (prévision ML, API applicative, visualisation). Il forme la **couche Data Foundation** du système d'information.

## Objectifs principaux
- Collecter des données externes (marchés, OHLCV, métadonnées) depuis des fournisseurs (ex: plateformes d'échange, agrégateurs).
- Normaliser et valider les données (schémas, formats temporels, cohérence des paires et intervalles).
- Stocker dans une base locale (SQLite dans la version actuelle) ou autre backend futur.
- Offrir des scripts d'initialisation (`init_db_and_data.py`) et de mise à jour (`update_ohlcv.py`).
- Préparer des vues ou requêtes réutilisables pour les étapes d'agrégation / reporting / machine learning.

## Structure logique (simplifiée)
- `config/` : Fichiers YAML de configuration (base de données, extraction, mise à jour).
- `data/` : Arborescence de stockage (base SQLite, sources externes, logs, temporaires).
- `docs/` : Documentation détaillée par sous-domaine (voir liens ci-dessous).
- `init_db_and_data.py` : Initialisation des tables + première ingestion.
- `update_ohlcv.py` : Mise à jour incrémentale des chandeliers (OHLCV).

## Flux de haut niveau
1. Lecture des paramètres (YAML) → définition des sources et paramètres techniques.
2. Extraction → téléchargement de fichiers / appels d'API externes.
3. Validation / nettoyage → gestion des entrées échouées (fichiers `failed_*`).
4. Insertion en base locale (`crypto_data.db`).
5. Mise à disposition pour agrégation et consommation par les modules ML / API.

## Références vers les documentations détaillées
Chaque aspect a sa propre documentation ciblée. Utiliser les liens explicites ci-dessous :

- [Documentation API d'extraction / ingestion](docs/api_documentation.md)
- [Documentation des requêtes (Query Layer)](docs/query_documentation.md)
- [Documentation d'agrégation (transformations & vues)](docs/aggregation_documentation.md)
- [Documentation base de données (structures, tables, index)](docs/database_documentation.md)
- [Modèle conceptuel / Merise](docs/merise_model_documentation.md)
- [Diagramme Entité-Association (ER)](docs/diagramme_ER.png "Diagramme ER – modèle de données") – (Image : représentation graphique des entités, clés, relations; alt text: Diagramme montrant les entités principales crypto, prix, historique OHLCV et leurs relations.)

## Données manipulées
- Données de marché (OHLCV, symboles, paires trading).
- Métadonnées d'extraction (timestamps de dernière mise à jour, logs d'échec).
- Aucune donnée personnelle (PII) – orientation purement marché.

## Interconnexions
| Consommateur | Usage | Mode |
|--------------|-------|------|
| Module ML (E3-ml) | Features modèles (historique, agrégats) | Lecture via requêtes / exports |
| API Applicative (E4-app) | Exposition / consultation métriques | Requêtes directes ou endpoints intermédiaires |
| Veille / Analyse (E2-veille) | Comparaison signaux externes | Alignement symboles / normalisation |

## Qualité & Fiabilité (état actuel)
- Journaux d'erreurs (`data/logs/failed_*`).
- Nécessite consolidation des validations (contrôles de duplications, cohérence temporalité). 
- Améliorations possibles : tests automatiques sur schéma, monitoring volume/jours manquants.

## Sécurité
- Aucune clé sensible stockée ici par défaut (vérifier si ajout futur d'APIs privées).
- Éviter l'introduction de secrets dans `config/` (préférer variables d'environnement).

## Accessibilité documentaire
- Ce document sert de point d'entrée rapide.
- Langage clair, titres hiérarchisés, liens explicites. 
- Alt text fourni pour l'image du diagramme ER.


## Révision
- Version: 1.0

Pour approfondir un sujet spécifique, consulter directement les documents listés dans la section "Références" ci-dessus.