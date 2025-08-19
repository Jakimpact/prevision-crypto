"""
Module de journalisation centralisé pour l'application E4.
Configuration minimale avec rotation automatique des fichiers.
"""
import logging
import logging.handlers
import os
from flask import request, session
from config import Config


class AppLogger:
    """Gestionnaire de logs centralisé pour l'application."""
    
    def __init__(self):
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure le logger avec les paramètres de config."""
        # Créer le répertoire de logs s'il n'existe pas
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)
        
        # Configuration du logger principal
        self.logger = logging.getLogger('crypto_app')
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Éviter la duplication des handlers
        if self.logger.handlers:
            return
        
        # Formatter commun
        formatter = logging.Formatter(Config.LOG_FORMAT)
        
        # Handler pour fichier général (avec rotation)
        app_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(Config.LOG_DIR, 'app.log'),
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        
        # Handler pour erreurs uniquement
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(Config.LOG_DIR, 'error.log'),
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler console (développement)
        if Config.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Ajouter les handlers
        self.logger.addHandler(app_handler)
        self.logger.addHandler(error_handler)
    
    def _get_user_context(self):
        """Récupère le contexte utilisateur pour les logs."""
        try:
            username = session.get('username', 'Anonymous')
            ip = request.remote_addr if request else 'Unknown'
            return f"User: {username} - IP: {ip}"
        except:
            return "User: Unknown - IP: Unknown"
    
    def info(self, message, include_user=True):
        """Log niveau INFO avec contexte utilisateur optionnel."""
        if include_user:
            message = f"{message} - {self._get_user_context()}"
        self.logger.info(message)
    
    def warning(self, message, include_user=True):
        """Log niveau WARNING avec contexte utilisateur optionnel."""
        if include_user:
            message = f"{message} - {self._get_user_context()}"
        self.logger.warning(message)
    
    def error(self, message, include_user=True, exc_info=False):
        """Log niveau ERROR avec contexte utilisateur optionnel."""
        if include_user:
            message = f"{message} - {self._get_user_context()}"
        self.logger.error(message, exc_info=exc_info)
    
    def debug(self, message, include_user=False):
        """Log niveau DEBUG (développement uniquement)."""
        if include_user:
            message = f"{message} - {self._get_user_context()}"
        self.logger.debug(message)
    
    # Méthodes avec préfixe log_ pour compatibilité
    def log_info(self, message, include_user=True):
        """Alias pour info()."""
        self.info(message, include_user)
    
    def log_warning(self, message, include_user=True):
        """Alias pour warning()."""
        self.warning(message, include_user)
    
    def log_error(self, message, include_user=True, exc_info=False):
        """Alias pour error()."""
        self.error(message, include_user, exc_info)
    
    def log_debug(self, message, include_user=False):
        """Alias pour debug()."""
        self.debug(message, include_user)


# Instance globale du logger
app_logger = AppLogger()

# Alias pour compatibilité
logger = app_logger

# Fonctions raccourcies pour utilisation simple
def log_info(message, include_user=True):
    """Raccourci pour log INFO."""
    app_logger.info(message, include_user)

def log_warning(message, include_user=True):
    """Raccourci pour log WARNING."""
    app_logger.warning(message, include_user)

def log_error(message, include_user=True, exc_info=False):
    """Raccourci pour log ERROR."""
    app_logger.error(message, include_user, exc_info)

def log_debug(message, include_user=False):
    """Raccourci pour log DEBUG."""
    app_logger.debug(message, include_user)
