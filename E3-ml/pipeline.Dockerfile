# Utiliser une image Python légère
FROM python:3.9-slim

# Installer cron
RUN apt-get update && apt-get install -y cron

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source et les scripts nécessaires
COPY src/ ./src
COPY update_models_and_forecasts.py .

# Copier le script d'entrée et le rendre exécutable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Définir le point d'entrée
ENTRYPOINT ["./entrypoint.sh"]
