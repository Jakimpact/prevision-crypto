from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVMinute


@with_session
def get_last_ohlcv_minute_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVMinute:
    """
    Récupère la dernière entrée OHLCV minute pour une paire de trading donnée.
    Filtrage sur trading_pair_id et tri décroissant sur la date pour obtenir la plus récente.
    Utilisation de .first() pour ne retourner qu'un seul résultat.
    """
    return session.query(OHLCVMinute)\
        .filter(OHLCVMinute.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVMinute.date.desc())\
        .first()
