# Monitoring et Journalisation – Application E4

> Résumé: Ce document décrit le dispositif de monitoring (Flask Monitoring Dashboard) et de journalisation/alerting (logs structurés + seuils de latence) mis en place dans l'application E4. Il couvre : objectifs, choix techniques, installation, métriques, seuils, alertes, bonnes pratiques d'exploitation et accessibilité.

## 1. Introduction
L'application E4 implémente deux volets complémentaires :
- **Monitoring d'exécution** (temps de réponse, endpoints instrumentés) via *Flask Monitoring Dashboard* (FMD).
- **Journalisation et alertes** (évènements métier, sécurité légère, performance) via un logger centralisé et un module d'alertes seuil.

L'objectif est de détecter rapidement régressions de performance et anomalies fonctionnelles, tout en produisant des traces exploitables pour diagnostic.

## 2. Objectifs et Portée
- Suivi des endpoints critiques (`/forecast`, `/api/chart-data`).
- Traçabilité des opérations utilisateur (authentification, génération de prévision, accès interface).
- Génération d'alertes automatiques sur dépassement de latence (warning / critical).
- Extensibilité future (taux d'erreurs, percentiles, sécurité renforcée).

## 3. Architecture Synthétique
```
[Flask App]
  |-- app.py (routes + instrumentation latence)
  |-- utils/logger.py (logger central + rotation)
  |-- utils/alerts.py (check_latency + JSON alerts)
  |-- monitoring/config.cfg (config FMD)
  |-- config.py (THRESHOLDS)
  |-- docs/metriques_journalisation.md (catalogue métriques)
```

## 4. Choix Techniques – Justification
| Composant | Choix | Raisons | Alternatives (non retenues) |
|-----------|-------|---------|-----------------------------|
| Monitoring HTTP | Flask Monitoring Dashboard | Intégration native Flask, zero instrumentation lourde, stats endpoint-level | Prometheus + exporter (jugé surdimensionné pour phase actuelle) |
| Journalisation | `logging` standard + RotatingFileHandler | Fiable, stdlib, rotation intégrée | Log frameworks externes (structlog) – valeur ajoutée limitée ici |
| Format logs | Texte lisible + fragments clé=valeur | Lecture humaine rapide, parse possible ultérieur | JSON complet (plus verbeux, pas encore requis) |
| Alerte latence | Seuils statiques dans `Config.THRESHOLDS` | Simplicité, transparence, facile à modifier | Apprentissage adaptatif – complexité prématurée |
| Stockage alertes | Fichier `alerts.jsonl` (JSON Lines) | Append sûr, greppable, compatible ingestion future | Base externe (ELK) – non nécessaire local |
| Injection métriques | Appels ponctuels dans routes critiques | Minimisation du couplage, lisibilité | Middleware global + base temps — plus tard si extension |

## 5. Installation et Configuration
### 5.1 Prérequis
- Python 3.12+ (selon environnement actuel)
- Virtualenv activé (`.venv`)

### 5.2 Dépendances (local)
```powershell
# Depuis le dossier racine du projet ou E4-app
pip install -r requirements.txt
# Vérifier que flask-monitoringdashboard est présent
pip show flask-monitoringdashboard
```

### 5.3 Configuration Monitoring
Fichier: `E4-app/monitoring/config.cfg` (extrait) :
```
[dashboard]
CUSTOM_LINK=admin/dashboard
MONITOR_LEVEL=3
```
- Accès tableau: http://localhost:5000/admin/dashboard
- Credentials définis dans la section `[authentication]` du fichier.

### 5.4 Configuration Application
Fichier: `E4-app/config.py` (extrait):
```python
THRESHOLDS = {
  "latency": {
    "forecast_ms": {"warning": 6000, "critical": 8000},
    "chart_data_ms": {"warning": 8500, "critical": 10000},
  }
}
```

### 5.5 Lancement Local
```powershell
# Depuis E4-app
python app.py
# Ouvrir monitoring
start http://localhost:5000/admin/dashboard
```

## 6. Journalisation – Règles et Intégration
### 6.1 Logger Central
- Défini dans `utils/logger.py`
- Deux fichiers: `logs/app.log` (INFO+) & `logs/error.log` (ERROR)
- Rotation: taille max configurable (`LOG_MAX_BYTES`) et backups (`LOG_BACKUP_COUNT`).

### 6.2 Contexte utilisateur
Chaque log (sauf DEBUG explicite) ajoute: `User: <username> - IP: <ip>` si disponible.

### 6.3 Endpoints Instrumentés
| Endpoint | Logs principaux | Exemple |
|----------|-----------------|---------|
| `/login` | Succès / échec | `Connexion réussie - Utilisateur: Test` |
| `/forecast` | Succès + latence + taille résultat | `Latence prévision - Paire: BTC-USDT - Granularité: daily - Duree_ms: 4511` |
| `/api/chart-data` | Latence + volume bougies | `Latence chart-data - Paire: BTC/USDT - Bougies: 48964 - Duree_ms: 7773` |
| Divers | Erreurs récupération | `Erreur récupération données graphiques: ...` |

### 6.4 Séparation des niveaux
- `INFO`: événements métier normaux.
- `WARNING`: anomalies récupérables (paire inconnue, prévision échouée, alerte warning latence).
- `ERROR`: exceptions & latence critique.

## 7. Monitoring – Détails
### 7.1 Instrumentation FMD
- Binding déplacé après définition de toutes les routes pour garantir la détection.
- Endpoints visibles sous l’interface FMD (fréquence, durée moyenne, etc.).

### 7.2 Complémentarité
FMD fournit agrégations globales (moyennes, distribution), tandis que la journalisation capture contexte métier spécifique (paire, granularité, points prédits).

## 8. Métriques et Seuils d’Alerte
Les métriques complètes (actuelles + backlog) sont documentées dans: **`docs/metriques_journalisation.md`**.

Métriques à risque actuellement surveillées avec alertes:
| Métrique | Warning | Critical | Contexte journalisé |
|----------|---------|----------|---------------------|
| Latence prévision (ms) | > 6000 | > 8000 | paire, granularité, nb points |
| Latence chart-data (ms) | > 8500 | > 10000 | paire, granularité, bougies, forecast_count |

## 9. Système d’Alerte
### 9.1 Flux
1. Durée calculée (ms) dans route.
2. Appel à `check_latency(metric_key, duration_ms, context)`.
3. Comparaison aux seuils -> niveau `WARNING` ou `CRITICAL`.
4. Écriture ligne JSON dans `logs/alerts.jsonl` + log secondaire (`log_warning` / `log_error`).

### 9.2 Format JSON (exemple réel simplifié)
```json
{
  "ts": "2025-08-19T13:06:37Z",
  "metric": "chart_data_ms",
  "value_ms": 9123,
  "threshold_ms": 8500,
  "level": "WARNING",
  "context": {"pair": "BTC/USDT", "granularity": "hourly", "ohlcv_count": 48964}
}
```

### 9.3 Exploitation
Rechercher alertes critiques:
```powershell
Select-String -Path logs/alerts.jsonl -Pattern 'CRITICAL'
```

## 10. Vérifications Opérationnelles
| Contrôle | Méthode | Résultat attendu |
|----------|---------|------------------|
| Accès dashboard | Ouvrir /admin/dashboard | Statistiques endpoints visibles |
| Log latence forecast | Générer prévision | Ligne `Latence prévision` dans app.log |
| Alerte latence warning | Simuler lenteur (>6000ms) | Entrée JSON + log WARNING |
| Alerte latence critical | Simuler lenteur (>8000ms) | Entrée JSON + log ERROR |

## 11. Accessibilité de la Documentation
Bonnes pratiques appliquées :
- Titres hiérarchisés (#, ##, ###) pour structurer.
- Résumé initial pour compréhension rapide.
- Tableaux et listes pour lisibilité (pas d'information transmise uniquement par couleur).
- Liens explicites (ex: *Voir `docs/metriques_journalisation.md`* sans « cliquez ici »).
- Pas d’images ; si ajout futur, fournir un texte alternatif descriptif ou marquer « image décorative ».
- Langage simple et définitions implicites (ex: *latence* = durée d’exécution d’un appel endpoint).
- Formats JSON fournis pour permettre une lecture machine (accessibilité indirecte outils externes).

## 14. Références Fichiers
| Fichier | Rôle |
|---------|------|
| `app.py` | Routes + instrumentation latence |
| `utils/logger.py` | Logger central + rotation |
| `utils/alerts.py` | Génération d’alertes seuils |
| `config.py` | Paramètres + THRESHOLDS |
| `monitoring/config.cfg` | Configuration FMD |
| `docs/metriques_journalisation.md` | Détail complet des métriques |
