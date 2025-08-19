"""Minimal mock of the external E1 API used in CI so the training pipeline can run
without needing the real service running on localhost:8000.

Placed under src/C12_tests/mocks so it stays clearly in test scope.

Served endpoints (subset):
POST /api/v1/authentification/login -> returns {"access_token": "dummy-token"}
GET  /api/v1/ohlcv/hourly_by_trading_pair_id/{id}
GET  /api/v1/ohlcv/daily_by_trading_pair_id/{id}
POST /api/v1/forecast/hourly
POST /api/v1/forecast/daily

The OHLCV endpoints return synthetic deterministic data with fields:
  date, trading_pair_id, close
Big enough history to satisfy model lag requirements (>= max lags 24 for hourly, 7 for daily).
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, Path

app = FastAPI(title="Mock E1 API")


def _generate_series(trading_pair_id: int, granularity: str):
    if granularity == "hourly":
        points = 24 * 10  # 10 days
        delta = timedelta(hours=1)
    elif granularity == "daily":
        points = 120
        delta = timedelta(days=1)
    else:
        points = 10
        delta = timedelta(minutes=1)

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start = now - (points * delta)
    data = []
    for i in range(points):
        ts = start + i * delta
        close = 100 + trading_pair_id % 50 + i * 0.1
        data.append({
            "date": ts.isoformat(),
            "trading_pair_id": trading_pair_id,
            "close": close,
        })
    return data


@app.post("/api/v1/authentification/login")
async def login():  # Accept any credentials
    return {"access_token": "dummy-token"}


@app.get("/api/v1/ohlcv/hourly_by_trading_pair_id/{trading_pair_id}")
async def ohlcv_hourly(trading_pair_id: int = Path(...)):
    return _generate_series(trading_pair_id, "hourly")


@app.get("/api/v1/ohlcv/daily_by_trading_pair_id/{trading_pair_id}")
async def ohlcv_daily(trading_pair_id: int = Path(...)):
    return _generate_series(trading_pair_id, "daily")


@app.post("/api/v1/forecast/hourly")
async def post_forecast_hourly():
    return {"status": "ok"}


@app.post("/api/v1/forecast/daily")
async def post_forecast_daily():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.C12_tests.mocks.ci_mock_e1_api:app", host="0.0.0.0", port=8000)
