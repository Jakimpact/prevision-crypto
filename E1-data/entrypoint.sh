#!/bin/bash

# Chemin vers le fichier de verrouillage
INIT_LOCK_FILE="/app/config/.initialized"

# --- 1. Sauvegarde de l'environnement pour Cron ---
echo "Sauvegarde des variables d'environnement pour cron..."
printenv | grep -v "no_proxy" > /etc/environment

# --- 2. Exécution unique du script d'initialisation ---
if [ ! -f "$INIT_LOCK_FILE" ]; then
    echo "Première exécution : Lancement du script d'initialisation de la base de données..."
    
    # Exécuter le script d'initialisation
    /app/.venv/bin/python init_db_and_data.py
    
    # Vérifier si le script a réussi avant de créer le fichier de verrouillage
    if [ $? -eq 0 ]; then
        echo "Initialisation terminée avec succès. Création du fichier de verrouillage."
        # Créer le fichier de verrouillage dans le volume de configuration
        touch $INIT_LOCK_FILE
    else
        echo "ERREUR : Le script d'initialisation a échoué. Le conteneur va s'arrêter."
        exit 1
    fi
else
    echo "L'initialisation a déjà été effectuée. Démarrage normal."
fi

# --- 3. Configuration et lancement des tâches Cron ---
echo "Configuration des tâches cron..."

# Créer le fichier crontab pour un environnement Debian
CRON_FILE="/etc/cron.d/data-cron"
# Utiliser bash -c pour s'assurer que l'environnement est chargé
echo '02 * * * * root bash -c "source /etc/environment && /app/.venv/bin/python /app/update_ohlcv.py --frequency hour >> /var/log/cron.log 2>&1"' > $CRON_FILE
echo '01 00 * * * root bash -c "source /etc/environment && /app/.venv/bin/python /app/update_ohlcv.py --frequency day >> /var/log/cron.log 2>&1"' >> $CRON_FILE

# Donner les permissions nécessaires au fichier cron
chmod 0644 $CRON_FILE

# Créer le fichier de log pour que cron puisse y écrire
touch /var/log/cron.log

echo "Tâches cron configurées."

# --- 4. Démarrage du service Cron en avant-plan ---
echo "Démarrage du service cron..."
# L'option -f maintient cron en avant-plan, ce qui est nécessaire pour que le conteneur ne s'arrête pas
exec cron -f
