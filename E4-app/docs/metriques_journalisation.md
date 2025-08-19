# Métriques de Journalisation et Monitoring - Application E4

Ce document recense les métriques actuellement journalisées dans l'application Flask (E4) ainsi que celles proposées pour une supervision élargie avec seuils et alertes.

## 1. Objectifs
- Disposer d'une traçabilité des actions utilisateur et des traitements métiers.
- Permettre la détection précoce d'anomalies de performance, d'erreurs et d'abus.
- Préparer l'implémentation d'alertes basées sur des seuils configurables (via `config.py`).

## 2. Niveaux de Log Utilisés
| Niveau | Usage Principal | Exemples |
|--------|-----------------|----------|
| DEBUG  | Diagnostic technique détaillé (dev) | Accès à une page, paramètres d'appel |
| INFO   | Événements normaux significatifs | Connexion réussie, génération de prévision |
| WARNING| Situations anormales récupérables | Tentative de login échouée, paramètres invalides |
| ERROR  | Échec bloquant ou exception | Erreur API, exception dans un service |

## 3. Métriques Actuellement Journalisées
| Domaine | Métrique | Description | Source Log | Exemple Actuel |
|---------|----------|-------------|------------|----------------|
| Authentification | Connexions réussies | Nombre et fréquence des logins valides | `log_info` dans `login()` | "Connexion réussie - Utilisateur: X" |
| Authentification | Connexions échouées | Tentatives invalides (credentials erronés) | `log_warning` | "Tentative de connexion échouée - Utilisateur: X" |
| Authentification | Tokens expirés | Sessions invalidées pour expiration | `require_valid_token` | "Token expiré pour l'utilisateur X" |
| Session | Déconnexions | Comptage des logouts | `log_info` dans `logout()` | "Déconnexion - Utilisateur: X" |
| Prévision | Prévisions générées | Succès de génération de séries prédites | `log_info` dans `forecast()` | "Prévision générée - Paire: BTCUSDT - Granularité: hourly - Points: 24" |
| Prévision | Échecs de prévision | Erreurs côté service modèle/API | `log_warning` | "Échec prévision - Paire: ..." |
| Performance | Latence prévision (ms) | Durée totale génération prévision | `log_info` + `check_latency` | "Latence prévision - Paire: BTC-USDT - Granularité: daily - Duree_ms: 4511" |
| Données | Requêtes chart-data | Appels aux données OHLCV + forecast | `log_debug` | "Appel API chart-data - Paire: BTC/USDT - Granularité: hourly" |
| Performance | Latence chart-data (ms) | Durée agrégation & formatage OHLCV/forecast | `log_info` + `check_latency` | "Latence chart-data - Paire: BTC/USDT - Granularité: hourly - Bougies: 48964 - Duree_ms: 7773" |
| Données | Paires non trouvées | Incohérence de paramètre ou absence DB | `log_warning` | "Paire de trading non trouvée - BTC/ABC" |
| Données | Erreurs récupération | Exceptions côté data service | `log_error` | "Erreur récupération données graphiques: ..." |
| Navigation | Accès dashboard | Trafic réel vers interface principale | `log_debug` | "Accès au dashboard" |
| Système | Démarrage application | Trace unique de lancement | `log_info` | "Application E4 démarrée" |

## 4. Métriques Recommandées à Ajouter (Backlog)
| Domaine | Métrique | Description | Mode de Calcul | Intérêt |
|---------|----------|-------------|----------------|---------|
| Performance | Temps moyen par endpoint | Moyenne glissante sur N requêtes | Décorateur + deque | Optimisation ressources |
| Performance | P95 latence chart-data | 95e percentile fenêtre glissante | Buffer temps | Détection pics |
| Erreurs | Taux erreurs prévision | % erreurs / total sur fenêtre | Compteurs + fenêtre | Santé modèle/API |
| Erreurs | Taux erreurs chart-data | % erreurs / total sur fenêtre | Compteurs | Stabilité data |
| Sécurité | Tentatives login par IP | Fréquence des échecs par IP | Compteur + purge temps | Anti brute force |

## 5. Seuils et Valeurs d'Alerte (Implémentés)
Sources: `Config.THRESHOLDS` + module `utils/alerts.py`.

| Catégorie | Métrique | Warning | Critical | Déclenchement | Action | Exemple Alerte |
|-----------|---------|---------|----------|---------------|--------|----------------|
| Performance | Latence prévision (ms) | > 6000 | > 8000 | Durée unique d'un appel | Écriture JSON + log WARNING/ERROR | `{ "metric": "forecast_ms", "value_ms": 9120, "level": "CRITICAL" }` |
| Performance | Latence chart-data (ms) | > 8500 | > 10000 | Durée unique d'un appel | Écriture JSON + log WARNING/ERROR | `{ "metric": "chart_data_ms", "value_ms": 10350, "level": "CRITICAL" }` |

Format JSON stocké: fichier `logs/alerts.jsonl` (1 alerte par ligne). Clés: `ts`, `metric`, `value_ms`, `threshold_ms`, `level`, `context`.

Exemple réel (simplifié):
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

## 6. Implémentation Réalisée
Étape 1: Ajout des seuils dans `Config.THRESHOLDS`.
Étape 2: Création de `utils/alerts.py` (fonctions `check_latency`, `write_alert`).
Étape 3: Instrumentation des routes `/forecast` et `/api/chart-data` (succès & erreurs) avec appel à `check_latency`.