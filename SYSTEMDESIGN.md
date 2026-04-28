# System Design: Customer Churn Prediction MLOps Platform

**Author:** Fraidoon Omarzai
**Project:** Cloud-Native, Production-Scale MLOps System for Real-Time Churn Prediction
**Stack:** Python · FastAPI · Streamlit · Docker · Kubernetes · AWS EKS · MLflow · GitHub Actions

---

## Table of Contents

1. [What This System Does](#1-what-this-system-does)
2. [Requirements](#2-requirements)
3. [Full Architecture Overview](#3-full-architecture-overview)
4. [Data Layer](#4-data-layer)
5. [ML Pipeline](#5-ml-pipeline)
6. [Serving Layer](#6-serving-layer)
7. [Containerisation](#7-containerisation)
8. [Testing Strategy](#8-testing-strategy)
9. [CI/CD Pipeline](#9-cicd-pipeline)
10. [Infrastructure & Kubernetes](#10-infrastructure--kubernetes)
11. [Monitoring](#11-monitoring)
12. [Trade-offs & Design Decisions](#12-trade-offs--design-decisions)
13. [How to Apply This Framework to Any AI Project](#13-how-to-apply-this-framework-to-any-ai-project)

---

## 1. What This System Does

### The Business Problem

A telecom company loses customers every month without knowing in advance who will leave. By the time a customer cancels, it is too late to intervene.

**Goal:** Predict which customers are likely to cancel (churn) so the retention team can proactively reach out and reduce churn by 15%.

### The Technical Solution

A full MLOps platform that:

- Takes raw customer data and runs it through an automated training pipeline
- Trains and compares 4 ML algorithms, tracking every experiment
- Selects the best model and saves it for serving
- Exposes predictions via a REST API and a business dashboard
- Packages everything in Docker containers
- Deploys to Kubernetes on AWS with automated CI/CD

### Who Uses It

| User                       | Interface                   | What They Do                                          |
| -------------------------- | --------------------------- | ----------------------------------------------------- |
| Marketing / Retention team | Streamlit dashboard         | Upload customer CSV, view risk levels, take action    |
| Other internal services    | FastAPI REST API            | Call `/predict` to get churn probability in real time |
| Data scientists            | MLflow UI                   | Compare experiments, inspect metrics, select models   |
| DevOps / Platform team     | Kubernetes + GitHub Actions | Monitor deployments, scale, roll back                 |

---

## 2. Requirements

### Before designing anything, always define your requirements first. This is the most important step.

### 2.1 Functional Requirements

These describe **what the system must do**.

| ID    | Requirement                                                             |
| ----- | ----------------------------------------------------------------------- |
| FR-01 | Load raw customer CSV data and validate its quality before processing   |
| FR-02 | Train 4 ML models and track all experiments with parameters and metrics |
| FR-03 | Automatically select the best model based on AUC-ROC score              |
| FR-04 | Serve real-time single-customer predictions via a REST API              |
| FR-05 | Serve batch predictions for a list of customers via a REST API          |
| FR-06 | Expose model metadata and feature importance via API                    |
| FR-07 | Provide a web dashboard for business users (no coding required)         |
| FR-08 | Support re-running the full training pipeline to update the model       |

### 2.2 Non-Functional Requirements

These describe **how well the system must perform**.

| Requirement     | Target                 | Why                                    |
| --------------- | ---------------------- | -------------------------------------- |
| Latency         | < 200ms per prediction | Real-time API response expectation     |
| Throughput      | 100 requests/second    | Expected peak load                     |
| Availability    | 99.5% uptime           | Business-critical service              |
| Test Coverage   | ≥ 70%                  | Code reliability and confidence        |
| Security        | 6 automated scanners   | Production systems must be secure      |
| Reproducibility | 100%                   | Every training run must be re-runnable |

### 2.3 Model Performance Targets

These are defined before training begins, based on business needs.

| Metric    | Target | Why This Metric Matters                                                            |
| --------- | ------ | ---------------------------------------------------------------------------------- |
| Recall    | ≥ 80%  | Catch most churners — missing a churner costs the business more than a false alarm |
| Precision | ≥ 70%  | Avoid wasting retention budget on customers who weren't leaving                    |
| F1-Score  | ≥ 0.75 | Balance between recall and precision                                               |
| AUC-ROC   | ≥ 0.85 | Overall model discrimination ability                                               |

### 2.4 Actual Results (from evaluation_report.json)

| Model               | AUC-ROC   | Recall | Precision | F1    | Selected    |
| ------------------- | --------- | ------ | --------- | ----- | ----------- |
| Random Forest       | **0.864** | 79.4%  | 57.6%     | 0.667 | ✅ Champion |
| Logistic Regression | 0.862     | 82.3%  | 51.7%     | 0.635 | —           |
| LightGBM            | 0.857     | 79.4%  | 54.6%     | 0.647 | —           |
| XGBoost             | 0.859     | 55.2%  | 67.3%     | 0.607 | —           |

**Why Random Forest was selected:** Best AUC-ROC (0.864). XGBoost had the highest accuracy but only 55% recall — it missed nearly half the actual churners, which defeats the purpose of the system.

---

## 3. Full Architecture Overview

```
RAW DATA
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1 — ML PIPELINE                                      │
│                                                             │
│  Data Ingestion                                             │
│       │                                                     │
│       ▼                                                     │
│  Data Validation ──► validation_report.json                 │
│       │                                                     │
│       ▼                                                     │
│  Data Preprocessing ──► preprocessor.pkl                   │
│       │                                                     │
│       ▼                                                     │
│  Model Training (4 algorithms) ──► MLflow tracking         │
│       │                                                     │
│       ▼                                                     │
│  Model Evaluation ──► evaluation_report.json               │
│       │                                                     │
│       ▼                                                     │
│  Best Model saved ──► artifacts/models/random_forest.pkl   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2 — SERVING LAYER                                    │
│                                                             │
│  FastAPI :8000              Streamlit :8501                 │
│  ├── GET  /health           ├── Single prediction form      │
│  ├── POST /predict          ├── Batch CSV upload            │
│  ├── POST /predict/batch    ├── Risk level charts           │
│  ├── GET  /model/info       └── Analytics dashboard         │
│  └── GET  /model/feature-importance                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3 — CONTAINERISATION                                 │
│                                                             │
│  Dockerfile.api      ──► API Docker image                   │
│  Dockerfile.streamlit──► Streamlit Docker image             │
│  Dockerfile.training ──► Training Docker image              │
│  docker-compose.yml  ──► Local multi-service orchestration  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4 — TESTING                                          │
│                                                             │
│  Unit tests · Integration tests · Data tests · Model tests  │
│  70%+ coverage · pytest · Codecov                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5 — CI/CD (GitHub Actions)                           │
│                                                             │
│  Test → Lint → Security → Docker Build → Deploy to EKS      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6 — KUBERNETES ON AWS EKS                            │
│                                                             │
│  churn-prediction namespace                                 │
│  ├── API Deployment (2 replicas) ←── AWS NLB               │
│  └── Streamlit Deployment (2 replicas) ←── AWS NLB         │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Layer

### 4.1 The Dataset

**Source:** Kaggle Telco Customer Churn dataset
**Size:** 7,043 customers × 21 features
**Target:** Churn (Yes/No) — 26.5% positive class (imbalanced)

### 4.2 Feature Groups

| Group        | Features                                                                                                                                |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Demographics | gender, SeniorCitizen, Partner, Dependents                                                                                              |
| Services     | PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies |
| Account      | tenure, Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges                                                         |
| Target       | Churn (Yes=1 / No=0)                                                                                                                    |

### 4.3 Data Pipeline Flow

```
Step 1 — DataIngestion (src/components/data_ingestion.py)
    Input:  data/raw/churn_data.csv
    Action: Load CSV → stratified 80/20 split on Churn label
    Output: data/processed/train.csv (5,634 rows)
            data/processed/test.csv  (1,409 rows)

Step 2 — DataValidation (src/components/data_validation.py)
    Input:  train.csv
    Checks: all 21 columns present, correct data types,
            no excessive missing values, valid category values,
            numerical ranges (tenure ≥ 0, MonthlyCharges > 0)
    Output: artifacts/validation_report.json (PASS/FAIL per check)
    Rule:   Pipeline STOPS if validation fails (fail fast)

Step 3 — DataPreprocessing (src/components/data_preprocessing.py)
    Input:  train.csv + test.csv
    Actions:
        - Drop customerID (not a feature)
        - Fix TotalCharges (has spaces) → convert to float
        - Binary encode: Yes/No columns → 1/0
        - One-hot encode: Contract, PaymentMethod, InternetService, etc.
        - StandardScaler on: tenure, MonthlyCharges, TotalCharges
    CRITICAL: Scaler is fit on TRAIN data only, then applied to both.
    Output: preprocessor.pkl (saved to artifacts/preprocessors/)
            X_train, X_test arrays ready for model training
```

### 4.4 The Two Critical Rules of Data Preprocessing

**Rule 1 — Stratified Split (not random)**

The dataset has 26.5% churn rate. A random split might give the test set 20% or 35% churn by chance, making your evaluation metrics unreliable. Stratified split guarantees the same 26.5% ratio in both train and test.

```python
# CORRECT
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y        # ← this is the key argument
)
```

**Rule 2 — Prevent Data Leakage**

Data leakage happens when your test data "leaks" information into your training process. This makes your model look better than it actually is.

```python
# WRONG — scaler sees test data during fit
scaler.fit(X_all_data)          # ← leakage! test data included
X_train_scaled = scaler.transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# CORRECT — scaler only sees training data
scaler.fit(X_train)             # ← only training data
X_train_scaled = scaler.transform(X_train)
X_test_scaled  = scaler.transform(X_test)  # ← same scaler, not re-fit
```

### 4.5 Class Imbalance

73.5% of customers did NOT churn. 26.5% did. This is a problem because:

- A model that always predicts "no churn" gets 73.5% accuracy but catches zero churners
- Accuracy is a misleading metric — use AUC-ROC and Recall instead

Solutions applied in this project:

- Stratified split (maintains ratio in train/test)
- AUC-ROC as primary selection metric (better for imbalanced data)
- Recall as key business metric (missing a churner is costly)

Next improvements:

- `class_weight='balanced'` in model config
- Threshold tuning (lower from 0.5 to 0.3 to improve recall)
- SMOTE oversampling of minority class

---

## 5. ML Pipeline

### 5.1 Pipeline Components

Each component is a separate Python class with a single responsibility.

```
src/
├── components/
│   ├── data_ingestion.py      # Load + split data
│   ├── data_validation.py     # Quality checks
│   ├── data_preprocessing.py  # Feature engineering + encoding + scaling
│   ├── model_trainer.py       # Train 4 algorithms with MLflow tracking
│   └── model_evaluation.py    # Compare models, select champion
├── pipeline/
│   └── training_pipeline.py   # Orchestrates all components in order
└── utils/
    └── common.py              # Shared utilities (save/load artifacts, logging)
```

**Why separate components?**

- Each component is independently testable
- A failure in one step doesn't corrupt others
- Components can be replaced or improved without touching the rest
- This mirrors how real ML teams structure production pipelines

### 5.2 MLflow Experiment Tracking

Every training run logs:

```python
with mlflow.start_run(run_name="random_forest"):

    # 1. Log hyperparameters
    mlflow.log_params({
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42
    })

    # 2. Log training metrics
    mlflow.log_metrics({
        "train_auc_roc": 0.926,
        "train_recall":  0.874,
        "train_f1":      0.739
    })

    # 3. Log test metrics (used for model selection)
    mlflow.log_metrics({
        "test_auc_roc": 0.864,   # ← champion selection criterion
        "test_recall":  0.794,
        "test_f1":      0.667
    })

    # 4. Save the model artifact
    mlflow.sklearn.log_model(model, "random_forest")
```

**View experiments:** Run `mlflow ui` then open `http://localhost:5000`

### 5.3 Model Selection Logic

```python
# From model_evaluation.py
# Compare all 4 models on test AUC-ROC
best_model_name = max(
    all_results,
    key=lambda name: all_results[name]["test_metrics"]["roc_auc"]
)
# Result: random_forest wins with 0.864
```

### 5.4 Why These 4 Algorithms?

| Algorithm           | Role          | Strengths                                                    |
| ------------------- | ------------- | ------------------------------------------------------------ |
| Logistic Regression | Baseline      | Simple, fast, interpretable. Sets minimum bar.               |
| Random Forest       | Ensemble      | Handles non-linear patterns, robust to outliers, best AUC    |
| XGBoost             | Boosting      | High accuracy, but aggressive on majority class (low recall) |
| LightGBM            | Fast Boosting | Similar to XGBoost but faster training, good for large data  |

### 5.5 Artifacts Produced

After running `python scripts/train.py`:

```
artifacts/
├── models/
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl          ← champion model
│   ├── xgboost.pkl
│   └── lightgbm.pkl
├── preprocessors/
│   └── preprocessor.pkl           ← must be loaded with model
└── metrics/
    └── evaluation_report.json     ← all model results
```

---

## 6. Serving Layer

### 6.1 Why Two Services?

| Service   | Port | Users                               | Format   |
| --------- | ---- | ----------------------------------- | -------- |
| FastAPI   | 8000 | Other services, scripts, automation | JSON API |
| Streamlit | 8501 | Marketing team, business analysts   | Web UI   |

They serve different consumers with different needs. Streamlit internally calls the FastAPI service — it does not load the model directly.

### 6.2 FastAPI Endpoint Design

```
GET  /health
     Returns: { status, model_loaded, preprocessor_loaded, api_version }
     Used by: Kubernetes health probes every 10 seconds

POST /predict
     Input:   { "customer": { 19 feature fields } }
     Returns: { prediction, churn_probability, no_churn_probability,
                confidence, risk_level }
     Latency: < 200ms

POST /predict/batch
     Input:   { "customers": [ {...}, {...}, ... ] }
     Returns: { predictions: [...], total_customers, high_risk_count }
     Use case: Marketing uploads 10,000 customers every morning

GET  /model/info
     Returns: model name, version, training date, feature count

GET  /model/feature-importance
     Returns: { "Contract_Month-to-month": 0.18, "tenure": 0.15, ... }
```

### 6.3 Prediction Pipeline (Inference Path)

```python
# src/pipeline/prediction_pipeline.py

class PredictionPipeline:

    def __init__(self):
        # Load ONCE at startup — not on every request
        # Loading a model takes ~200ms. Doing it per request would make the API unusable.
        self.model       = load("artifacts/models/random_forest.pkl")
        self.preprocessor = load("artifacts/preprocessors/preprocessor.pkl")

    def predict_single(self, customer_data: dict) -> dict:

        # Step 1: Convert dict to DataFrame (preserves feature names)
        df = pd.DataFrame([customer_data])

        # Step 2: Apply SAME preprocessing used during training
        # This is why we saved preprocessor.pkl — guarantees identical transformations
        X = self.preprocessor.transform(df)

        # Step 3: Get probability scores (not just 0/1)
        proba = self.model.predict_proba(X)[0]
        # proba = [0.28, 0.72] means 28% no-churn, 72% churn

        # Step 4: Apply threshold (default 0.5)
        label = int(proba[1] >= 0.5)

        # Step 5: Business logic for risk level
        if proba[1] > 0.7:
            risk = "High"
        elif proba[1] > 0.4:
            risk = "Medium"
        else:
            risk = "Low"

        return {
            "prediction":        "Yes" if label else "No",
            "churn_probability": round(proba[1], 4),
            "risk_level":        risk
        }
```

### 6.4 Input Validation with Pydantic

Pydantic validates every incoming request before it reaches the model. This prevents crashes from bad input.

```python
from pydantic import BaseModel, validator

class CustomerRequest(BaseModel):
    tenure:         int
    MonthlyCharges: float
    Contract:       str

    @validator('Contract')
    def contract_must_be_valid(cls, v):
        valid = ['Month-to-month', 'One year', 'Two year']
        if v not in valid:
            raise ValueError(f'Must be one of {valid}')
        return v

# If someone sends Contract: "monthly" → 422 error returned immediately
# The model never sees invalid input
# This prevents KeyError crashes in the preprocessor
```

### 6.5 API Response Example

```json
{
  "prediction": "Yes",
  "prediction_label": 1,
  "churn_probability": 0.7245,
  "no_churn_probability": 0.2755,
  "confidence": 0.7245,
  "risk_level": "High"
}
```

---

## 7. Containerisation

### 7.1 Three Docker Images

| Image           | Dockerfile                  | Purpose                |
| --------------- | --------------------------- | ---------------------- |
| API image       | docker/Dockerfile.api       | Runs FastAPI service   |
| Streamlit image | docker/Dockerfile.streamlit | Runs web dashboard     |
| Training image  | docker/Dockerfile.training  | Runs training pipeline |

### 7.2 Multi-Stage Build Pattern

Multi-stage builds keep the final Docker image small and secure by separating build tools from the production image.

```dockerfile
# Dockerfile.api

# Stage 1: Builder — install everything including build tools (gcc, git, etc.)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production — only copy what's needed to run
FROM python:3.11-slim AS production
WORKDIR /app

# Copy installed Python packages from builder (no build tools included)
COPY --from=builder /root/.local /root/.local

# Copy only application code
COPY src/       ./src/
COPY api/       ./api/
COPY artifacts/ ./artifacts/
COPY config/    ./config/

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

# Run as non-root user (security best practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Result: ~200MB final image instead of ~800MB
# No gcc, git, or build tools in production → smaller attack surface
```

### 7.3 Docker Compose (Local Orchestration)

```
docker-compose up -d
```

Starts all 3 services together on a shared network:

```
┌──────────────────────────────────────┐
│       Docker Compose Network         │
│                                      │
│  API :8000    Streamlit :8501        │
│     │              │                 │
│     └──────┬────────┘                │
│            │                         │
│        MLflow :5000                  │
│                                      │
│  Shared volumes:                     │
│  artifacts/ ← model files            │
│  mlflow/    ← experiment data        │
└──────────────────────────────────────┘
```

**Why Docker Compose for local?**

- One command starts everything
- Services communicate by name (e.g., `http://api:8000`) not by IP
- Volumes share model artifacts between containers
- Easy to stop, restart, or rebuild individual services

### 7.4 Multi-Architecture Builds

```bash
# Build for both Intel/AMD (amd64) and Apple M1/M2 + AWS Graviton (arm64)
docker buildx build --platform linux/amd64,linux/arm64 -t username/churn-api:latest .
```

This means the same image runs on your laptop (M1 Mac), your colleague's laptop (Intel), and AWS servers — no compatibility issues.

---

## 8. Testing Strategy

### 8.1 Four Test Categories

```
tests/
├── unit/
│   ├── test_data_ingestion.py      # Does ingestion load and split correctly?
│   └── test_prediction_pipeline.py # Does the pipeline return valid output?
├── integration/
│   └── test_api_endpoints.py       # Do API endpoints return correct responses?
├── data/
│   └── test_data_quality.py        # Is the data clean and valid?
└── model/
    └── test_model_performance.py   # Does the model meet minimum thresholds?
```

### 8.2 What Each Category Tests

**Unit tests** — individual functions in isolation:

- Data ingestion loads the correct number of rows
- Train/test split produces the right sizes
- Prediction pipeline returns expected keys

**Integration tests** — components working together:

- Full training pipeline runs end to end without errors
- API `/predict` endpoint returns 200 with valid JSON
- API `/health` endpoint returns `model_loaded: true`

**Data quality tests** — the dataset itself:

- No missing columns
- Correct data types (tenure is int, MonthlyCharges is float)
- Valid category values (Contract is one of 3 valid options)
- Numerical ranges are sensible (no negative tenure)

**Model performance tests** — the trained model:

- AUC-ROC ≥ 0.70 (minimum bar)
- Recall ≥ 0.50 (not predicting everything as no-churn)
- Model does not always predict the same class (constant prediction check)

### 8.3 Running Tests

```bash
# Run all tests
pytest -v

# Run by category
pytest -m unit
pytest -m integration
pytest -m data
pytest -m model

# Run with coverage report
pytest --cov=src --cov=api --cov-report=term-missing

# View HTML coverage report
pytest --cov=src --cov=api --cov-report=html
open htmlcov/index.html
```

### 8.4 Coverage Target: 70%+

70% means at least 70% of your code lines are executed during tests. This catches bugs before deployment. Reported to Codecov on every CI run.

---

## 9. CI/CD Pipeline

### 9.1 Overview

Every `git push` automatically triggers a 5-stage pipeline in GitHub Actions. Nothing is deployed unless all stages pass.

```
git push
    │
    ├──────────────────┐
    ▼                  ▼
 STAGE 1            STAGE 2
 Test               Lint
 (parallel)         (parallel)
    │                  │
    └────────┬─────────┘
             ▼
          STAGE 3
          Security
             │
             ▼
          STAGE 4
          Docker Build
             │
             ▼
          STAGE 5
          Deploy (on version tag only)
```

### 9.2 Stage Details

**Stage 1 — Test**

Triggers on: every push and pull request to `main` or `develop`

What runs:

- `pytest` across Python 3.9, 3.10, and 3.11 in parallel (matrix build)
- This catches Python version compatibility bugs
- Coverage report uploaded to Codecov
- If any test fails → pipeline stops here, nothing is built or deployed

**Stage 2 — Code Quality (Lint)**

Runs in parallel with Stage 1.

| Tool   | What It Checks                            |
| ------ | ----------------------------------------- |
| Black  | Code formatting (auto-fix on PRs)         |
| isort  | Import statement ordering                 |
| Flake8 | PEP8 compliance                           |
| Pylint | Deeper code analysis (complexity, naming) |
| MyPy   | Type annotation correctness               |

**Stage 3 — Security Scanning**

Runs after Test + Lint both pass.

| Tool       | What It Catches                                                              |
| ---------- | ---------------------------------------------------------------------------- |
| Bandit     | Python security vulnerabilities in code (SQL injection, hardcoded passwords) |
| Safety     | Known vulnerabilities in your Python dependencies                            |
| pip-audit  | Additional dependency vulnerability scanning                                 |
| Gitleaks   | Accidentally committed API keys or passwords in git history                  |
| TruffleHog | Deep git history scanning for secrets                                        |
| CodeQL     | Advanced static analysis (GitHub's own security tool)                        |
| Trivy      | Docker image vulnerabilities                                                 |

Also runs on a schedule: full scan every Sunday midnight.

**Stage 4 — Docker Build and Push**

Runs after Security passes.

What happens:

1. Build API, Streamlit, and Training Docker images
2. Scan each image with Trivy for container vulnerabilities
3. Push to Docker Hub with 4 tags:
   - `latest` (most recent main branch build)
   - `v1.0.0` (specific version tag)
   - `main-abc123` (git commit SHA — for traceability)
   - `pr-42` (pull request number — for review)

**Stage 5 — Deploy**

Triggers only on version tags (e.g., `git tag v1.0.1 && git push --tags`).

What happens:

1. `aws eks update-kubeconfig` — connect to EKS cluster
2. `kubectl apply -f k8s/namespace.yaml`
3. `kubectl apply -f k8s/api.yaml` — deploy API with new image
4. `kubectl apply -f k8s/streamlit.yaml` — deploy Streamlit with new image
5. `kubectl rollout status` — wait until new pods are healthy
6. If rollout fails → Kubernetes automatically rolls back

### 9.3 GitHub Secrets Required

Set these in Settings → Secrets and Variables → Actions:

| Secret                  | Value                        |
| ----------------------- | ---------------------------- |
| `DOCKER_USERNAME`       | Your Docker Hub username     |
| `DOCKER_PASSWORD`       | Your Docker Hub access token |
| `AWS_ACCESS_KEY_ID`     | AWS IAM access key           |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key           |

---

## 10. Infrastructure & Kubernetes

### 10.1 Why Kubernetes?

Docker Compose is great for local development. Kubernetes is needed in production because:

- **Self-healing:** If a container crashes, Kubernetes automatically restarts it
- **Scaling:** Add more replicas under load without downtime
- **Rolling updates:** Deploy new versions without any downtime
- **Health checks:** Automatically remove unhealthy pods from the load balancer

### 10.2 Kubernetes Architecture on AWS EKS

```
┌─────────────────────────────────────────────────┐
│               AWS EKS Cluster                   │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │       churn-prediction namespace          │  │
│  │                                           │  │
│  │  API Deployment                           │  │
│  │  ├── replicas: 2                          │  │
│  │  ├── image: dockerhub/churn-api:v1.0.0    │  │
│  │  ├── port: 8000                           │  │
│  │  ├── livenessProbe:  GET /health          │  │
│  │  ├── readinessProbe: GET /health          │  │
│  │  └── resources: cpu 0.5–1, memory 512M–1G│  │
│  │                                           │  │
│  │  Streamlit Deployment                     │  │
│  │  ├── replicas: 2                          │  │
│  │  ├── image: dockerhub/churn-streamlit     │  │
│  │  └── port: 8501                           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────┐   ┌───────────────────────┐   │
│  │ API Service  │   │  Streamlit Service    │   │
│  │  AWS NLB     │   │     AWS NLB           │   │
│  │ :80 → :8000  │   │   :80 → :8501         │   │
│  └──────────────┘   └───────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 10.3 Why 2 Replicas?

Running 2 pods instead of 1 gives you three things:

1. **Zero-downtime deployments:** Kubernetes starts the new pod, waits for it to be healthy, then terminates the old pod. With 1 replica, there's always a gap. With 2, one is always serving while the other updates.

2. **Node failure tolerance:** AWS EC2 nodes can go down. If your pod is on that node and you only have 1 replica → total outage. With 2 replicas on different nodes → one survives.

3. **Load distribution:** The NLB distributes requests across both pods, effectively doubling throughput.

### 10.4 Health Checks — The Key to Reliable K8s

```yaml
# From k8s/api.yaml

livenessProbe:
  httpGet:
    path: /health # Your FastAPI /health endpoint
    port: 8000
  initialDelaySeconds: 30 # Wait 30s for app to start
  periodSeconds: 10 # Check every 10 seconds
  failureThreshold: 3 # Restart pod after 3 consecutive failures

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 5
```

**Liveness probe:** "Is this pod alive?" — if it fails, Kubernetes restarts the pod.
**Readiness probe:** "Is this pod ready to receive traffic?" — if it fails, Kubernetes removes the pod from the load balancer (but does not restart it).

Your `/health` endpoint returns `model_loaded: true/false`. If the model fails to load, the pod fails the health check and Kubernetes stops sending it traffic. Users always hit a healthy pod.

### 10.5 Deployment Progression

| Environment    | Command                      | Use Case                           |
| -------------- | ---------------------------- | ---------------------------------- |
| Local scripts  | `python run_api.py`          | Quick development iteration        |
| Docker Compose | `docker-compose up -d`       | Full local stack testing           |
| Local K8s      | `kubectl apply -f k8s/`      | K8s testing via Docker Desktop     |
| AWS EKS        | GitHub Actions (on tag push) | Production — managed, scalable, HA |

### 10.6 Key kubectl Commands

```bash
# Check pods are running
kubectl get pods -n churn-prediction

# Check services (get external IP from NLB)
kubectl get svc -n churn-prediction

# See logs from API pod
kubectl logs -n churn-prediction deployment/churn-api

# Watch a rolling deployment happen
kubectl rollout status deployment/churn-api -n churn-prediction

# Roll back if something went wrong
kubectl rollout undo deployment/churn-api -n churn-prediction

# Scale manually (add replicas under load)
kubectl scale deployment churn-api --replicas=4 -n churn-prediction
```

---

## 11. Monitoring

### 11.1 What the Project Has Now

| Monitor           | How                                    | What It Tells You                           |
| ----------------- | -------------------------------------- | ------------------------------------------- |
| Health endpoint   | `GET /health`                          | Is the model loaded and serving?            |
| Kubernetes probes | Automatic via liveness/readiness       | Are pods healthy? Auto-restart if not.      |
| Container logs    | `kubectl logs` / `docker-compose logs` | What is happening inside each service       |
| MLflow UI         | `http://localhost:5000`                | Full experiment history, metrics, artifacts |
| GitHub Actions    | Pass/fail badges                       | Did the last CI run succeed?                |

### 11.2 What to Add Next

**Operational monitoring (Prometheus + Grafana)**

What to track: request rate, error rate, response latency (p50/p95/p99)

```python
# Add to FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
# Now /metrics endpoint is available for Prometheus to scrape
```

**ML-specific monitoring (Evidently AI)**

What to track: are the input features drifting away from the training distribution?

```python
import evidently
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=new_production_df)

# If MonthlyCharges distribution has shifted significantly → retrain signal
```

**Explainability (SHAP)**

```python
import shap

explainer = shap.TreeExplainer(random_forest_model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values[1], X_test)

# Top churn drivers will be: contract type, tenure, monthly charges
```

This shows WHY the model made each prediction — critical for regulated industries (finance, healthcare).

### 11.3 When to Retrain

| Trigger          | How                                                    | Complexity                  |
| ---------------- | ------------------------------------------------------ | --------------------------- |
| Schedule         | Cron job every Sunday: `python scripts/train.py`       | Low — already possible      |
| Data drift       | Evidently AI: if PSI > 0.2 on any key feature          | Medium                      |
| Performance drop | Monitor on labelled production data: if AUC drops > 5% | High (needs label pipeline) |

---

## 12. Trade-offs & Design Decisions

Every design decision has a trade-off. Knowing these is what separates a good engineer from a great one.

### Decision 1: Random Forest over XGBoost as Champion

|                         | Detail                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **Chose**               | Random Forest (AUC 0.864, Recall 79%)                                                              |
| **Instead of**          | XGBoost (AUC 0.859, Recall 55%)                                                                    |
| **Why**                 | The business goal is catching churners (recall). XGBoost missed 45% of actual churners.            |
| **Trade-off**           | Random Forest has lower precision (57% vs 67%) — more false alarms to the retention team           |
| **At scale I'd change** | Tune XGBoost threshold from 0.5 → 0.3. This likely improves recall enough to make it the champion. |

### Decision 2: FastAPI over Flask

|                         | Detail                                                             |
| ----------------------- | ------------------------------------------------------------------ |
| **Chose**               | FastAPI                                                            |
| **Instead of**          | Flask                                                              |
| **Why**                 | Pydantic validation, auto-generated docs at `/docs`, async support |
| **Trade-off**           | Slightly more setup required than Flask                            |
| **At scale I'd change** | Keep FastAPI. Add async batch endpoint for large CSV processing.   |

### Decision 3: Two Separate Services (FastAPI + Streamlit)

|                         | Detail                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **Chose**               | Separate API and UI services                                                                       |
| **Instead of**          | One Streamlit app that loads the model directly                                                    |
| **Why**                 | API can be called by other services. UI and API scale independently. Clear separation of concerns. |
| **Trade-off**           | More containers to manage, Streamlit must make HTTP calls to the API                               |
| **At scale I'd change** | Same. This is the correct production pattern.                                                      |

### Decision 4: Save preprocessor.pkl with the Model

|                         | Detail                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **Chose**               | Serialise the sklearn preprocessing pipeline and load it at serving time                           |
| **Instead of**          | Re-implementing the preprocessing logic in the API code                                            |
| **Why**                 | Guarantees identical transformations between training and serving. Prevents training-serving skew. |
| **Trade-off**           | Must always keep model and preprocessor versions in sync                                           |
| **At scale I'd change** | Use a Feature Store (Feast) to centralise feature computation                                      |

### Decision 5: Static 2 Replicas

|                      | Detail                                                                     |
| -------------------- | -------------------------------------------------------------------------- |
| **Chose**            | Fixed 2 replicas                                                           |
| **Instead of**       | Horizontal Pod Autoscaler (HPA)                                            |
| **Why**              | Sufficient for project scale. Simple to reason about.                      |
| **Trade-off**        | Pays for 2 pods even during off-peak (low traffic) hours                   |
| **At scale I'd add** | `kubectl autoscale deployment churn-api --min=2 --max=10 --cpu-percent=70` |

### Decision 6: CSV as Data Source

|                   | Detail                                                                                         |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| **Chose**         | Kaggle Telco CSV                                                                               |
| **Instead of**    | PostgreSQL database                                                                            |
| **Why**           | Demonstrates full MLOps lifecycle without unnecessary infrastructure complexity                |
| **Trade-off**     | Not realistic for production (no daily updates, no live data)                                  |
| **In production** | Replace `DataIngestion` to pull from Postgres/Redshift. The rest of the pipeline is unchanged. |

---

## 13. How to Apply This Framework to Any AI Project

This 10-step structure works for any ML system: fraud detection, recommendations, NLP pipelines, computer vision APIs, RAG systems, or agentic AI. The technology changes. The structure does not.

### Step 1 — Define Requirements First

Before writing a single line of code, answer:

- What business problem are we solving?
- What does success look like? (metrics, thresholds)
- Who are the users and how will they access this?
- What are the latency, throughput, and availability requirements?

### Step 2 — Design the Data Layer

- Where does data come from?
- What is the schema? What are the data types and valid values?
- How do you validate data quality before training?
- How do you split data? (Stratified for imbalanced, time-based for time-series)
- Where do you save processed data and artifacts?

### Step 3 — Build the ML Pipeline

- Start with a baseline model (Logistic Regression, simple rules)
- Add complexity only when the baseline is not enough
- Track everything with MLflow from day one — never skip this
- Select models on the metric that maps to your business goal, not accuracy

### Step 4 — Design the Serving Layer

- Who consumes predictions? (API for services, UI for humans, batch for bulk)
- Load the model once at startup, not per request
- Validate all inputs before they reach the model
- Return probabilities, not just labels — the caller can decide the threshold

### Step 5 — Containerise

- One Docker image per service
- Multi-stage builds to keep images small
- Health check endpoint in every service
- Docker Compose for local multi-service development

### Step 6 — Write Tests

- Unit tests: does each function do what it claims?
- Integration tests: do components work together?
- Data tests: is the data schema and quality what we expect?
- Model tests: does the model meet minimum performance thresholds?
- Target 70%+ coverage and enforce it in CI

### Step 7 — Build CI/CD

- Test on every push
- Security scan on every push
- Build Docker images only after tests pass
- Deploy only on version tags, never on every push
- Nothing ships manually

### Step 8 — Orchestrate with Kubernetes

- At least 2 replicas for production (zero-downtime deploys, fault tolerance)
- Liveness and readiness probes on every deployment
- Set resource limits (CPU + memory) to prevent one service starving others
- Use namespaces to isolate environments

### Step 9 — Add Monitoring

- Operational: latency, error rate, throughput (Prometheus + Grafana)
- ML-specific: feature drift, prediction distribution shift (Evidently AI)
- Business: is the model still driving the outcome it was designed for?
- Define a retraining trigger before you need it, not after

### Step 10 — Document Your Trade-offs

For every major decision, be able to answer:

- What did I choose?
- What was the alternative?
- Why did I make this choice?
- What would I change at 10× the scale?

---

## Quick Reference

### Latency Budget (Single Prediction Request)

```
Client → NLB → Kubernetes → FastAPI → Pydantic validation
→ preprocessor.transform() → model.predict_proba() → JSON response

Breakdown:
  Network (NLB + K8s): ~5ms
  Pydantic validation:  ~1ms
  Preprocessing:        ~2ms
  Model inference:      ~10ms (Random Forest, in memory)
  JSON serialisation:   ~1ms
  ─────────────────────────
  Total:                ~19ms (well under 200ms target)
```

### Common Failure Modes and Fixes

| Failure                      | Symptom                                     | Fix                                               |
| ---------------------------- | ------------------------------------------- | ------------------------------------------------- |
| Model not loaded             | `/health` returns `model_loaded: false`     | Check artifacts path in config                    |
| Training-serving skew        | Good test metrics, poor production accuracy | Ensure same preprocessor.pkl is used in both      |
| Data leakage                 | Unrealistically high test metrics           | Fit scaler on train only                          |
| Constant predictions         | Model always predicts "No churn"            | Check class imbalance handling, use recall metric |
| CI failing on Python version | Tests pass locally, fail in CI              | Test locally on the same Python version matrix    |
| Docker image too large       | Slow builds and pulls                       | Use multi-stage builds                            |
| Pod crashing in K8s          | `kubectl get pods` shows CrashLoopBackOff   | Check `kubectl logs`, usually model path issue    |

### File Structure

```
project/
├── src/
│   ├── components/         # ML pipeline steps
│   ├── pipeline/           # Pipeline orchestration
│   └── utils/              # Shared helpers
├── api/                    # FastAPI application
├── streamlit_app/          # Streamlit dashboard
├── tests/                  # All test categories
├── docker/                 # Dockerfiles
├── k8s/                    # Kubernetes manifests
├── .github/workflows/      # GitHub Actions CI/CD
├── config/                 # Configuration YAML files
├── artifacts/              # Model files (generated, not committed)
├── data/                   # Raw and processed data
├── scripts/                # Run scripts (train, test, deploy)
├── docker-compose.yml      # Local orchestration
└── requirements.txt        # Python dependencies
```

---

_This document covers the complete system design for the Customer Churn Prediction MLOps platform. Every decision here applies directly to production ML systems in industry. The framework in Section 13 can be applied to any AI project regardless of domain or technology._
