from __future__ import annotations

import numpy as np
import pandas as pd


def build_features(df: pd.DataFrame, early_warning_window_hours: int = 6) -> pd.DataFrame:
    df = df.copy()
    df["price_diff"] = df["spot_price"] - df["on_demand_price"]
    df["price_ratio"] = df["spot_price"] / df["on_demand_price"].replace(0, 1.0)
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df = df.sort_values(["instance_id", "timestamp"]).reset_index(drop=True)
    grouped = df.groupby("instance_id")

    df["rolling_mean_1h"] = grouped["price_diff"].rolling(window=2, min_periods=1).mean().reset_index(level=0, drop=True)
    df["rolling_mean_3h"] = grouped["price_diff"].rolling(window=6, min_periods=1).mean().reset_index(level=0, drop=True)
    df["rolling_std_1h"] = grouped["price_diff"].rolling(window=2, min_periods=1).std().reset_index(level=0, drop=True).fillna(0.0)
    df["rolling_std_3h"] = grouped["price_diff"].rolling(window=6, min_periods=1).std().reset_index(level=0, drop=True).fillna(0.0)

    df["price_delta"] = grouped["spot_price"].diff().fillna(0.0)
    spike_threshold = (df["rolling_std_3h"] * 2).fillna(0.0)
    df["spike_flag"] = ((df["price_delta"] > spike_threshold) | (df["price_delta"] > 0.1)).astype(int)

    if "termination_time" in df.columns:
        df["time_to_termination_hours"] = (
            df["termination_time"] - df["timestamp"]
        ).dt.total_seconds() / 3600
        df["label"] = (
            df["time_to_termination_hours"].between(0, early_warning_window_hours)
        ).astype(int)
    else:
        df["label"] = 0

    return df
