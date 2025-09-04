# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copier le code source de l'API
COPY src/ ./src

# Le script de l'API est dans src/C5_api/api.py
# Le port interne de l'API sera 8001
EXPOSE 8001

# Commande pour lancer l'API avec Gunicorn en utilisant un worker Uvicorn pour FastAPI
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001", "src.C5_api.api:app"]
