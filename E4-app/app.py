from flask import Flask, render_template, request, redirect, url_for, flash, session
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import os
from config import Config

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
        
        # TODO: Appel à l'API E1 pour authentification
        # Pour le moment, authentification factice
        if username and password:
            # Simulation d'une authentification réussie
            session['user_id'] = username
            session['username'] = username
            
            if remember_me:
                session.permanent = True
            
            flash(f'Connexion réussie ! Bienvenue {username}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants invalides', 'error')
    
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
        
        # TODO: Appel à l'API E1 pour créer le compte
        # Pour le moment, création factice
        try:
            # Simulation d'une création réussie
            flash(f'Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Erreur lors de la création du compte', 'error')
    
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    """Page principale après connexion (WF2)"""
    if 'user_id' not in session:
        flash('Vous devez être connecté pour accéder à cette page', 'warning')
        return redirect(url_for('index'))
    
    # TODO: Récupérer les données via APIs E1 et E3
    # Pour le moment, données factices
    user_data = {
        'username': session.get('username', 'Utilisateur'),
        'last_login': 'Aujourd\'hui'
    }
    
    return render_template('dashboard.html', user=user_data)


@app.route('/logout')
def logout():
    """Déconnexion"""
    username = session.get('username', 'Utilisateur')
    session.clear()
    flash(f'Au revoir {username} ! Vous êtes déconnecté.', 'success')
    return redirect(url_for('index'))


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


# =================== FONCTIONS UTILITAIRES ===================

def is_authenticated():
    """Vérifie si l'utilisateur est connecté"""
    return 'user_id' in session


# =================== LANCEMENT ===================

if __name__ == '__main__':
    # Utilisation de la configuration centralisée
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )