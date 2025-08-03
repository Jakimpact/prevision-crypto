from pydantic import BaseModel


class ForecastPairRequest(BaseModel):
    trading_pair_symbol: str
    num_pred: int