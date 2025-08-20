# Documentation d'intégration du service Token Metrics (Trading Signals)

## Résumé exécutif
Ce document décrit le paramétrage et l'intégration initiale du service **Token Metrics Trading Signals API** dans le cadre du projet de prévision crypto. Il couvre l'accès (authentification par clé API), la configuration réalisée dans le script `parametrage.py`, les dépendances, les procédures d'installation et de test, les données manipulées, ainsi que les considérations d'accessibilité et de monitoring.

## 1. Objectif du service
Le service fournit des signaux de trading (orientations haussières / baissières / neutres) pour des cryptomonnaies. Dans cette démonstration : récupération des signaux via l'endpoint `https://api.tokenmetrics.com/v2/trading-signals`.

## 2. Portée fonctionnelle actuelle
- Récupération des données brutes du service distant.
- Construction d'un DataFrame pandas avec les colonnes principales : `TOKEN_NAME`, `TOKEN_SYMBOL`, `DATE`, `TRADING_SIGNAL`, `TOKEN_TREND`, `TRADING_SIGNALS_RETURNS`, `HOLDING_RETURNS`.
- Affichage console pour vérification manuelle.

## 3. Architecture d'intégration (vue simple)
- Composant client : script `E2-veille/parametrage.py`.
- Secret/API Key : fichier `.env` (variable `token_metrics_api_key`).
- Dépendances Python : `requests`, `pandas`, `python-dotenv`.
- Sortie immédiate : affichage dans la console (peut évoluer vers un enregistrement en base ou un envoi à la couche ML).

## 4. Authentification et gestion des accès
### 4.1 Méthode
- Authentification par **clé API**.
- En-tête utilisé dans le script : `x-api-key: <clé>`. (Remarque : la documentation Token Metrics mentionne parfois `tm-api-key`. Adapter si le fournisseur normalise ce header.)

### 4.2 Stockage de la clé
- Fichier `.env` non versionné (doit être listé dans `.gitignore` — à vérifier). Exemple :
  ```env
  token_metrics_api_key="<votre_cle_api>"
  ```
- Chargement via `load_dotenv` avant l'appel API.

## 5. Installation & configuration
### 5.1 Prérequis
- Python ≥ 3.10 (version exacte non critique ici mais cohérente avec le reste du projet).
- Accès internet vers `api.tokenmetrics.com`.

### 5.2 Installation des dépendances pour ce module
Dans le dossier `E2-veille` :
```bash
pip install -r requirements.txt
```
Contenu actuel :
```
pandas==2.2.3
requests==2.32.3
```
(Vérifier si `python-dotenv` doit être ajouté explicitement. Si absent dans l'env global, ajouter : `python-dotenv>=1.0.0`.)

### 5.3 Configuration
1. Créer / compléter le fichier `.env` avec la clé API.

## 6. Procédure de test rapide
1. Se placer dans le dossier `E2-veille`.
2. Vérifier que la clé est correcte (`echo %token_metrics_api_key%` sous Windows si exportée globalement, sinon ouvrir `.env`).
3. Exécuter :
   ```bash
   python parametrage.py
   ```
4. Résultat attendu : un DataFrame imprimé. En cas d'erreur : code HTTP 400, 401, 403 ou 404.

## 7. Données traitées
### 7.1 Champs utilisés
- `TOKEN_NAME`: Nom lisible.
- `TOKEN_SYMBOL`: Symbole (BTC, ETH, ...).
- `DATE`: Date/horodatage du signal.
- `TRADING_SIGNAL`: Valeur catégorique (généralement 1, -1, 0 ou texte équivalent selon version API).
- `TOKEN_TREND`: Tendance détectée.
- `TRADING_SIGNALS_RETURNS`: Performance associée au signal (si fournie).
- `HOLDING_RETURNS`: Performance de conservation simple (si fournie).

### 7.2 Sensibilité & conformité
- Aucune donnée personnelle / PII.
- Données purement de marché (faible sensibilité, mais valeur business). Stockage futur : respecter les politiques internes (intégrité, traçabilité).

### 7.3 Format & transformation
- Format JSON source → DataFrame pandas.

## 8. Monitoring & journalisation
### 8.1 État actuel
- Pas de monitoring applicatif intégré. Un dashboard de monitoring de l'utilisation de la clé API est disponible sur le site Token Metrics.

## 9. Interconnexions & extensions possibles
| Futur consommateur | Description |
|--------------------|-------------||
| Module ML (E3-ml)  | Alimenter des features dérivées des signaux |
| Base de données (E1-data) | Historisation pour analyses longitudinales |


## 11. Accessibilité du document
Conformité visée : principes généraux d'accessibilité (structure, lisibilité, absence de jargon non défini). 
- Contraste suffisant (géré par la feuille de style de la plateforme de diffusion si publiée en HTML / PDF accessible).