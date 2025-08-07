from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVDaily, TradingPair


@with_session
def get_all_pairs_from_ohlcv_daily(session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading ayant des données OHLCV daily.
    
    Jointure SQL : TradingPair JOIN OHLCVDaily
    - Utilise .distinct() pour éviter les doublons et optimiser la requête.
    - Permet de ne sélectionner que les paires réellement présentes dans la table daily.
    - Optimisation : la jointure et le distinct évitent des sous-requêtes ou des scans inutiles.
    """
    return session.query(TradingPair)\
        .join(OHLCVDaily)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_daily_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVDaily]:
    """
    Récupère toutes les entrées OHLCV daily pour une paire de trading donnée.
    
    Filtrage : WHERE trading_pair_id = ...
    - Utilise un index sur trading_pair_id pour accélérer la recherche.
    """
    return session.query(OHLCVDaily)\
        .filter(OHLCVDaily.trading_pair_id == trading_pair_id)\
        .all()


@with_session
def get_last_ohlcv_daily_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVDaily:
    """
    Récupère la dernière entrée OHLCV daily pour une paire de trading donnée.
    
    Filtrage : WHERE trading_pair_id = ...
    - Utilise .order_by(desc(OHLCVDaily.date)) pour obtenir la plus récente.
    - Optimisation : .first() limite la requête à un seul résultat.
    """
    return session.query(OHLCVDaily)\
        .filter(OHLCVDaily.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVDaily.date.desc())\
        .first()
