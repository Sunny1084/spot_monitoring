from pathlib import Path

import pandas as pd

from src.data.ingest import load_raw_data, merge_instance_time_series
from src.features.engineering import build_features


def test_merge_and_feature_engineering(tmp_path: Path) -> None:
    launch_csv = tmp_path / "launch_log.csv"
    termination_csv = tmp_path / "termination_log.csv"
    price_csv = tmp_path / "spot_price.csv"

    launch_csv.write_text(
        "instance_id,instance_type,availability_zone,launch_time\ni-1000,m5.large,us-east-1a,2024-01-01 00:00:00\n"
    )
    termination_csv.write_text(
        "instance_id,termination_time,reason\ni-1000,2024-01-01 03:00:00,price-too-high\n"
    )
    price_csv.write_text(
        "timestamp,instance_type,availability_zone,spot_price,on_demand_price\n"
        "2024-01-01 00:30:00,m5.large,us-east-1a,0.14,0.15\n"
        "2024-01-01 01:00:00,m5.large,us-east-1a,0.18,0.15\n"
    )

    root = tmp_path
    launch_df, termination_df, price_df = load_raw_data(root, {
        "launch": "launch_log.csv",
        "termination": "termination_log.csv",
        "prices": "spot_price.csv",
    }, root)

    merged = merge_instance_time_series(launch_df, termination_df, price_df)
    assert not merged.empty
    assert merged["instance_id"].nunique() == 1
    features = build_features(merged, early_warning_window_hours=6)
    assert "price_diff" in features.columns
    assert "rolling_mean_1h" in features.columns
    assert features["spike_flag"].isin([0, 1]).all()
