# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer MLflow
# On installe uniquement MLflow car les dépendances du projet ne sont pas nécessaires pour simplement servir l'UI
RUN pip install mlflow

# Le volume /app/mlruns sera monté ici
# Le port 5000 sera exposé par docker-compose

# Commande pour lancer le serveur MLflow
# Le backend-store-uri pointe vers le volume qui sera partagé avec le conteneur ml-pipeline
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "/app/mlruns"]
