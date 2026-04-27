from __future__ import annotations

from pathlib import Path

import joblib
import mlflow
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score


def _select_best_contamination(
    X: np.ndarray,
    y: np.ndarray | None,
    contamination_grid: list[float],
    random_state: int,
    n_estimators: int,
    max_samples: str | int,
    n_jobs: int,
) -> tuple[float, float]:
    best_contamination = contamination_grid[0]
    best_score = -np.inf

    for contamination in contamination_grid:
        model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=n_estimators,
            max_samples=max_samples,
            n_jobs=n_jobs,
        )
        model.fit(X)
        scores = -model.score_samples(X)

        if y is not None and len(np.unique(y)) > 1:
            try:
                metric = roc_auc_score(y, scores)
            except ValueError:
                metric = average_precision_score(y, scores)
        else:
            metric = np.nan

        if np.isnan(metric):
            metric = -np.abs(np.mean(scores))

        if metric > best_score:
            best_score = metric
            best_contamination = contamination

    return best_contamination, best_score


def train_isolation_forest(
    X: np.ndarray,
    config: dict,
    y: np.ndarray | None = None,
) -> tuple[IsolationForest, dict]:
    training_config = config["training"]
    data_config = config["data"]
    mlruns_path = Path(data_config["mlruns_dir"]).resolve()
    mlflow.set_tracking_uri(mlruns_path.as_uri())
    mlflow.set_experiment(data_config["experiment_name"])

    best_contamination, best_metric = _select_best_contamination(
        X=X,
        y=y,
        contamination_grid=training_config["contamination_grid"],
        random_state=training_config["random_state"],
        n_estimators=training_config["n_estimators"],
        max_samples=training_config["max_samples"],
        n_jobs=training_config["n_jobs"],
    )

    model = IsolationForest(
        contamination=best_contamination,
        random_state=training_config["random_state"],
        n_estimators=training_config["n_estimators"],
        max_samples=training_config["max_samples"],
        n_jobs=training_config["n_jobs"],
    )
    model.fit(X)
    scores = -model.score_samples(X)

    model_dir = Path(data_config["models_dir"])
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.joblib"
    joblib.dump(model, model_path)

    with mlflow.start_run():
        mlflow.log_params({
            "contamination": best_contamination,
            "n_estimators": training_config["n_estimators"],
            "max_samples": training_config["max_samples"],
            "random_state": training_config["random_state"],
        })
        mlflow.log_metric("best_selection_score", float(best_metric))
        mlflow.log_artifact(str(model_path), artifact_path="model")

    return model, {
        "model_path": str(model_path),
        "best_contamination": best_contamination,
        "selection_score": float(best_metric),
    }
