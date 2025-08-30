#!/bin/sh

# Chemin vers le fichier de verrouillage
INIT_LOCK_FILE="/app/config/.initialized"

# --- 1. Exécution unique du script d'initialisation ---
if [ ! -f "$INIT_LOCK_FILE" ]; then
    echo "Première exécution : Lancement du script d'initialisation de la base de données..."
    
    # Exécuter le script d'initialisation
    python init_db_and_data.py
    
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

# --- 2. Configuration et lancement des tâches Cron ---
echo "Configuration des tâches cron..."

# Créer le fichier crontab
# Rediriger la sortie standard et d'erreur des crons vers les logs du conteneur
echo "01 * * * * python /app/update_ohlcv.py --frequency hour >> /var/log/cron.log 2>&1" > /etc/crontabs/root
echo "01 00 * * * python /app/update_ohlcv.py --frequency day >> /var/log/cron.log 2>&1" >> /etc/crontabs/root

# Créer le fichier de log pour que cron puisse y écrire
touch /var/log/cron.log

echo "Tâches cron configurées."

# --- 3. Démarrage du service Cron en avant-plan ---
echo "Démarrage du service cron..."
# L'option -f maintient cron en avant-plan, ce qui est nécessaire pour que le conteneur ne s'arrête pas
exec crond -f
