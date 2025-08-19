"""Run the ML training pipeline with mocked persistence (forecasts sending + model saving)
without altering production source files.

Usage:
  python src/C12_tests/mocks/run_pipeline_with_mocks.py --granularity hour
"""
import sys
from pathlib import Path

# Ensure project root on path (same as original script behavior)
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Import the pipeline module AFTER path tweak
import update_models_and_forecasts as pipeline  # type: ignore

# (Optional) import logger if available
try:
    from src.settings import logger
except Exception:
    class _Dummy:  # fallback simple print wrapper
        def info(self, msg):
            print(msg)
    logger = _Dummy()


def mock_save_forecasters_models(pair_forecasters, granularity):
    logger.info(f"[MOCK] Skipping saving {len(pair_forecasters)} model(s) for granularity={granularity}")


def mock_save_forecasts_to_db(pair_forecasters):
    logger.info(f"[MOCK] Skipping sending {sum(len(f.current_forecast) for f in pair_forecasters)} forecast row(s) for {len(pair_forecasters)} forecaster(s)")

# Monkeypatch symbols imported in pipeline module
pipeline.save_forecasters_models = mock_save_forecasters_models  # type: ignore
pipeline.save_forecasts_to_db = mock_save_forecasts_to_db  # type: ignore

if __name__ == "__main__":
    # Delegate to original CLI parsing logic (argparse inside pipeline.main())
    pipeline.main()
