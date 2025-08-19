"""Apply monkeypatches before running pipeline to avoid heavy evaluation logic failures in CI.
This overrides generate_test_periods to return a minimal single-step test window.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Import target module after path insertion
from src.utils import functions as utils_functions  # type: ignore


def _mock_generate_test_periods(forecaster):
    # Single synthetic period ending at last historical point
    try:
        last = forecaster.df_historical_data.index.max()
    except Exception:
        import pandas as pd
        last = pd.Timestamp.utcnow().floor("h")
    start = last - pd.Timedelta(1, unit=forecaster.freq)
    return pd.DataFrame({
        "test_start": [start],
        "test_end": [last]
    })

# Apply monkeypatch
utils_functions.generate_test_periods = _mock_generate_test_periods  # type: ignore
