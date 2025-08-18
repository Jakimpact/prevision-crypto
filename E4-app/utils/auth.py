from flask import session, request, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timezone
from jose import jwt
from utils.logger import logger

def is_authenticated():
    """Vérifie si l'utilisateur est connecté avec un token valide"""
    # Vérification des données essentielles en session
    required_fields = ['user_id', 'access_token', 'username']
    
    for field in required_fields:
        if field not in session:
            logger.log_debug(f"Champ manquant en session: {field}")
            return False
    
    # Vérification que le token n'est pas vide
    token = session.get('access_token')
    if not token or len(token.strip()) == 0:
        logger.log_debug("Token vide ou manquant en session")
        return False
    
    return True

def get_auth_headers():
    """Retourne les headers d'authentification pour les appels API"""
    if not is_authenticated():
        return None
    
    token = session.get('access_token')
    token_type = session.get('token_type', 'bearer')
    
    return {
        'Authorization': f'{token_type.capitalize()} {token}',
        'Content-Type': 'application/json'
    }

def get_current_user():
    """Retourne les informations de l'utilisateur connecté"""
    if not is_authenticated():
        return None
    
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'user_role': session.get('user_role', 'user'),
        'access_token': session.get('access_token')
    }

def check_token_validity():
    """
    Vérifie la validité du token JWT et déconnecte automatiquement si expiré.
    
    Returns:
        bool: True si le token est valide, False si expiré ou invalide
    """
    if not is_authenticated():
        logger.log_debug("Utilisateur non authentifié lors de la vérification du token")
        return False
    
    token = session.get('access_token')
    username = session.get('username', 'unknown')
    
    try:
        # Décoder sans vérifier la signature avec une clé factice
        payload = jwt.decode(
            token, 
            key="fake-key",  # Clé factice
            algorithms=["HS256"], 
            options={
                "verify_signature": False,
                "verify_exp": False,  # Nous gérons l'expiration manuellement
                "verify_aud": False,
                "verify_iss": False
            }
        )
        exp = payload.get('exp')
        
        # Si pas de claim d'expiration, le token est invalide
        if exp is None:
            logger.log_warning(f"Token sans claim d'expiration pour l'utilisateur {username}")
            session.clear()
            return False
        
        # Vérifier si le token est expiré
        exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        
        if exp_time < current_time:
            logger.log_info(f"Token expiré pour l'utilisateur {username} - Déconnexion automatique")
            session.clear()
            return False
        
        return True
    except Exception as e:
        # En cas d'erreur de décodage, nettoyer la session
        logger.log_error(f"Erreur lors du décodage du token pour l'utilisateur {username}: {str(e)}")
        session.clear()
        return False

def require_valid_token(f):
    """
    Décorateur pour protéger les routes avec validation automatique du token.
    
    - Pour les routes API (/api/): retourne une erreur JSON 401
    - Pour les routes web: redirige vers la page de connexion avec message
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', 'unknown')
        
        if not check_token_validity():
            if request.path.startswith('/api/'):
                logger.log_warning(f"Tentative d'accès API avec token invalide pour {username}: {request.path}")
                return {'error': 'Token expiré, veuillez vous reconnecter'}, 401
            else:
                logger.log_info(f"Redirection vers page de connexion pour {username} - Token invalide: {request.path}")
                flash('Votre session a expiré, veuillez vous reconnecter', 'warning')
                return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function
