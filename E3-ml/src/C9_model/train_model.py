import pandas as pd


def train_model(model, timeseries, freq, training_end):
    """Entraîne le modèle jusqu'à une date précise qui sera exclus."""

    training_end = training_end - pd.Timedelta(1, unit=freq)
    timeseries = timeseries["close"]
    model.fit(series=timeseries[:training_end])