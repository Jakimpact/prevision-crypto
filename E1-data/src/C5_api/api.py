import sys
from pathlib import Path

from fastapi import FastAPI
import uvicorn

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from src.settings import logger
from src.C5_api.routes import login, ohlcv, trading_pairs


app = FastAPI(
    title="Crypto API",
    description="API pour accéder aux données de cryptomonnaies",
    version="1.0.0"
)

app.include_router(login.router, prefix="/api/v1")
app.include_router(trading_pairs.router, prefix="/api/v1")
app.include_router(ohlcv.router, prefix="/api/v1")


if __name__ == "__main__":
    logger.info("Démarrage du serveur API")
    uvicorn.run(
        "src.C5_api.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # EN DEV -> Paramètre pour recharger automatiquement le serveur lors des modifications du code
    )