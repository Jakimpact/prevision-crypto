#!/bin/sh

# --- 1. Configuration et lancement des tâches Cron ---
echo "Configuration des tâches cron pour le pipeline ML..."

# Créer le fichier crontab
# Rediriger la sortie standard et d'erreur des crons vers les logs du conteneur
# Le décalage de 5 minutes assure que les données de E1-data sont à jour
echo "05 * * * * python /app/update_models_and_forecasts.py --granularity hour >> /var/log/cron.log 2>&1" > /etc/crontabs/root
echo "05 00 * * * python /app/update_models_and_forecasts.py --granularity day >> /var/log/cron.log 2>&1" >> /etc/crontabs/root

# Créer le fichier de log pour que cron puisse y écrire
touch /var/log/cron.log

echo "Tâches cron du pipeline ML configurées."

# --- 2. Démarrage du service Cron en avant-plan ---
echo "Démarrage du service cron..."
# L'option -f maintient cron en avant-plan, ce qui est nécessaire pour que le conteneur ne s'arrête pas
exec crond -f
