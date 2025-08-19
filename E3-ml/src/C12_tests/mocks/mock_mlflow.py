"""Lightweight mock for mlflow used during CI training to avoid real server calls.
It captures set_experiment/start_run/log_params/log_metrics without network.
Registerable by putting path early in PYTHONPATH and importing before code that uses mlflow.
"""
from contextlib import contextmanager

_tracking_uri = None
_experiments = {}
_runs = []


def set_tracking_uri(uri):
    global _tracking_uri
    _tracking_uri = uri


def set_experiment(name):
    _experiments.setdefault(name, {})
    return {"name": name}

@contextmanager
def start_run(run_name=None):
    run_info = {"run_name": run_name}
    _runs.append(run_info)
    try:
        yield run_info
    finally:
        pass


def log_params(params):
    _runs[-1].setdefault("params", {}).update(params)


def log_metrics(metrics):
    _runs[-1].setdefault("metrics", {}).update(metrics)


def set_tag(key, value):
    _runs[-1].setdefault("tags", {})[key] = value
