import logging
from pathlib import Path

import pandas as pd

from src.config import get_project_root, load_config
from src.data.ingest import load_raw_data, merge_instance_time_series
from src.features.engineering import build_features
from src.models.evaluate import compute_anomaly_metrics
from src.models.train import train_isolation_forest

logger = logging.getLogger("spot_pipeline")

FEATURE_COLUMNS = [
    "price_diff",
    "price_ratio",
    "hour_of_day",
    "day_of_week",
    "rolling_mean_1h",
    "rolling_mean_3h",
    "rolling_std_1h",
    "rolling_std_3h",
    "price_delta",
    "spike_flag",
]


def _ensure_directories(config: dict) -> None:
    for raw_dir in [
        config["data"]["processed_dir"],
        config["data"]["artifacts_dir"],
        config["data"]["models_dir"],
        config["data"]["mlruns_dir"],
    ]:
        Path(raw_dir).mkdir(parents=True, exist_ok=True)


def run_training(config_path: str | None = None) -> dict:
    config = load_config(config_path)
    root = get_project_root()
    _ensure_directories(config)

    launch_df, termination_df, price_df = load_raw_data(
        root / config["data"]["raw_dir"],
        config["data"]["raw_files"],
        root,
    )
    merged = merge_instance_time_series(launch_df, termination_df, price_df)
    features = build_features(merged, config["evaluation"]["early_warning_window_hours"])

    features[FEATURE_COLUMNS] = features[FEATURE_COLUMNS].fillna(0.0)
    X = features[FEATURE_COLUMNS].to_numpy()
    y = features["label"].to_numpy()

    model, metadata = train_isolation_forest(X, config, y)
    scores = -model.score_samples(X)
    metrics = compute_anomaly_metrics(features, scores, metadata["best_contamination"])

    output_path = root / config["data"]["processed_dir"] / "feature_matrix.parquet"
    features.to_parquet(output_path, index=False)
    metrics["feature_asset"] = str(output_path)

    logger.info("Training complete, model saved at %s", metadata["model_path"])
    return {**metadata, **metrics}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_training()
