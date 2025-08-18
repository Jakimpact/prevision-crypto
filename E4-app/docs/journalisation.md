# Documentation - Système de Journalisation

## Vue d'ensemble

Le système de journalisation centralisé de l'application E4 permet un suivi complet des actions utilisateur, des erreurs système et des événements de sécurité. Il est conçu pour être simple à utiliser, performant et adapté à un environnement de production.

## Architecture

### Structure des fichiers
```
E4-app/
├── utils/
│   └── logger.py           # Module principal de journalisation
├── logs/                   # Répertoire des fichiers de log
│   ├── app.log            # Log principal avec rotation
│   ├── app.log.1          # Sauvegarde 1
│   ├── app.log.2          # Sauvegarde 2
│   ├── ...                # Jusqu'à 5 sauvegardes
│   ├── error.log          # Log des erreurs uniquement
│   └── error.log.1        # Sauvegardes des erreurs
├── config.py              # Configuration des paramètres de log
└── docs/
    └── journalisation.md  # Cette documentation
```

## Configuration

### Paramètres de configuration (`config.py`)

```python
class Config:
    # Journalisation
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')           # Niveau de log
    LOG_DIR = os.getenv('LOG_DIR', 'logs')               # Répertoire des logs
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB par fichier
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))   # 5 fichiers de sauvegarde
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'   # Format des messages
```

### Niveaux de log disponibles
- **DEBUG** : Informations détaillées pour le développement
- **INFO** : Informations générales sur le fonctionnement
- **WARNING** : Avertissements et situations suspectes
- **ERROR** : Erreurs nécessitant une attention

### Variables d'environnement
```bash
# Optionnel - Configuration via variables d'environnement
export LOG_LEVEL=DEBUG
export LOG_DIR=/var/log/crypto-app
export LOG_MAX_BYTES=20971520  # 20MB
export LOG_BACKUP_COUNT=10
```

## Utilisation

### Import et utilisation basique

```python
from utils.logger import logger

# Méthodes disponibles
logger.log_info("Message d'information")
logger.log_warning("Message d'avertissement")
logger.log_error("Message d'erreur")
logger.log_debug("Message de debug")

# Ou utilisation directe
logger.info("Message d'information")
logger.warning("Message d'avertissement")
logger.error("Message d'erreur")
logger.debug("Message de debug")
```

### Import des fonctions raccourcies

```python
from utils.logger import log_info, log_warning, log_error, log_debug

log_info("Utilisateur connecté")
log_warning("Tentative de connexion échouée")
log_error("Erreur de base de données")
log_debug("Valeur de la variable X")
```

### Contexte utilisateur automatique

Le système ajoute automatiquement le contexte utilisateur (nom et IP) :

```python
# Code
log_info("Action effectuée")

# Résultat dans le log
2024-08-18 14:30:15 - INFO - Action effectuée - User: john_doe - IP: 192.168.1.100
```

### Désactiver le contexte utilisateur

```python
# Pour les logs système sans contexte utilisateur
logger.log_info("Démarrage de l'application", include_user=False)

# Résultat
2024-08-18 14:30:15 - INFO - Démarrage de l'application
```

### Gestion des exceptions

```python
try:
    # Code pouvant lever une exception
    result = risky_operation()
except Exception as e:
    # Log avec trace complète de l'exception
    logger.log_error(f"Erreur lors de l'opération: {str(e)}", exc_info=True)
```

## Exemples de logs générés

### Authentification
```
2024-08-18 14:30:15 - INFO - Tentative de connexion pour l'utilisateur: john_doe - User: Anonymous - IP: 192.168.1.100
2024-08-18 14:30:16 - INFO - Connexion réussie pour: john_doe - User: john_doe - IP: 192.168.1.100
2024-08-18 14:35:22 - WARNING - Token expiré pour l'utilisateur john_doe - Déconnexion automatique - User: john_doe - IP: 192.168.1.100
```

### Accès aux pages
```
2024-08-18 14:31:10 - INFO - Accès au dashboard - User: john_doe - IP: 192.168.1.100
2024-08-18 14:32:45 - INFO - Consultation des prévisions BTC-USDT - User: john_doe - IP: 192.168.1.100
2024-08-18 14:33:20 - INFO - Visualisation des graphiques ETH-USDT - User: john_doe - IP: 192.168.1.100
```

### Erreurs et avertissements
```
2024-08-18 14:40:18 - ERROR - Erreur API E1: 500 - Internal Server Error - User: alice - IP: 192.168.1.101
2024-08-18 14:41:05 - WARNING - Tentative d'accès API avec token invalide pour bob: /api/forecast - User: bob - IP: 192.168.1.102
2024-08-18 14:42:12 - ERROR - Headers d'authentification manquants pour récupération OHLCV - User: charlie - IP: 192.168.1.103
```

## Fonctionnalités avancées

### Rotation automatique
- **Taille maximum** : 10MB par fichier par défaut
- **Nombre de sauvegardes** : 5 fichiers par défaut
- **Rotation** : Automatique quand la taille limite est atteinte
- **Compression** : Les anciens fichiers sont conservés sans compression

### Séparation des logs
- **app.log** : Tous les niveaux de log (INFO, WARNING, ERROR, DEBUG)
- **error.log** : Uniquement les erreurs (ERROR)

### Mode développement
En mode DEBUG (`Config.DEBUG = True`), les logs sont également affichés dans la console.

### Performance
- **Asynchrone** : Les écritures de log n'bloquent pas l'application
- **Bufferisé** : Les logs sont écrits par lots pour optimiser les performances
- **Contexte paresseux** : Le contexte utilisateur n'est récupéré qu'au moment de l'écriture

## Sécurité et confidentialité

### Données sensibles
**Attention** : Ne jamais logger de données sensibles :
- Mots de passe
- Tokens complets (seulement les premières/dernières lettres)
- Clés API
- Données personnelles sensibles

### Exemple de log sécurisé
```python
# ❌ MAUVAIS
log_info(f"Token: {full_token}")

# ✅ BON
log_info(f"Token: {token[:8]}...{token[-4:]}")

# ✅ BON
log_info("Token valide pour l'utilisateur")
```

### Accès aux fichiers
- Les fichiers de log sont créés avec des permissions restrictives
- Seul le processus de l'application peut écrire dans les logs
- Accès en lecture réservé aux administrateurs

## Monitoring et maintenance

### Surveillance des logs
```bash
# Suivi en temps réel
tail -f logs/app.log

# Recherche d'erreurs
grep "ERROR" logs/app.log

# Statistiques de connexion
grep "Connexion réussie" logs/app.log | wc -l

# Tentatives de connexion échouées
grep "Échec de connexion" logs/app.log
```

### Nettoyage automatique
Le système de rotation gère automatiquement :
- Suppression des anciens fichiers
- Conservation de l'historique selon `LOG_BACKUP_COUNT`
- Pas de nettoyage manuel nécessaire

### Alertes recommandées
Configurez des alertes pour :
- Taux d'erreur élevé (> 5% des requêtes)
- Tentatives de connexion multiples échouées
- Erreurs de connexion API répétées
- Espace disque faible dans le répertoire de logs

## Troubleshooting

### Problèmes courants

#### Les logs ne s'écrivent pas
1. Vérifier les permissions du répertoire `logs/`
2. Vérifier l'espace disque disponible
3. Contrôler la configuration `LOG_LEVEL`

#### Logs trop volumineux
1. Réduire `LOG_MAX_BYTES`
2. Augmenter `LOG_BACKUP_COUNT` si nécessaire
3. Passer en niveau `WARNING` ou `ERROR` en production

#### Performances dégradées
1. Vérifier si le disque de logs n'est pas saturé
2. Réduire le niveau de log en production
3. Considérer un stockage plus rapide pour les logs

### Commandes de diagnostic

```bash
# Vérifier la configuration
python -c "from config import Config; print(f'LOG_LEVEL: {Config.LOG_LEVEL}')"

# Tester l'écriture
python -c "from utils.logger import log_info; log_info('Test log')"

# Vérifier la rotation
ls -la logs/

# Espace disque
df -h logs/
```

## Intégration dans le code

### Dans les routes Flask
```python
from utils.logger import log_info, log_warning, log_error

@app.route('/dashboard')
@require_valid_token
def dashboard():
    log_info("Accès au dashboard")
    try:
        # Logique métier
        return render_template('dashboard.html')
    except Exception as e:
        log_error(f"Erreur lors du chargement du dashboard: {str(e)}")
        return "Erreur interne", 500
```

### Dans les services
```python
from utils.logger import logger

class AuthService:
    def login(self, username, password):
        logger.log_info(f"Tentative de connexion pour: {username}")
        try:
            # Logique d'authentification
            result = authenticate(username, password)
            logger.log_info(f"Connexion réussie pour: {username}")
            return result
        except Exception as e:
            logger.log_error(f"Erreur de connexion pour {username}: {str(e)}")
            raise
```

### Dans les décorateurs
```python
from utils.logger import logger

def require_valid_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_token_validity():
            logger.log_warning(f"Tentative d'accès avec token invalide: {request.path}")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

## Bonnes pratiques

### Messages de log efficaces
```python
# ✅ BON - Message clair et contextualisé
log_info("Récupération données OHLCV pour BTC-USDT, période: 7j")

# ❌ MAUVAIS - Message trop vague
log_info("Récupération données")

# ✅ BON - Niveau approprié
log_error("Échec connexion API E1: timeout après 30s")

# ❌ MAUVAIS - Niveau inapproprié
log_error("Utilisateur connecté")  # Devrait être INFO
```

### Structure cohérente
```python
# Format recommandé : Action + Détails + Contexte
log_info(f"Action: {action} - Détails: {details} - Contexte: {context}")

# Exemples
log_info("Connexion utilisateur - Username: john_doe - Succès")
log_warning("Validation token - Token expiré - Déconnexion automatique")
log_error("Appel API E1 - Endpoint: /forecast - Erreur: 500")
```

### Niveaux de log appropriés
- **DEBUG** : Variables, états internes, traces détaillées
- **INFO** : Actions utilisateur, étapes importantes du processus
- **WARNING** : Situations inhabituelles mais gérées, tentatives échouées
- **ERROR** : Erreurs nécessitant une intervention, exceptions non gérées
