import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd

from src.C10_app.utils import get_forecast, get_jwt_token
from src.settings import DataSettings


st.set_page_config(page_title="Prévision Crypto", layout="centered")

st.title("Bienvenue sur l'application 'POC' de prévision crypto")
st.write("Utilisez cette interface pour réaliser des prévisions concernant le cours de cryptomonnaies.")

# Texte d'information en haut
st.info(
    "Ce POC permet de réaliser des prévisions sur les paires de trading **BTC-USDT** et **ETH-USDT**. "
    "Vous pouvez choisir une granularité horaire (jusqu'à 24 heures de prévision) ou journalière (jusqu'à 7 jours de prévision)."
)

# Barre latérale pour choisir la granularité
granularity = st.sidebar.radio(
    "Choix de la granularité de prévision :",
    ("Prévision horaire", "Prévision journalière")
)

# Formulaire dynamique
with st.form("forecast_form"):
    pair = st.selectbox("Sélectionnez la paire de trading :", ["BTC-USDT", "ETH-USDT"])
    if granularity == "Prévision horaire":
        num_pred = st.number_input("Nombre d'heures à prévoir (1-24) :", min_value=1, max_value=24, value=1)
    else:
        num_pred = st.number_input("Nombre de jours à prévoir (1-7) :", min_value=1, max_value=7, value=1)
    submitted = st.form_submit_button("Lancer la prévision")

# Appel API et affichage du résultat
if submitted:
    try:
        token = get_jwt_token()
        if granularity == "Prévision horaire":
            forecast_url = DataSettings.E3_api_post_forecast_urls["hourly"]
        else:
            forecast_url = DataSettings.E3_api_post_forecast_urls["daily"]
        result = get_forecast(token, pair, num_pred, forecast_url)
        st.success("Prévision réalisée avec succès !")
        dates = result.get("forecast_dates", [])
        preds = result.get("forecast", [])
        # Mise en forme des valeurs
        preds_fmt = [f"{round(val)} $" for val in preds]
        # Mise en forme des dates UTC
        dates_fmt = [f"{date} (UTC)" for date in dates]
        df = pd.DataFrame({"Date (UTC)": dates_fmt, "Prédiction": preds_fmt})
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la prévision : {e}")

