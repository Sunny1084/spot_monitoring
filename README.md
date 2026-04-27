# AWS Spot Interruption Detection

A production-oriented MLOps project for predicting AWS Spot Instance interruptions using anomaly detection.

## Architecture Overview

The repository is built as a modular machine learning pipeline with the following components:

- `src/data`: ingest raw launch, termination, and spot price data.
- `src/features`: build time-series and behavioral features.
- `src/models`: train an Isolation Forest model, tune contamination, and evaluate anomaly signals.
- `src/pipelines`: run full training and retraining workflows.
- `src/api`: expose a FastAPI prediction endpoint.
- `config/config.yaml`: centralized configuration for data paths, model settings, and API behavior.

## Project Structure

```
spot_monitoring/
├── config/
│   └── config.yaml
├── data/
│   └── raw/.gitkeep
├── artifacts/
│   └── models/.gitkeep
├── mlruns/
├── src/
│   ├── api/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── pipelines/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .github/workflows/ci.yml
```

## Setup Instructions

1. Activate your virtual environment:

```powershell
cd c:\Users\su108\OneDrive\Documents\spot_monitoring
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Place the raw CSV files into `data/raw/`.

   - `launch_log.csv`
   - `termination_log.csv`
   - `spot_price.csv`

   The pipeline also supports the existing `exp/` folder as a fallback data source.

## Run the Training Pipeline

```powershell
python -m src.pipelines.train_pipeline
```

This will:

- ingest and merge the raw datasets
- compute rolling and behavioral features
- train an Isolation Forest model
- log metrics and artifacts to MLflow
- save the model to `artifacts/models/model.joblib`

## Run the API Locally

Start the FastAPI service once the model is trained:

```powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

> Note: On Windows PowerShell, use `python -m uvicorn` instead of calling `uvicorn.exe` directly if AppLocker or application control blocks the executable.

### Sample Request

Use `curl.exe` or PowerShell native requests to ensure the JSON body is sent correctly.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" --data-raw "{\"timestamp\":\"2024-01-01T01:00:00\",\"instance_type\":\"m5.large\",\"availability_zone\":\"us-east-1a\",\"spot_price\":0.18,\"on_demand_price\":0.15,\"price_diff\":0.03,\"price_ratio\":1.2,\"hour_of_day\":1,\"day_of_week\":0,\"rolling_mean_1h\":0.02,\"rolling_mean_3h\":0.025,\"rolling_std_1h\":0.01,\"rolling_std_3h\":0.015,\"price_delta\":0.03,\"spike_flag\":0}"
```

Or use PowerShell native request:

```powershell
$body = [PSCustomObject]@{
  timestamp = '2024-01-01T01:00:00'
  instance_type = 'm5.large'
  availability_zone = 'us-east-1a'
  spot_price = 0.18
  on_demand_price = 0.15
  price_diff = 0.03
  price_ratio = 1.2
  hour_of_day = 1
  day_of_week = 0
  rolling_mean_1h = 0.02
  rolling_mean_3h = 0.025
  rolling_std_1h = 0.01
  rolling_std_3h = 0.015
  price_delta = 0.03
  spike_flag = 0
}
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method Post -ContentType 'application/json' -Body ($body | ConvertTo-Json)
```

### Expected Response

```json
{
  "anomaly_score": 0.6423,
  "anomaly_label": 1,
  "explanation": "Anomaly score is higher for likely interruption behavior."
}
```

## Docker

Build and run the API container:

```powershell
docker build -t spot-monitoring-api .
docker run --rm -p 8000:8000 -v ${PWD}\artifacts:/app/artifacts -v ${PWD}\mlruns:/app/mlruns spot-monitoring-api
```

Run with Docker Compose:

```powershell
docker compose up --build
```

## CI/CD and Retraining

- GitHub Actions pipeline defined in `.github/workflows/ci.yml`
- It runs:
  - tests with `pytest`
  - training with `python -m src.pipelines.train_pipeline`
  - Docker image build
- Scheduled retraining can be enabled by GitHub Actions cron or by triggering `src/pipelines/retrain.py` when new data arrives.

## System Design Diagram

- Data ingestion: raw CSVs -> instance-level time series
- Feature engineering: price, time, rolling statistics, behavioral signals
- Modeling: Isolation Forest anomaly detection
- Evaluation: anomaly / termination correlation, early warning lead time
- Model serving: FastAPI prediction endpoint
- Tracking: MLflow experiment history and artifact management

## Notes for Production

- `config/config.yaml` centralizes paths and hyperparameters.
- No hardcoded paths are used inside source modules.
- Model artifacts and MLflow run tracking are stored outside source code.
- The API validates input data with Pydantic.
- The project is structured for maintainability, testing, and CI automation.
