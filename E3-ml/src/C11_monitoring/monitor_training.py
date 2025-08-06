import mlflow

import pandas as pd

from src.C9_model.evaluate_model import test_forecaster_past_performances
from src.settings import MLSettings, logger


def monitor_trainings(pair_forecasters, granularity):
    """Lance le monitoring des performances à l'entraînement des modèles."""

    if granularity == "hour":
        training_date = pd.Timestamp.utcnow().replace(minute=0, second=0, microsecond=0).tz_localize(None)
    elif granularity == "day":
        training_date = pd.Timestamp.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).tz_localize(None)

    mlflow.set_tracking_uri(MLSettings.ml_flow_tracking_uri)

    for forecaster in pair_forecasters:
        mlflow.set_experiment(f"{forecaster.symbol}_training_monitoring")

        with mlflow.start_run(run_name=f"{forecaster.granularity_type}_{training_date}"):
            mlflow.set_tag("symbol", forecaster.symbol)
            mlflow.set_tag("model", forecaster.model_name)
            mlflow.set_tag("granularity", forecaster.granularity_type)

            mlflow.log_params({
                "trading_pair_symbol": forecaster.symbol,
                "granularity": forecaster.granularity_type,
                "model_name": forecaster.model_name,
                "model_params": forecaster.model_params,
                "training_date": training_date,
                "test_period_duration": forecaster.test_period_duration,
                "test_period_duration_unit": forecaster.test_period_duration_unit,
            })

            mape, mae, direction_accuracy = test_forecaster_past_performances(forecaster)

            mlflow.log_metrics({
                "mape_score": round(mape, 2),
                "mae_score": round(mae, 2),
                "direction_accuracy": round(direction_accuracy, 2)
            })