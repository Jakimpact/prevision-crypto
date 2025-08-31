import time
import os
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash, session
try:
    import flask_monitoringdashboard as dashboard  # type: ignore
except Exception as _dash_import_err:  # pragma: no cover
    dashboard = None  # Fallback placeholder
from config import Config
from services.auth import auth_service
from services.forecast import forecast_service
from services.ohlcv import OHLCVService
from utils.auth import require_valid_token
from utils.datetime import convert_forecast_dates
from utils.logger import log_info, log_warning, log_error, log_debug
from utils.alerts import check_latency

# Initialisation des services
ohlcv_service = OHLCVService()

# Initialisation Flask
app = Flask(__name__)
app.config.from_object(Config)

DISABLE_MONITORING = os.getenv('DISABLE_MONITORING', '0') == '1'

# Initialisation et configuration du dashboard de monitoring
if not DISABLE_MONITORING and dashboard:
    try:
        # 1. Appliquer la configuration depuis les variables d'environnement
        dashboard.config.database_name = Config.MONITORING_DB_URI
        dashboard.config.username = Config.MONITORING_USERNAME
        dashboard.config.password = Config.MONITORING_PASSWORD
        dashboard.config.security_token = Config.MONITORING_SECURITY_TOKEN
        dashboard.config.link = Config.MONITORING_CUSTOM_LINK
        dashboard.config.timezone = pytz.timezone(Config.MONITORING_TIMEZONE)

    except Exception as e:  # pragma: no cover
        log_warning(f"Impossible d'initialiser le monitoring dashboard: {e}", include_user=False)
else:
    log_info("Monitoring dashboard désactivé (tests ou configuration)", include_user=False)


# Log du démarrage de l'application
log_info("Application E4 démarrée", include_user=False)


# =================== ROUTES FLASK ===================

@app.route('/')
def index():
    """Page de connexion (WF1)"""
    if 'user_id' in session:
        # Si utilisateur connecté, rediriger vers le dashboard
        return redirect(url_for('app_dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Traitement de la connexion"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validation basique
        if not username or not password:
            flash('Nom d\'utilisateur et mot de passe requis', 'error')
            return render_template('index.html')
        
        # Appel à l'API E1 pour authentification
        success, result = auth_service.login(username, password)
        
        if success:
            # Stockage des informations de session
            session['user_id'] = username
            session['username'] = username
            session['access_token'] = result.get('access_token')
            session['token_type'] = result.get('token_type', 'bearer')
            session['user_role'] = result.get('role', 'user')
            
            if remember_me:
                session.permanent = True
            
            # Log connexion réussie
            log_info(f"Connexion réussie - Utilisateur: {username}")
            
            flash(f'Connexion réussie ! Bienvenue {username}', 'success')
            return redirect(url_for('app_dashboard'))
        else:
            # Log tentative de connexion échouée
            log_warning(f"Tentative de connexion échouée - Utilisateur: {username} - Erreur: {result.get('detail', 'Erreur inconnue')}")
            
            # Affichage de l'erreur retournée par l'API
            error_message = result.get('detail', 'Erreur de connexion')
            flash(error_message, 'error')
    
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page et traitement de l'inscription"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validation basique
        if not username or not password:
            flash('Nom d\'utilisateur et mot de passe requis', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Le nom d\'utilisateur doit contenir au moins 3 caractères', 'error')
            return render_template('register.html')
        
        # Appel à l'API E1 pour créer le compte
        success, result = auth_service.register(username, password)
        
        if success:
            log_info(f"Nouveau compte créé - Utilisateur: {username}")
            flash(f'Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('index'))
        else:
            log_warning(f"Échec création compte - Utilisateur: {username} - Erreur: {result.get('detail', 'Erreur inconnue')}")
            # Affichage de l'erreur retournée par l'API
            error_message = result.get('detail', 'Erreur lors de la création du compte')
            flash(error_message, 'error')
    
    return render_template('register.html')


@app.route('/dashboard')
@require_valid_token
def app_dashboard():
    """Page principale après connexion (WF2)"""
    log_debug("Accès au dashboard")
    
    # Récupération des données utilisateur depuis la session
    user_data = {
        'username': session.get('username', 'Utilisateur'),
        'user_role': session.get('user_role', 'user'),
    }
    
    return render_template('dashboard.html', user=user_data)


@app.route('/logout')
def logout():
    """Déconnexion"""
    username = session.get('username', 'Utilisateur')
    log_info(f"Déconnexion - Utilisateur: {username}")
    session.clear()
    flash(f'Au revoir {username} ! Vous êtes déconnecté.', 'success')
    return redirect(url_for('index'))


@app.route('/forecast', methods=['GET', 'POST'])
@require_valid_token
def forecast():
    """Page de prévisions crypto"""
    if request.method == 'POST':
        # Récupération des données du formulaire
        trading_pair = request.form.get('trading_pair', '').strip()
        granularity = request.form.get('granularity', '').strip()
        num_pred_str = request.form.get('num_pred', '').strip()
        
        # Validation des données
        if not all([trading_pair, granularity, num_pred_str]):
            flash('Tous les champs sont requis', 'error')
            return render_template('forecast.html')
        
        try:
            num_pred = int(num_pred_str)
        except ValueError:
            flash('Horizon de prévision invalide', 'error')
            return render_template('forecast.html')
        
        # Validation des paramètres via le service
        valid, error_msg = forecast_service.validate_forecast_params(trading_pair, granularity, num_pred)
        if not valid:
            flash(error_msg, 'error')
            return render_template('forecast.html')
        
        # Appel au service de prévision
        import time
        start_time = time.time()
        success, result = forecast_service.get_forecast(trading_pair, granularity, num_pred)
        api_duration = time.time() - start_time
        
        if success:
            # Formatage des résultats pour le template
            dates_utc = result.get("forecast_dates", [])
            predictions = result.get("forecast", [])
            
            # Log prévision réussie
            log_info(f"Prévision générée - Paire: {trading_pair} - Granularité: {granularity} - Points: {len(predictions)}")
            
            # Conversion des dates UTC vers timezone Paris avec format selon granularité
            dates_paris = convert_forecast_dates(dates_utc, granularity)
            
            # Création des paires (date, prix) pour le template
            forecast_result = list(zip(dates_paris, predictions))
            
            # Paramètres pour affichage
            forecast_params = {
                'trading_pair': trading_pair,
                'granularity': granularity,
                'num_pred': num_pred
            }
            
            flash(f'Prévision réalisée avec succès ! {len(predictions)} points prédits.', 'success')
            # Log latence prévision (ms)
            try:
                log_info(
                    f"Latence prévision - Paire: {trading_pair} - Granularité: {granularity} - Duree_ms: {int(api_duration * 1000)}"
                )
                # Vérification seuils (alerte éventuelle)
                check_latency(
                    'forecast_ms',
                    int(api_duration * 1000),
                    context={
                        'pair': trading_pair,
                        'granularity': granularity,
                        'points': len(predictions)
                    }
                )
            except Exception:
                pass
            return render_template('forecast.html', 
                                 forecast_result=forecast_result, 
                                 forecast_params=forecast_params)
        else:
            error_message = result.get('error', 'Erreur lors de la prévision')
            log_warning(
                f"Échec prévision - Paire: {trading_pair} - Duree_ms: {int(api_duration * 1000)} - Erreur: {error_message}"
            )
            # Même en cas d'échec on peut déclencher une alerte de latence
            try:
                check_latency(
                    'forecast_ms',
                    int(api_duration * 1000),
                    context={
                        'pair': trading_pair,
                        'granularity': granularity,
                        'status': 'error'
                    }
                )
            except Exception:
                pass
            flash(error_message, 'error')
    
    return render_template('forecast.html')


@app.route('/charts')
@require_valid_token
def charts():
    """Page de visualisation des graphiques (WF3)"""
    log_debug("Accès à la page graphiques")
    return render_template('charts.html')


@app.route('/api/chart-data')
@require_valid_token
def api_chart_data():
    """API pour récupérer les données de graphiques"""
    # Paramètres de la requête
    base_symbol = request.args.get('base', 'BTC')
    quote_symbol = request.args.get('quote', 'USDT')
    granularity = request.args.get('granularity', 'hourly')
    
    log_debug(f"Appel API chart-data - Paire: {base_symbol}/{quote_symbol} - Granularité: {granularity}")
    
    try:
        # Récupération de toutes les données disponibles via le service OHLCV avec métriques
        start_time = time.time()
        
        ohlcv_data, forecast_data, trading_pair = ohlcv_service.get_all_data(
            base_symbol=base_symbol,
            quote_symbol=quote_symbol,
            granularity=granularity
        )
        
        api_duration = time.time() - start_time
        
        if not trading_pair:
            log_warning(f"Paire de trading non trouvée - {base_symbol}/{quote_symbol}")
            return {
                'error': f'Paire de trading {base_symbol}/{quote_symbol} non trouvée'
            }, 404
                
        # Formatage des données pour les graphiques
        chart_data = ohlcv_service.format_chart_data(ohlcv_data, forecast_data)
        
        # Ajout des informations sur la paire
        chart_data['trading_pair'] = {
            'id': trading_pair.get('id'),
            'base_symbol': base_symbol,
            'quote_symbol': quote_symbol,
            'display_name': f"{base_symbol}/{quote_symbol}"
        }
        
        # Ajout des paramètres de la requête
        chart_data['params'] = {
            'granularity': granularity
        }
        
        # Log latence en cas de succès
        try:
            log_info(
                f"Latence chart-data - Paire: {base_symbol}/{quote_symbol} - Granularité: {granularity} - Bougies: {len(ohlcv_data)} - Duree_ms: {int(api_duration * 1000)}"
            )
            # Vérification des seuils de latence
            check_latency(
                'chart_data_ms',
                int(api_duration * 1000),
                context={
                    'pair': f"{base_symbol}/{quote_symbol}",
                    'granularity': granularity,
                    'ohlcv_count': len(ohlcv_data) if ohlcv_data else 0,
                    'forecast_count': len(forecast_data) if forecast_data else 0
                }
            )
        except Exception:
            pass
        return chart_data
        
    except Exception as e:
        try:
            api_duration = time.time() - start_time
            log_error(
                f"Erreur récupération données graphiques - Duree_ms: {int(api_duration * 1000)} - Erreur: {str(e)}",
                exc_info=True
            )
            try:
                # Alerte éventuelle sur la latence malgré l'erreur
                check_latency(
                    'chart_data_ms',
                    int(api_duration * 1000),
                    context={
                        'pair': f"{base_symbol}/{quote_symbol}",
                        'granularity': granularity,
                        'status': 'error'
                    }
                )
            except Exception:
                pass
        except Exception:
            log_error(f"Erreur récupération données graphiques: {str(e)}", exc_info=True)
        print(f"Erreur lors de la récupération des données de graphiques: {e}")
        return {
            'error': 'Erreur lors de la récupération des données'
        }, 500


# =================== GESTION D'ERREURS ===================

@app.errorhandler(404)
def not_found(error):
    """Page 404"""
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Page 500"""
    flash('Erreur interne du serveur', 'error')
    return render_template('base.html'), 500


# =================== LANCEMENT ===================

# Initialisation et configuration du dashboard de monitoring
if not DISABLE_MONITORING and dashboard:
        dashboard.bind(app)
        log_info("Monitoring dashboard initialisé et configuré.", include_user=False)


if __name__ == '__main__':
    # Affichage des informations de démarrage
    log_info(f"Démarrage serveur sur {Config.HOST}:{Config.PORT}", include_user=False)

    # Utilisation de la configuration centralisée
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )