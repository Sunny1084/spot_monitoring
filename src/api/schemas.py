from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PositiveFloat


class PredictRequest(BaseModel):
    timestamp: datetime = Field(..., description="Event timestamp for the current observation")
    instance_type: str = Field(..., description="Spot instance type")
    availability_zone: str = Field(..., description="Availability zone")
    spot_price: PositiveFloat = Field(..., description="Current spot price")
    on_demand_price: PositiveFloat = Field(..., description="Reference on-demand price")
    price_diff: float = Field(..., description="Spot price difference from on-demand price")
    price_ratio: float = Field(..., description="Ratio of spot price to on-demand price")
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of day extracted from timestamp")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week extracted from timestamp")
    rolling_mean_1h: float = Field(..., description="Rolling mean price_diff over the last hour")
    rolling_mean_3h: float = Field(..., description="Rolling mean price_diff over the last 3 hours")
    rolling_std_1h: float = Field(..., description="Rolling price volatility over the last hour")
    rolling_std_3h: float = Field(..., description="Rolling price volatility over the last 3 hours")
    price_delta: float = Field(..., description="Price change since previous interval")
    spike_flag: int = Field(..., ge=0, le=1, description="Indicator for a sudden price spike")


class PredictResponse(BaseModel):
    anomaly_score: float
    anomaly_label: int
    explanation: str
