import logging
from pathlib import Path

import joblib
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from src.api.schemas import PredictRequest, PredictResponse

logger = logging.getLogger("spot_api")
app = FastAPI(title="Spot Interruption Detector API", version="1.0")

MODEL_PATH = Path("artifacts/models/model.joblib")
MODEL = None
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


@app.on_event("startup")
def load_model() -> None:
    global MODEL
    if not MODEL_PATH.exists():
        logger.warning("Model artifact not found at %s. API will start in degraded mode.", MODEL_PATH)
        MODEL = None
        return

    try:
        MODEL = joblib.load(MODEL_PATH)
        logger.info("Loaded model from %s", MODEL_PATH)
    except Exception as exc:
        logger.exception("Failed to load model")
        MODEL = None


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    features = [
        payload.price_diff,
        payload.price_ratio,
        payload.hour_of_day,
        payload.day_of_week,
        payload.rolling_mean_1h,
        payload.rolling_mean_3h,
        payload.rolling_std_1h,
        payload.rolling_std_3h,
        payload.price_delta,
        payload.spike_flag,
    ]

    try:
        scores = MODEL.score_samples([features])
        score = -float(scores[0])
        label = int(MODEL.predict([features])[0] == -1)
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PredictResponse(
        anomaly_score=score,
        anomaly_label=label,
        explanation="Anomaly score is higher for likely interruption behavior.",
    )
