from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVDaily


@with_session
def get_last_ohlcv_daily_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVDaily:
    """
    Récupère la dernière entrée OHLCV daily pour une paire de trading donnée.
    Filtrage sur trading_pair_id et tri décroissant sur la date pour obtenir la plus récente.
    Utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return session.query(OHLCVDaily)\
        .filter(OHLCVDaily.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVDaily.date.desc())\
        .first()
