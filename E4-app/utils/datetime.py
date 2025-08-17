from datetime import datetime
from typing import List, Union, Optional
import pytz

# Timezone de Paris (gère automatiquement CET/CEST)
PARIS_TZ = pytz.timezone('Europe/Paris')
UTC_TZ = pytz.timezone('UTC')

def utc_to_paris(utc_datetime_str: str, input_format: str = None) -> str:
    """
    Convertit une date/heure UTC en timezone Paris
    
    Args:
        utc_datetime_str: Date en string UTC
        input_format: Format d'entrée (auto-détection si None)
        
    Returns:
        String de la date/heure convertie au timezone Paris
    """
    try:
        # Auto-détection du format si non spécifié
        if input_format is None:
            # Formats courants des APIs
            formats_to_try = [
                "%Y-%m-%d %H:%M:%S",      # 2025-01-17 14:30:00
                "%Y-%m-%dT%H:%M:%S",      # 2025-01-17T14:30:00
                "%Y-%m-%dT%H:%M:%SZ",     # 2025-01-17T14:30:00Z
                "%Y-%m-%dT%H:%M:%S.%f",   # 2025-01-17T14:30:00.123456
                "%Y-%m-%dT%H:%M:%S.%fZ",  # 2025-01-17T14:30:00.123456Z
                "%Y-%m-%d",               # 2025-01-17 (jour seulement)
            ]
            
            parsed_datetime = None
            for fmt in formats_to_try:
                try:
                    parsed_datetime = datetime.strptime(utc_datetime_str, fmt)
                    break
                except ValueError:
                    continue
                    
            if parsed_datetime is None:
                raise ValueError(f"Format de date non reconnu: {utc_datetime_str}")
        else:
            parsed_datetime = datetime.strptime(utc_datetime_str, input_format)
        
        # Assigner le timezone UTC
        utc_datetime = UTC_TZ.localize(parsed_datetime)
        
        # Convertir vers Paris
        paris_datetime = utc_datetime.astimezone(PARIS_TZ)
        
        # Formater pour l'affichage (avec timezone)
        return paris_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
        
    except Exception as e:
        # En cas d'erreur, retourner la date originale avec un indicateur
        return f"{utc_datetime_str} (UTC)"

def utc_to_paris_simple(utc_datetime_str: str) -> str:
    """
    Version simplifiée sans indicateur de timezone dans l'affichage
    
    Args:
        utc_datetime_str: Date en string UTC
        
    Returns:
        String de la date/heure convertie (sans indicateur de timezone)
    """
    try:
        # Auto-détection du format
        formats_to_try = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]
        
        parsed_datetime = None
        for fmt in formats_to_try:
            try:
                parsed_datetime = datetime.strptime(utc_datetime_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_datetime is None:
            return utc_datetime_str  # Retourner l'original si échec
        
        # Conversion UTC -> Paris
        utc_datetime = UTC_TZ.localize(parsed_datetime)
        paris_datetime = utc_datetime.astimezone(PARIS_TZ)
        
        # Format simple sans timezone
        return paris_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception:
        return utc_datetime_str

def convert_forecast_dates(dates: List[str], granularity: str = "hourly") -> List[str]:
    """
    Convertit une liste de dates UTC vers le timezone Paris
    Spécialement conçue pour les résultats de forecast
    
    Args:
        dates: Liste des dates UTC
        granularity: "hourly" (avec heures) ou "daily" (date seulement)
        
    Returns:
        Liste des dates converties au timezone Paris
    """
    converted_dates = []
    for date_str in dates:
        if granularity == "daily":
            converted_dates.append(utc_to_paris_date_only(date_str))
        else:
            converted_dates.append(utc_to_paris_simple(date_str))
    
    return converted_dates

def utc_to_paris_date_only(utc_datetime_str: str) -> str:
    """
    Convertit une date UTC vers Paris et affiche seulement la date (sans heure)
    
    Args:
        utc_datetime_str: Date en string UTC
        
    Returns:
        String de la date convertie (format: YYYY-MM-DD)
    """
    try:
        # Auto-détection du format
        formats_to_try = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",  # Déjà en format date seulement
        ]
        
        parsed_datetime = None
        for fmt in formats_to_try:
            try:
                parsed_datetime = datetime.strptime(utc_datetime_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_datetime is None:
            return utc_datetime_str  # Retourner l'original si échec
        
        # Conversion UTC -> Paris
        utc_datetime = UTC_TZ.localize(parsed_datetime)
        paris_datetime = utc_datetime.astimezone(PARIS_TZ)
        
        # Format date seulement
        return paris_datetime.strftime("%Y-%m-%d")
        
    except Exception:
        return utc_datetime_str

def get_current_paris_time() -> str:
    """
    Retourne l'heure actuelle au timezone Paris
    
    Returns:
        String de l'heure actuelle à Paris
    """
    now_utc = datetime.now(UTC_TZ)
    now_paris = now_utc.astimezone(PARIS_TZ)
    return now_paris.strftime("%Y-%m-%d %H:%M:%S %Z")

def format_date_for_display(date_str: str, show_seconds: bool = True) -> str:
    """
    Formate une date pour l'affichage en interface utilisateur
    
    Args:
        date_str: Date string (sera convertie de UTC vers Paris)
        show_seconds: Afficher les secondes ou non
        
    Returns:
        Date formatée pour affichage
    """
    try:
        # Conversion UTC vers Paris
        paris_date = utc_to_paris_simple(date_str)
        
        # Re-parser pour formater selon les préférences
        dt = datetime.strptime(paris_date, "%Y-%m-%d %H:%M:%S")
        
        if show_seconds:
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return dt.strftime("%d/%m/%Y %H:%M")
            
    except Exception:
        return date_str  # Retourner l'original si échec
