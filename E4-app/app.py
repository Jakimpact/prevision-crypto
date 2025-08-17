from flask import Flask, render_template, request, redirect, url_for, flash, session
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import os
from config import Config
from services.auth import auth_service
from services.forecast import forecast_service
from utils.auth import is_authenticated, get_auth_headers, get_current_user
from utils.datetime import convert_forecast_dates

# Initialisation Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation Dash
dash_app = dash.Dash(__name__, server=app, url_base_pathname=Config.DASH_URL_BASE_PATHNAME)

# Configuration de base pour Dash
dash_app.layout = html.Div([
    html.H1("Dashboard Crypto", style={'text-align': 'center'}),
    html.P("Interface Dash en cours de développement...", style={'text-align': 'center'})
])


# =================== ROUTES FLASK ===================

@app.route('/')
def index():
    """Page de connexion (WF1)"""
    if 'user_id' in session:
        # Si utilisateur connecté, rediriger vers le dashboard
        return redirect(url_for('dashboard'))
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
            
            flash(f'Connexion réussie ! Bienvenue {username}', 'success')
            return redirect(url_for('dashboard'))
        else:
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
            flash(f'Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('index'))
        else:
            # Affichage de l'erreur retournée par l'API
            error_message = result.get('detail', 'Erreur lors de la création du compte')
            flash(error_message, 'error')
    
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    """Page principale après connexion (WF2)"""
    if not is_authenticated():
        flash('Vous devez être connecté pour accéder à cette page', 'warning')
        return redirect(url_for('index'))
    
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
    session.clear()
    flash(f'Au revoir {username} ! Vous êtes déconnecté.', 'success')
    return redirect(url_for('index'))

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    """Page de prévisions crypto"""
    if not is_authenticated():
        flash('Vous devez être connecté pour accéder aux prévisions', 'warning')
        return redirect(url_for('index'))
    
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
        success, result = forecast_service.get_forecast(trading_pair, granularity, num_pred)
        
        if success:
            # Formatage des résultats pour le template
            dates_utc = result.get("forecast_dates", [])
            predictions = result.get("forecast", [])
            
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
            return render_template('forecast.html', 
                                 forecast_result=forecast_result, 
                                 forecast_params=forecast_params)
        else:
            error_message = result.get('error', 'Erreur lors de la prévision')
            flash(error_message, 'error')
    
    return render_template('forecast.html')


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

if __name__ == '__main__':
    # Utilisation de la configuration centralisée
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )