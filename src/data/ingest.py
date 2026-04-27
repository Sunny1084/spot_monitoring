from __future__ import annotations

from pathlib import Path

import pandas as pd


def _resolve_raw_dir(raw_dir: Path, raw_files: dict, root: Path) -> Path:
    def has_required_files(directory: Path) -> bool:
        return all((directory / raw_files[filename]).exists() for filename in raw_files)

    if raw_dir.exists() and has_required_files(raw_dir):
        return raw_dir

    fallback = root / "exp"
    if fallback.exists() and has_required_files(fallback):
        return fallback

    missing = [name for name, fname in raw_files.items() if not (raw_dir / fname).exists()]
    raise FileNotFoundError(
        f"Raw data directory must contain {list(raw_files.values())}.\n"
        f"Checked {raw_dir}, missing files: {missing}.\n"
        f"Fallback location {fallback} also missing required files."
    )


def load_raw_data(raw_dir: str | Path, raw_files: dict, root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_dir = Path(raw_dir)
    raw_dir = _resolve_raw_dir(raw_dir, raw_files, root)

    launch_path = raw_dir / raw_files["launch"]
    termination_path = raw_dir / raw_files["termination"]
    price_path = raw_dir / raw_files["prices"]

    launch_df = pd.read_csv(launch_path, parse_dates=["launch_time"])
    termination_df = pd.read_csv(termination_path, parse_dates=["termination_time"])
    price_df = pd.read_csv(price_path, parse_dates=["timestamp"])

    return launch_df, termination_df, price_df


def merge_instance_time_series(
    launch_df: pd.DataFrame,
    termination_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> pd.DataFrame:
    launch_df = launch_df.copy()
    termination_df = termination_df.copy()
    price_df = price_df.copy()

    merged = launch_df.merge(termination_df, on="instance_id", how="left")
    merged = merged.merge(
        price_df,
        on=["instance_type", "availability_zone"],
        how="inner",
    )

    merged["timestamp"] = pd.to_datetime(merged["timestamp"], errors="coerce")
    merged = merged.dropna(subset=["timestamp"])

    merged = merged[merged["timestamp"] >= merged["launch_time"]].copy()
    if "termination_time" in merged.columns:
        terminated_mask = merged["termination_time"].notna()
        merged = merged[~terminated_mask | (merged["timestamp"] <= merged["termination_time"])]

    merged["spot_price"] = merged["spot_price"].fillna(merged["on_demand_price"])
    merged["on_demand_price"] = merged["on_demand_price"].fillna(merged["spot_price"].replace(0, 1.0))
    merged["spot_price"] = merged["spot_price"].astype(float)
    merged["on_demand_price"] = merged["on_demand_price"].astype(float)

    merged = merged.sort_values(["instance_id", "timestamp"]).reset_index(drop=True)
    return merged
