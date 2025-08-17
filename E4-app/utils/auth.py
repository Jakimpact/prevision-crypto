from flask import session

def is_authenticated():
    """Vérifie si l'utilisateur est connecté avec un token valide"""
    # Vérification des données essentielles en session
    required_fields = ['user_id', 'access_token', 'username']
    
    for field in required_fields:
        if field not in session:
            return False
    
    # Vérification que le token n'est pas vide
    token = session.get('access_token')
    if not token or len(token.strip()) == 0:
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
