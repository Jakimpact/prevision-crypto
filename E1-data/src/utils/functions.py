from datetime import datetime
from typing import Optional

import pandas as pd


def validate_date(date_str: Optional[str]) -> Optional[datetime]:
    """Convertit une chaîne de date en objet datetime."""
        
    try:
        # Essaie plusieurs formats courants
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Format de date non reconnu: {date_str}")
    except Exception as e:
        raise ValueError(f"Erreur de conversion de la date: {str(e)}")
    

def parse_date(date_str):
    """Convertit une chaîne de date en objet datetime, en essayant plusieurs formats."""
    
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT