#!/bin/bash

# --- 1. Sauvegarde de l'environnement pour Cron ---
echo "Sauvegarde des variables d'environnement pour cron..."
printenv | grep -v "no_proxy" > /etc/environment

# --- 2. Configuration et lancement des tâches Cron ---
echo "Configuration des tâches cron pour le pipeline ML..."

# Créer le fichier crontab pour un environnement Debian
CRON_FILE="/etc/cron.d/ml-cron"
# Le décalage de 5 minutes assure que les données de E1-data sont à jour
# Utiliser bash -c pour s'assurer que l'environnement est chargé
echo '05 * * * * root bash -c "source /etc/environment && /app/.venv/bin/python /app/update_models_and_forecasts.py --granularity hour >> /var/log/cron.log 2>&1"' > $CRON_FILE
echo '03 00 * * * root bash -c "source /etc/environment && /app/.venv/bin/python /app/update_models_and_forecasts.py --granularity day >> /var/log/cron.log 2>&1"' >> $CRON_FILE

# Donner les permissions nécessaires au fichier cron
chmod 0644 $CRON_FILE

# Créer le fichier de log pour que cron puisse y écrire
touch /var/log/cron.log

echo "Tâches cron du pipeline ML configurées."

# --- 3. Démarrage du service Cron en avant-plan ---
echo "Démarrage du service cron..."
# L'option -f maintient cron en avant-plan, ce qui est nécessaire pour que le conteneur ne s'arrête pas
exec cron -f
