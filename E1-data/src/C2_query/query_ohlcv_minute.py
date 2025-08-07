from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVMinute, TradingPair


@with_session
def get_all_pairs_from_ohlcv_minute(session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading ayant des données OHLCV minute.
    
    Jointure SQL : TradingPair JOIN OHLCVMinute
    - Utilise .distinct() pour éviter les doublons et optimiser la requête.
    - Permet de ne sélectionner que les paires réellement présentes dans la table minute.
    - Optimisation : la jointure et le distinct évitent des sous-requêtes ou des scans inutiles.
    """
    return session.query(TradingPair)\
        .join(OHLCVMinute)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_minute_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVMinute]:
    """
    Récupère toutes les entrées OHLCV minute pour une paire de trading donnée.
    
    Filtrage : WHERE trading_pair_id = ...
    - Utilise un index sur trading_pair_id pour accélérer la recherche.
    """
    return session.query(OHLCVMinute)\
        .filter(OHLCVMinute.trading_pair_id == trading_pair_id)\
        .all()