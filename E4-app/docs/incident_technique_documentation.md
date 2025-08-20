# Rapport d'Incident Technique - Expiration des Tokens JWT

## Informations Générales

- **Date de l'incident** : 18 août 2025, 17:41:33
- **Composants affectés** : Application E4 (Flask) et API E1 (FastAPI)
- **Sévérité** : Critique - Perte d'accès aux fonctionnalités après 30 minutes
- **Statut** : ✅ **RÉSOLU** - Implémentation complète déployée

## Description du Problème

### Symptômes Observés

L'application présente un dysfonctionnement critique après 30 minutes d'utilisation :

1. **Côté Application E4 (Flask)** :
   - L'utilisateur reste "connecté" en apparence (session Flask active)
   - Les pages protégées restent accessibles (`/charts`, `/dashboard`, `/forecast`)
   - Les appels API vers E1 échouent avec des erreurs 401/404

2. **Côté API E1 (FastAPI)** :
   - Retourne des erreurs 401 Unauthorized pour les endpoints protégés
   - Les tokens JWT sont correctement expirés après 30 minutes

### Logs d'Erreur

```
# Application E4
127.0.0.1 - - [18/Aug/2025 17:41:33] "GET /charts HTTP/1.1" 200 -
Paire BTC/USDT non trouvée: 401
127.0.0.1 - - [18/Aug/2025 17:41:40] "GET /api/chart-data?base=BTC&quote=USDT&granularity=daily&display_mode=both HTTP/1.1" 404 -

# API E1  
INFO: 127.0.0.1:53458 - "GET /api/v1/trading_pairs/trading_pair_by_currency_symbols/BTC/USDT HTTP/1.1" 401 Unauthorized
```

## Analyse des Causes

### Cause Racine Identifiée

**Incohérence dans la gestion de l'expiration des tokens JWT entre les couches d'authentification**

### Causes Détaillées

#### 1. **Problème de Timezone dans les Tokens JWT (RÉSOLU)**

**Symptôme Initial** :
- Tokens affichaient une expiration incorrecte (3h au lieu de 30 min)
- Décalage de +2h dû à une incohérence timezone

**Cause Technique** :
```python
# AVANT (Problématique)
expire = datetime.now() + timedelta(minutes=30)  # Heure locale (UTC+2)
exp_datetime = datetime.fromtimestamp(exp_timestamp)  # UTC → Local (+2h supplémentaires)

# APRÈS (Corrigé)
expire = datetime.now(timezone.utc) + timedelta(minutes=30)  # UTC
exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)  # UTC
```

**Résolution** : Utilisation forcée d'UTC dans toutes les opérations de date/heure des tokens.

#### 2. **Absence de Validation d'Expiration côté E4 (PROBLÈME ACTUEL)**

**Symptôme** :
- L'application E4 ne vérifie pas l'expiration des tokens stockés en session
- La fonction `is_authenticated()` vérifie seulement la présence du token
- Les utilisateurs restent "connectés" avec des tokens expirés

**Code Problématique** :
```python
# E4-app/utils/auth.py
def is_authenticated():
    required_fields = ['user_id', 'access_token', 'username']
    for field in required_fields:
        if field not in session:
            return False
    
    token = session.get('access_token')
    if not token or len(token.strip()) == 0:
        return False
    
    return True  # Pas de vérification d'expiration !
```

#### 3. **Gestion d'Erreur Insuffisante**

**Symptôme** :
- Les erreurs 401 de l'API E1 ne déclenchent pas de déconnexion automatique
- L'utilisateur voit des erreurs 404 au lieu d'être redirigé vers la connexion
- Expérience utilisateur dégradée

**Flux d'Erreur Actuel** :
```
Session E4 active (30+ min) → Appel API E1 → Token expiré → 401 → Erreur 404 affichée
```

**Flux Attendu** :
```
Session E4 active (30+ min) → Validation token → Expiré → Récupération d'un nouveau token
```

## Impact

### Impact Fonctionnel
- **Perte d'accès** aux données OHLCV
- **Perte d'accès** aux graphiques interactifs
- **Interface incohérente** (connecté mais non fonctionnel)

### Impact Utilisateur
- **Confusion** sur l'état de connexion
- **Interruption de travail** après 30 minutes

## Données Techniques

### Configuration Actuelle
- **Durée token JWT** : 30 minutes (configuré correctement)
- **Session Flask** : Persistante jusqu'à déconnexion manuelle
- **Validation côté E1** : Fonctionnelle (rejette les tokens expirés)
- **Validation côté E4** : Défaillante (ne vérifie pas l'expiration)

### Tests Effectués
1. ✅ **Test d'expiration** : Token expire bien après 30 minutes
2. ✅ **Test de validation E1** : API rejette correctement les tokens expirés  
3. ❌ **Test de validation E4** : Application ne détecte pas l'expiration
4. ❌ **Test de gestion d'erreur** : Pas de déconnexion automatique

## Solutions Identifiées

### Solution 1 : Validation Côté Client (Recommandée)
Ajouter une validation d'expiration dans `is_authenticated()` :
```python
def is_authenticated():
    # Vérifications existantes...
    
    # Nouvelle validation d'expiration
    token = session.get('access_token')
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get('exp')
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            session.clear()  # Déconnexion automatique
            return False
    except:
        session.clear()
        return False
```

### Solution 2 : Renouvellement Automatique
Implémenter un système de refresh token (plus complexe).

## 🛠️ Procédure de Débogage Complète

### Étape 1 : Identification du Problème de Timezone

#### 1.1 Ajout de Logs de Debug dans l'API E1
**Fichier modifié** : `E1-data/src/C5_api/utils/auth.py`

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # DEBUG: Affichage des informations d'expiration
    print(f"🔐 DEBUG TOKEN CREATION:")
    print(f"   - Création: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Expiration: {expire.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Durée: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"   - Utilisateur: {data.get('sub', 'Unknown')}")
    
    encoded_jwt = jwt.encode(to_encode, SecretSettings.API_SECRET_KEY, algorithm=SecretSettings.API_ALGORITHM)
    return encoded_jwt
```

#### 1.2 Observation du Problème
**Logs observés** :
```
🔐 DEBUG TOKEN CREATION:
   - Création: 2025-08-18 16:34:45
   - Expiration: 2025-08-18 17:04:45
   - Durée: 30 minutes

🔍 DEBUG TOKEN VALIDATION:
   - Expiration token: 2025-08-18 19:04:45  # ❌ +2h de décalage !
   - Temps restant: 2:29:37
```

#### 1.3 Diagnostic
**Cause identifiée** : Incohérence timezone entre création (local) et validation (UTC→local conversion)

### Étape 2 : Correction du Problème de Timezone

#### 2.1 Solution Implémentée : Option 2 (UTC Forcé)
**Fichier modifié** : `E1-data/src/C5_api/utils/auth.py`

**Modifications** :
```python
# Import ajouté
from datetime import datetime, timedelta, timezone

# Création avec UTC
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # ...

# Validation avec UTC
def decode_access_token(token: str):
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    # ...
```

#### 2.2 Validation de la Correction
**Résultat** : Token expire correctement après 30 minutes, erreurs 401 générées par l'API E1.

### Étape 3 : Résolution du Problème Principal côté E4

#### 3.1 Identification du Problème
**Observation** : Utilisateurs restent connectés en apparence mais reçoivent des erreurs 401.

#### 3.2 Implémentation de la Solution Complète

##### A. Ajout des Dépendances
**Fichier modifié** : `E4-app/requirements.txt`
```diff
+ python-jose==3.3.0
```

##### B. Création de la Fonction de Validation
**Fichier modifié** : `E4-app/utils/auth.py`

```python
from flask import session, request, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timezone
from jose import jwt

def check_token_validity():
    """
    Vérifie la validité du token JWT et déconnecte automatiquement si expiré.
    """
    if not is_authenticated():
        return False
    
    token = session.get('access_token')
    try:
        # Décoder sans vérifier la signature avec une clé factice
        payload = jwt.decode(
            token, 
            key="fake-key",  # Clé factice requise par python-jose
            algorithms=["HS256"], 
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_aud": False,
                "verify_iss": False
            }
        )
        exp = payload.get('exp')
        
        # Validation explicite de la présence d'expiration
        if exp is None:
            session.clear()
            return False
        
        # Vérification d'expiration en UTC
        exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        
        if exp_time < current_time:
            session.clear()
            return False
        
        return True
    except Exception:
        session.clear()
        return False
```

##### C. Création du Décorateur Middleware
```python
def require_valid_token(f):
    """
    Décorateur pour protéger les routes avec validation automatique du token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_token_validity():
            if request.path.startswith('/api/'):
                return {'error': 'Token expiré, veuillez vous reconnecter'}, 401
            else:
                flash('Votre session a expiré, veuillez vous reconnecter', 'warning')
                return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

#### 3.3 Application aux Routes Protégées
**Fichier modifié** : `E4-app/app.py`

**Routes web mises à jour** :
```python
@app.route('/dashboard')
@require_valid_token
def dashboard():
    # Plus besoin de if not is_authenticated()
    # ...

@app.route('/forecast', methods=['GET', 'POST'])
@require_valid_token
def forecast():
    # ...

@app.route('/charts')
@require_valid_token
def charts():
    # ...
```

**Routes API mises à jour** :
```python
@app.route('/api/chart-data')
@require_valid_token
def api_chart_data():
    # Plus besoin de if not is_authenticated()
    # ...

@app.route('/api/trading-pairs')
@require_valid_token
def api_trading_pairs():
    # ...
```

### Étape 4 : Débogage des Problèmes d'Implémentation

#### 4.1 Problème Rencontré : Erreur de Décodage JWT
**Erreur observée** :
```
    DEBUG: Erreur décodage token: decode() missing 1 required positional argument: 'key'
```

**Cause** : La fonction `jwt.decode()` de `python-jose` exige une clé même avec `verify_signature: False`.

#### 4.2 Solution Appliquée
```python
payload = jwt.decode(
    token, 
    key="fake-key",  # Clé factice requise
    algorithms=["HS256"], 
    options={"verify_signature": False, ...}
)
```

#### 4.3 Problème Logique Identifié
**Question utilisateur** : "Il manque une étape logique si exp is None ?"

**Problème** : La logique `if exp:` retournait `True` par défaut si `exp` était `None`.

**Correction appliquée** :
```python
# AVANT (défaillant)
if exp:
    # vérifier expiration
    pass
return True  # ❌ Accepte les tokens sans expiration

# APRÈS (sécurisé)
if exp is None:
    session.clear()
    return False  # ✅ Rejette les tokens sans expiration

# Puis vérifier l'expiration normalement
exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
# ...
```

## Résolution Finale

### Fonctionnalités Implémentées

1. **Validation Proactive** : Vérification automatique avant chaque route protégée
2. **Déconnexion Automatique** : Nettoyage de session si token expiré
3. **Gestion Différenciée** : 
   - Routes API → Erreur JSON 401
   - Routes web → Redirection avec message
4. **Sécurité Renforcée** : Rejet des tokens malformés ou sans expiration
5. **Code Maintenable** : Décorateur réutilisable, logique centralisée

### Tests de Validation

1. ✅ **Token valide** : Accès normal aux fonctionnalités
2. ✅ **Token expiré** : Déconnexion automatique et redirection
3. ✅ **Token malformé** : Déconnexion automatique
4. ✅ **Token sans expiration** : Rejet sécurisé
5. ✅ **Routes API** : Retour d'erreur 401 approprié
6. ✅ **Routes web** : Redirection avec message utilisateur