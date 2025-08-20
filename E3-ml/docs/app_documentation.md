# Documentation Application (C10)

## Introduction
Cette application (dossier `C10_app`) est une interface Streamlit permettant d'intégrer l'API de prévision (C9) et de déclencher des prévisions sur des paires de cryptomonnaies. Elle illustre l'intégration fonctionnelle et utilisateur d'un service IA exposé via une API REST sécurisée.

## Résumé fonctionnel
- Objectif principal : permettre à un utilisateur d'obtenir des prévisions horaires (1–24) ou journalières (1–7) pour des paires prédéfinies (BTC-USDT, ETH-USDT).
- Technologies principales : Streamlit (UI), Requests (communication HTTP), Pydantic / FastAPI côté API (validation), Pandas (affichage tabulaire des résultats).

## 1. Installation et fonctionnement de l'application
- Lancement : exécution de `streamlit run app.py` (supposé) dans l'environnement configuré.
- Pré-requis : variables/config dans `DataSettings` et `SecretSettings` (URL API, credentials) ; dépendances Python installées.
- Statut : application fonctionnelle en environnement de développement (POC). Pas d'informations concernant un déploiement production.

## 2. Communication avec l'API
- Fonction `get_jwt_token` : effectue un POST sur l'endpoint `/authentification/login` pour récupérer un JWT.
- Fonction `get_forecast` : effectue un POST JSON signé (Bearer) vers `/forecast_hourly` ou `/forecast_daily` selon la granularité.
- Gestion simple des erreurs : `raise_for_status()` déclenche une exception gérée dans l'interface (affichage `st.error`).
- Les URL d'accès sont issues de `DataSettings` (centralisation des endpoints).

## 3. Authentification & renouvellement
- Authentification initiale : récupération dynamique du token avant chaque séquence de prévision.
- Renouvellement : Pas d'informations concernant ce point (le token est demandé à chaque soumission de formulaire, pas de logique d'expiration gérée côté app mais une logique implémenté côté API, ne génère pas de problème car le token est redemandé à chaque utilisation).

## 4. Intégration des points de terminaison API
- Endpoints intégrés : `/authentification/login`, `/forecast/forecast_hourly`, `/forecast/forecast_daily` via les fonctions utilitaires.

## 5. Adaptations d'interface
- Sélection de granularité via `st.sidebar.radio` (horaire vs journalière).
- Formulaire unique (`st.form`) pour saisie du nombre de pas et de la paire.
- Feedback utilisateur : messages `info`, `success`, `error` ; tableau formaté (`st.dataframe`).
- Formatage de sortie : arrondi des valeurs + ajout du symbole `$`, dates annotées `(UTC)`.
- Accessibilité : usage de labels explicites, structure hiérarchique et composants natifs Streamlit (compatibles lecteurs d'écran). Pas d'informations supplémentaires concernant audits d'accessibilité formels.

## 6. Tests d'intégration de l'application
Localisation : `src/C12_tests/app/`
### 6.1 Tests unitaires (`test_app_utils.py`)
- `get_jwt_token` : succès, échec HTTP, ignoration des credentials passés (fonction actuelle utilise valeurs config), récupération personnalisée, récupération après erreur.
- `get_forecast` : succès (vérification payload & headers), échec HTTP, différentes paires, token au format arbitraire.
### 6.2 Tests composants (`test_app_components.py`)
- Logiciel de sélection d'URL selon granularité (`get_forecast_url`). Cas valides + cas invalide.
### 6.3 Tests d'intégration (`test_app_workflow.py`)
- Workflow complet horaire et journalier (login + forecast).
- Gestion des échecs : auth échouée, forecast échoué, récupération après erreur.
- Multiples prévisions sur même token.
- Intégration des settings (validation URLs & credentials simulés).
- Vérification des imports (robustesse structurelle).

## 7. Exécution des tests et interprétation
- Résultats : chaque test affirme codes de statut implicites via mocks/raise_for_status et structure des réponses.
- Couverture : centrée sur flux utilisateur critiques (auth -> forecast) et robustesse en présence d'erreurs.
- Bugs résiduels connus : Pas d'informations concernant ce point.
- Rapport de couverture chiffré : Pas d'informations concernant ce point.

## 8. Accessibilité et normes
- Interface basée sur Streamlit : composants accessibles par défaut (inputs labellisés, navigation clavier standard, rendu HTML sémantique minimal).
- Documentation interne (présent fichier) : hiérarchie de titres, listes structurées, langage simple, absence d'images décoratives.

## 11. Synthèse
L'application Streamlit intègre correctement les endpoints critiques de l'API de prévision, fournit une interface simple et testée autour du flux principal (authentification, demande de prévisions et affichage structuré). Les tests couvrent les scénarios de succès et d'erreurs, assurant la fiabilité du POC. Des améliorations restent ouvertes pour la gestion de session, l'élargissement fonctionnel et l'accessibilité avancée.
