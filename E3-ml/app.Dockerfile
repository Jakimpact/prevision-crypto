# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application Streamlit
COPY src/ ./src

# Le port par défaut de Streamlit est 8501
EXPOSE 8501

# Commande pour lancer l'application Streamlit
# Le script principal est src/C10_app/app.py
CMD ["streamlit", "run", "src/C10_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
