from __future__ import annotations

import numpy as np
import pandas as pd


def compute_anomaly_metrics(df: pd.DataFrame, anomaly_scores: np.ndarray, contamination: float) -> dict:
    df = df.copy()
    df["anomaly_score"] = anomaly_scores
    df["anomaly_flag"] = (df["anomaly_score"] >= np.quantile(df["anomaly_score"], 1 - contamination)).astype(int)

    correlation = df["anomaly_score"].corr(df["label"]) if "label" in df.columns else np.nan
    confidence = float(correlation) if not np.isnan(correlation) else 0.0

    lead_times = []
    terminated = df[df["label"] == 1].copy()
    for instance_id, group in terminated.groupby("instance_id"):
        first_termination = group["termination_time"].iloc[0]
        anomalies = group[group["anomaly_flag"] == 1]
        if anomalies.empty:
            continue
        anomaly_time = anomalies["timestamp"].iloc[0]
        lead_time = (first_termination - anomaly_time).total_seconds() / 3600.0
        if lead_time >= 0:
            lead_times.append(lead_time)

    average_lead_time = float(np.mean(lead_times)) if lead_times else 0.0
    percent_caught = float(len(lead_times) / max(1, df[df["label"] == 1]["instance_id"].nunique()))

    return {
        "anomaly_label_correlation": confidence,
        "average_early_warning_hours": average_lead_time,
        "termination_coverage": percent_caught,
        "anomaly_threshold": float(np.quantile(df["anomaly_score"], 1 - contamination)),
    }
