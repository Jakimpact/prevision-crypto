from typing import List

from sqlalchemy.orm import Session

from src.C4_database.database import with_session
from src.C4_database.models import OHLCVHourly, TradingPair


@with_session
def get_all_pairs_from_ohlcv_hourly(session: Session = None) -> List[TradingPair]:
    """
    Récupère toutes les paires de trading ayant des données OHLCV hourly.
    
    Jointure SQL : TradingPair JOIN OHLCVHourly
    - Utilise .distinct() pour éviter les doublons et optimiser la requête.
    - Permet de ne sélectionner que les paires réellement présentes dans la table hourly.
    - Optimisation : la jointure et le distinct évitent des sous-requêtes ou des scans inutiles.
    """
    return session.query(TradingPair)\
        .join(OHLCVHourly)\
        .distinct()\
        .all()


@with_session
def get_ohlcv_hourly_by_pair_id(trading_pair_id: int, session: Session = None) -> List[OHLCVHourly]:
    """
    Récupère toutes les entrées OHLCV hourly pour une paire de trading donnée.
    
    Filtrage : WHERE trading_pair_id = ...
    - Utilise un index sur trading_pair_id pour accélérer la recherche.
    """
    return session.query(OHLCVHourly)\
        .filter(OHLCVHourly.trading_pair_id == trading_pair_id)\
        .all()


@with_session
def get_last_ohlcv_hourly_by_pair_id(trading_pair_id: int, session: Session = None) -> OHLCVHourly:
    """
    Récupère la dernière entrée OHLCV hourly pour une paire de trading donnée.
    
    Filtrage : WHERE trading_pair_id = ...
    - Utilise .order_by(desc(OHLCVHourly.date)) pour obtenir la plus récente.
    - Optimisation : .first() limite la requête à un seul résultat.
    """
    return session.query(OHLCVHourly)\
        .filter(OHLCVHourly.trading_pair_id == trading_pair_id)\
        .order_by(OHLCVHourly.date.desc())\
        .first()
