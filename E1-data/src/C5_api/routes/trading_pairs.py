from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_db


router = APIRouter(
    prefix="/trading_pairs",
    tags=["trading_pairs"]
)


@router.get("/get_trading_pairs_by_base_currency_symbol/{symbol}")
def get_trading_pairs_by_base_currency_symbol(symbol: str, db=Depends(get_db)):
    """Récupère toutes les paires de trading pour lesquelles le symbole donné apparaît comme base currency."""
    trading_pairs = db.trading_pairs.get_pairs_by_base_currency_symbol(symbol.upper())
    return trading_pairs


@router.get("/get_trading_pair_by_currency_symbols/{base_symbol}-{quote_symbol}")
def get_trading_pair_by_currency_symbols(base_symbol: str, quote_symbol: str, db=Depends(get_db)):
    """Récupère une paire de trading à partir des symbols des currency base et quote."""
    trading_pair = db.trading_pairs.get_pair_by_currency_symbols(base_symbol.upper(), quote_symbol.upper())
    return trading_pair