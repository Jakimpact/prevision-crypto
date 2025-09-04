# Stage 1: Builder - Installe les dépendances
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Installer les dépendances système nécessaires pour compiler certaines librairies Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Final - L'image de production
FROM python:3.11-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Créer un utilisateur et un groupe non-root pour des raisons de sécurité
RUN addgroup --system app && adduser --system --group app

# Copier les dépendances installées depuis le stage 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le code source de l'application
COPY . .

# Créer les répertoires pour les logs et le monitoring et donner les permissions
RUN mkdir -p logs monitoring && \
    chown -R app:app $APP_HOME && \
    chmod -R 755 $APP_HOME

# Changer pour l'utilisateur non-root
USER app

# Exposer le port que Gunicorn utilisera
EXPOSE 8080

# Commande pour lancer l'application en production avec Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8080", "app:app"]
