# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn "uvicorn[standard]"

# Copier le code source de l'API
COPY src/ ./src

# Le port interne de l'API sera 8002
EXPOSE 8002

# Commande pour lancer l'API avec Gunicorn et des workers Uvicorn
# Le point d'entrée de l'application FastAPI est 'app' dans le fichier src/C9_api/api.py
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8002", "src.C9_api.api:app"]
