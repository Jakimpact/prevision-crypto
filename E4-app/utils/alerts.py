"""Utility d'alertes basées sur les seuils définis dans Config.THRESHOLDS.
"""
from __future__ import annotations
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from config import Config
from utils.logger import log_warning, log_error

# Fichier de sortie des alertes (JSON Lines)
ALERTS_FILE = os.path.join(Config.LOG_DIR, 'alerts.jsonl')

# S'assure que le répertoire des logs existe
os.makedirs(Config.LOG_DIR, exist_ok=True)

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def write_alert(alert: Dict[str, Any]) -> None:
    """Écrit une alerte (dict) en JSON sur une ligne dans le fichier dédié."""
    try:
        with open(ALERTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + '\n')
    except Exception as e:
        # Dernier recours: log d'erreur (ne pas relancer d'exception pour ne pas casser le flux principal)
        log_error(f"Echec écriture alerte: {e}", include_user=False)

def check_latency(metric_key: str, duration_ms: int, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Vérifie la latence mesurée contre les seuils.

    Args:
        metric_key: 'forecast_ms' ou 'chart_data_ms'.
        duration_ms: durée mesurée en millisecondes.
        context: informations additionnelles (paire, granularité, etc.).
    Returns:
        Le niveau d'alerte ('WARNING' | 'CRITICAL') ou None si aucun dépassement.
    """
    context = context or {}
    try:
        latency_cfg = Config.THRESHOLDS.get('latency', {})
        metric_cfg = latency_cfg.get(metric_key)
        if not metric_cfg:
            return None  # métrique non configurée

        warning_th = metric_cfg.get('warning')
        critical_th = metric_cfg.get('critical')
        level = None
        threshold_used = None

        if critical_th is not None and duration_ms > critical_th:
            level = 'CRITICAL'
            threshold_used = critical_th
        elif warning_th is not None and duration_ms > warning_th:
            level = 'WARNING'
            threshold_used = warning_th

        if level:
            alert = {
                'ts': _utc_now_iso(),
                'metric': metric_key,
                'value_ms': duration_ms,
                'threshold_ms': threshold_used,
                'level': level,
                'context': context,
            }
            write_alert(alert)
            # Journalisation dans les logs existants
            if level == 'CRITICAL':
                log_error(
                    f"ALERTE CRITIQUE latence {metric_key} - {duration_ms}ms (> {threshold_used}ms) - contexte={context}",
                    include_user=False
                )
            else:
                log_warning(
                    f"Alerte latence {metric_key} - {duration_ms}ms (> {threshold_used}ms) - contexte={context}",
                    include_user=False
                )
            return level
        return None
    except Exception as e:
        log_error(f"Erreur check_latency {metric_key}: {e}", include_user=False)
        return None
