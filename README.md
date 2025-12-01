<h1 align=center> Chunk_Prediction(MLOps)</h1>

End-to-end MLOps project with Docker, Kubernetes, and AWS

# 🚀 DEVELOPMENT PHASES:

📊 What I'm Building: A production-ready, enterprise-grade MLOps platform with:

```
✅ Phase 1: ML Pipeline & Training
✅ Phase 2: API & Streamlit UI
✅ Phase 3: Docker Containers
✅ Phase 4: Testing Suite
✅ Phase 5: CI/CD 
✅ Phase 6: Kubernetes Deployment (AWS)
```

---

# 🎯 Business Problem

- Predict customer churn to enable proactive retention strategies, reducing customer attrition by 15% and improving customer lifetime value.

### Key Questions to Answer First:

#### 1. Business Problem & Use Case

What problem are we solving?

- Suggestion: Let's build a Customer Churn Prediction System (simple, practical, demonstrates full MLOps pipeline)

What's the impact?

- Business value: Reduce customer churn by 15%
- Target: Marketing team can proactively reach at-risk customers

#### 2. Data Questions

What data do we have?

- Customer demographics (age, location, tenure)
- Usage patterns (login frequency, feature usage)
- Transaction history (revenue, plan type)

Data size & freshness?

- For demo: Use Kaggle dataset (Telco Customer Churn)
- In production: Daily batch updates from database

#### 3. ML Model Requirements

What's good enough?

`Target Metrics:`

- Recall ≥ 80% (catch most churners)
- Precision ≥ 70% (avoid too many false alarms)
- F1-Score ≥ 0.75
- AUC-ROC ≥ 0.85

`Model type?`

- Start: Logistic Regression (baseline)
- Experiment: Random Forest, XGBoost, LightGBM

#### 4. System Requirements

- Latency: < 200ms for predictions (REST API)
- Throughput: Handle 100 requests/second
- Availability: 99.5% uptime

---

# 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- pip
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/FraidoonOmarzai/Chunk_Prediction-MLOps-.git
cd Chunk_Prediction-MLOps-
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
conda create -p ./venv python=3.11 -y

# Activate virtual environment
conda activate C:\Users\44787\Desktop\Chunk_Prediction-MLOps-\venv

```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Directory Structure (Define template of the project)
```bash
touch template.py
python3 template.py

```

### 5. Define Logger and Custom Exception

---

# ![alt text](images/image.png)ML Pipeline (Phase 1)
```
✅ Data ingestion & validation
✅ Feature engineering
✅ Model training (4 algorithms)
✅ MLflow experiment tracking
✅ Model evaluation & selection
```

## 📥 Download Dataset

### Option 1: Automatic Download (Recommended)
```bash
python scripts/download_data.py
```

### Option 2: Manual Download
1. Visit: https://www.kaggle.com/datasets/blastchar/telco-customer-churn
2. Download the dataset
3. Save as: `data/raw/churn_data.csv`

### Option 3: Kaggle API
```bash
# Install Kaggle
pip install kaggle

# Set up credentials (~/.kaggle/kaggle.json)
# Then run:
python scripts/download_data.py
```

## Run Jupyter Notebook for Experiments 

### ✅ Typical Experiment Workflow

1. Prototype in Jupyter Notebook

- You explore ideas, try models, test functions, visualize results, etc.

- This is the “playground” phase.

2. Move Stable Code to Python Scripts (.py)

- Once your experiment code is working in the notebook, you usually move the clean, reusable parts into Python files.

1. **Components:**
   - `src/components/data_ingestion.py`
   - `src/components/data_validation.py`
   - `src/components/data_preprocessing.py`
   - `src/components/model_trainer.py`
   - `src/components/model_evaluation.py`

2. **Pipelines:**
   - `src/pipeline/training_pipeline.py`

3. **Utilities:**
   - `scripts/train.py`
```


3. Run Experiments From Scripts

- Running .py files is better for:

    - long training jobs
    - large experiments
    - automated logging
    - reproducibility

## 🎯 Run Training Pipeline

### Execute Complete Pipeline
```bash
python scripts/train.py
```


### What Happens:
1. **Data Ingestion**: Loads and splits data (80/20)
2. **Data Validation**: Checks schema and quality
3. **Data Preprocessing**: Cleans and transforms features
4. **Model Training**: Trains 4 models with MLflow tracking
5. **Model Evaluation**: Compares models and selects best

### Expected Output:
```
======================================================================
TRAINING PIPELINE COMPLETED SUCCESSFULLY!
======================================================================

Best Model: xgboost
Models trained: 4
Preprocessor saved at: artifacts/preprocessors/preprocessor.pkl

Check MLflow UI for detailed experiment tracking:
  Run: mlflow ui
  Open: http://localhost:5000
======================================================================
```

## 📊 View Experiments with MLflow

### Start MLflow UI
```bash
mlflow ui
```

### Access Dashboard
Open browser: http://localhost:5000

### What You'll See:
- All experiment runs
- Parameters for each model
- Metrics (accuracy, precision, recall, F1, ROC-AUC)
- Model artifacts
- Comparison charts

## 📈 Evaluation Metrics

### Model Performance Targets
- **Recall**: ≥ 80% (catch most churners)
- **Precision**: ≥ 70% (avoid false alarms)
- **F1-Score**: ≥ 0.75
- **ROC-AUC**: ≥ 0.85

### Metrics Calculated
- Accuracy
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion Matrix
- Specificity, Sensitivity
- Classification Report

### View Results
```bash
# Check evaluation report
cat artifacts/metrics/evaluation_report.json

# Check validation report
cat artifacts/validation_report.json
```

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)
- Data paths
- Train/test split ratio
- Feature lists
- Artifact locations
- MLflow settings

### Model Configuration (`config/model_config.yaml`)
- Hyperparameters for each model
- Algorithm-specific settings
- Training parameters

## 📝 Logs

### Log Files
Logs are saved in: `logs/`

### Log Format
```
[2024-11-04 10:30:45] INFO - ChurnPrediction - Starting training pipeline
[2024-11-04 10:30:46] INFO - ChurnPrediction - Data loaded: (7043, 21)
```

## 🧪 Generated Artifacts

### After Training:
```
artifacts/
├── models/
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   └── lightgbm.pkl
├── preprocessors/
│   ├── preprocessor.pkl
│   └── preprocessor_label_encoder.pkl
├── metrics/
│   └── evaluation_report.json
└── validation_report.json
```

## 🎓 Model Training Details

### Models Trained:
1. **Logistic Regression** (Baseline)
2. **Random Forest** (Ensemble)
3. **XGBoost** (Gradient Boosting)
4. **LightGBM** (Fast Gradient Boosting)

### Training Process:
- Stratified train/test split (80/20)
- Standard scaling for numerical features
- One-hot encoding for categorical features
- Automated hyperparameter configuration
- MLflow tracking for all experiments

---

# ![alt text](images/image-1.png)API & UI (Phase 2)
```
✅ FastAPI REST API
✅ Streamlit dashboard
✅ Real-time predictions
✅ Batch processing
```


Phase 2 adds **FastAPI REST API** and **Streamlit Dashboard** for real-time predictions and interactive visualizations.

---

## 📦 New Components Added

### 1. **Prediction Pipeline** (`src/pipeline/prediction_pipeline.py`)
- Loads trained models for inference
- Handles single and batch predictions
- Calculates risk levels
- Feature importance extraction

### 2. **FastAPI REST API** (`api/`)
- RESTful endpoints for predictions
- Request/response validation with Pydantic
- Auto-generated API documentation
- Health checks and monitoring

### 3. **Streamlit Dashboard** (`streamlit_app/`)
- Interactive web interface
- Single customer prediction
- Batch CSV upload
- Visualizations and analytics

---

## 🚀 Quick Start

### Step 1: Install New Dependencies
```bash
pip install --upgrade pip
pip install fastapi uvicorn[standard] streamlit plotly python-multipart
```

Or install from updated requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Ensure Model is Trained
```bash
# If you haven't trained models yet
python scripts/train.py
```

### Step 3: Start the FastAPI Server
```bash
python run_api.py
```

**API will be available at:**
- Main API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Step 4: Start the Streamlit Dashboard (New Terminal)
```bash
python run_streamlit.py
```

**Dashboard will open at:** http://localhost:8501

---

## 📡 API Endpoints

### **1. Health Check**
```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "preprocessor_loaded": true,
  "api_version": "1.0.0"
}
```

### **2. Single Prediction**
```bash
POST http://localhost:8000/predict
```

**Request Body:**
```json
{
  "customer": {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "Yes",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.35,
    "TotalCharges": 840.50
  }
}
```

**Response:**
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

### **3. Batch Prediction**
```bash
POST http://localhost:8000/predict/batch
```

**Request Body:**
```json
{
  "customers": [
    { /* customer 1 data */ },
    { /* customer 2 data */ }
  ]
}
```

**Response:**
```json
{
  "predictions": [ /* array of predictions */ ],
  "total_customers": 2,
  "high_risk_count": 1
}
```

### **4. Model Information**
```bash
GET http://localhost:8000/model/info
```

### **5. Feature Importance**
```bash
GET http://localhost:8000/model/feature-importance
```

---

## 🧪 Testing the API

### Option 1: Interactive Docs (Recommended)
1. Start API server: `python run_api.py`
2. Open browser: http://localhost:8000/docs
3. Try out endpoints directly in the browser

### Option 2: Test Script
```bash
python test_api.py
```

### Option 3: cURL Commands
```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

### Option 4: Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"customer": {/* customer data */}}
)
print(response.json())
```

---

# ![alt text](images/image-2.png)Containerization (Phase 3)
```
✅ Docker images (API, Streamlit, Training)
✅ Docker Compose orchestration
✅ Multi-stage builds
✅ Pushed to Docker Hub
```
Phase 3 containerizes the entire application using Docker, enabling consistent deployments across any environment.

---

## 📦 What's Been Created

### **Docker Images**
1. **API Image** - FastAPI service
2. **Streamlit Image** - Web dashboard
3. **Training Image** - Model training pipeline

### **Configuration Files**
1. `docker/Dockerfile.api` - API container definition
2. `docker/Dockerfile.streamlit` - Streamlit container
3. `docker/Dockerfile.training` - Training container
4. `docker-compose.yml` - Multi-container orchestration
5. `.dockerignore` - Exclude unnecessary files
6. `.env.example` - Environment template
7. Build & push scripts

---

```bash

mlops-churn-prediction/
│
├── docker/
│   ├── Dockerfile.api           # NEW - API container
│   ├── Dockerfile.streamlit     # NEW - Streamlit container
│   └── Dockerfile.training      # NEW - Training container
│
├── docker-compose.yml           # NEW - Orchestration
├── .dockerignore                # NEW - Exclude files
├── .env.example                 # NEW - Environment template
│
└── scripts/
    ├── build_images.sh/bat          # NEW - Build script
    ├── push_images.sh/bat           # NEW - Push to Docker Hub
    └── run_docker.sh/bat            # NEW - Run containers (.sh for Mac/Linux)
```

## 🚀 Quick Start

### **Step 1: Prerequisites**
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

### **Step 2: Setup Environment**
```bash
# Edit .env file
# Set DOCKER_USERNAME to your Docker Hub username
nano .env  # or use your favorite editor
```

Example `.env`:
```bash
DOCKER_USERNAME=yourusername
VERSION=v1.0.0
```

### **Step 3: Make Scripts Executable (Linux/Mac)**
```bash
chmod +x scripts/build_images.sh
chmod +x scripts/push_images.sh
chmod +x scripts/run_docker.sh
```

### **Step 4: Build Images**

**Linux/Mac:**
```bash
./scripts/build_images.sh
```

**Windows:**
```cmd
scripts\build_images.bat
```

This will build all 3 Docker images (~5-10 minutes first time).

### **Step 5: Run with Docker Compose**
```bash
# Start all services
docker-compose up -d

# Or use the helper script
./scripts/run_docker.sh start
```

### **Step 6: Access Services**
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit**: http://localhost:8501
- **MLflow**: http://localhost:5000

---

## 🏗️ Docker Architecture

```
┌──────────────────────────────────────────┐
│         Docker Compose Network           │
│                                          │
│  ┌──────────┐  ┌──────────┐   ┌───────┐  │
│  │   API    │  │Streamlit │   │MLflow │  │
│  │  :8000   │  │  :8501   │   │ :5000 │  │
│  └────┬─────┘  └────┬─────┘   └───┬───┘  │
│       │             │             │      │
│       └─────────────┴─────────────┘      │
│            Shared Network                │
└──────────────────────────────────────────┘
         │                    │
    [Volumes]            [Volumes]
    artifacts/            mlflow/
     logs/                 data/
```

```
┌──────────────────────┐
│  Dockerfile.training │ ──build──> 🐳 app-image
└──────────────────────┘

┌───────────────────────┐
│  Dockerfile.streamlit │ ──build──> 🐳 db-image
└───────────────────────┘

┌──────────────────┐
│  Dockerfile.api  │ ──build──> 🐳 api-image
└──────────────────┘
            │
            ↓
    ┌──────────────────┐
    │ docker-compose   │ ──orchestrates──> 🚀 All containers running together
    └──────────────────┘
```

---

## 🚢 Pushing to Docker Hub

### **Step 1: Create Docker Hub Account**
1. Go to https://hub.docker.com
2. Sign up for free account
3. Create access token (Settings → Security → New Access Token)

### **Step 2: Login to Docker Hub**
```bash
docker login
# Enter username and password/token
```

### **Step 3: Push Images**

**Linux/Mac:**
```bash
./scripts/push_images.sh
```

**Windows:**
```cmd
scripts\push_images.bat
```

**Manual Push:**
```bash
docker push username/churn-prediction-api:latest
docker push username/churn-prediction-streamlit:latest
docker push username/churn-prediction-training:latest
```

### **Step 4: Verify**
Visit: https://hub.docker.com/u/yourusername

## 🔧 Customization

### **Change Ports**

Edit `docker-compose.yml`:
```yaml
services:
  api:
    ports:
      - "8080:8000"  # Change 8080 to your port
```

### **Add Environment Variables**

```yaml
services:
  api:
    environment:
      - CUSTOM_VAR=value
      - LOG_LEVEL=DEBUG
```

### **Use Different Model**

Edit `.env`:
```bash
MODEL_PATH=artifacts/models/random_forest.pkl
```

### **Memory Limits**

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

---

## 🧪 Testing Dockerized Services

### **Test API Health**
```bash
curl http://localhost:8000/health
```

### **Test Prediction**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

### **Test Streamlit**
Open browser: http://localhost:8501

### **Test MLflow**
Open browser: http://localhost:5000

### **Run Training in Container**
```bash
docker-compose --profile training up training
```

---

## 📊 Monitoring

### **Container Stats**
```bash
# Real-time stats
docker stats

# Specific container
docker stats churn-prediction-api
```

### **Logs**
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### **Health Checks**
```bash
# Check health
docker ps

# Inspect health
docker inspect churn-prediction-api | grep Health -A 10
```

---

## 🎯 Production Deployment

### **Using Built Images**

On any machine with Docker:
```bash
# Pull images
docker pull username/churn-prediction-api:latest
docker pull username/churn-prediction-streamlit:latest

# Run
docker-compose up -d
```

### **Environment-Specific Configs**

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

---

# ![alt text](images/image-3.png)Testing (Phase 4)
```
✅ Unit tests (70%+ coverage)
✅ Integration tests
✅ Data quality tests
✅ Model performance tests
✅ Automated test suite
```

Phase 4 implements a comprehensive testing framework covering unit tests, integration tests, data validation, model performance, and API testing.

---

## 📦 What's Been Created

### **Test Structure (4 Categories)**
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Pipeline and API testing
3. **Data Tests** - Data quality and validation
4. **Model Tests** - Performance and fairness testing

### **Test Files**
1. `pytest.ini` - Pytest configuration
2. `coveragerc` - Coverage settings
3. `tests/conftest.py` - Shared fixtures
4. `tests/unit/test_data_ingestion.py`
5. `tests/unit/test_prediction_pipeline.py`
6. `tests/integration/test_api_endpoints.py`
7. `tests/data/test_data_quality.py`
8. `tests/model/test_model_performance.py`
9. `scripts/run_tests.sh` - Test runner (Linux/Mac)
10. `scripts/run_tests.bat` - Test runner (Windows)


## 🚀 Quick Start

### **Step 1: Install Test Dependencies**
```bash
pip install pytest pytest-cov pytest-mock pytest-timeout
```

Or use existing requirements.txt:
```bash
pip install -r requirements.txt
```

### **Step 2: Run All Tests**
```bash
# Linux/Mac
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh all

# Windows
scripts\run_tests.bat all

# Or directly with pytest
pytest -v
```

### **Step 3: View Coverage Report**
```bash
./scripts/run_tests.sh coverage

# Then open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

---

## 📊 Test Categories

### **1. Unit Tests** (`tests/unit/`)
Test individual components in isolation.

**Run:**
```bash
pytest -m unit -v
./scripts/run_tests.sh unit
```

**Tests:**
- Data ingestion logic
- Data preprocessing
- Model training components
- Prediction pipeline
- Utility functions

**Example:**
```bash
pytest tests/unit/test_data_ingestion.py -v
```

### **2. Integration Tests** (`tests/integration/`)
Test complete workflows and API endpoints.

**Run:**
```bash
pytest -m integration -v
./scripts/run_tests.sh integration
```

**Tests:**
- End-to-end training pipeline
- API endpoint responses
- Service communication
- Complete prediction workflow

**Example:**
```bash
pytest tests/integration/test_api_endpoints.py -v
```

### **3. Data Quality Tests** (`tests/data/`)
Validate data quality and integrity.

**Run:**
```bash
pytest -m data -v
./scripts/run_tests.sh data
```

**Tests:**
- Missing values
- Data types
- Valid categories
- Numerical ranges
- Data consistency
- Class distribution

**Example:**
```bash
pytest tests/data/test_data_quality.py -v
```

### **4. Model Performance Tests** (`tests/model/`)
Ensure model meets performance requirements.

**Run:**
```bash
pytest -m model -v
./scripts/run_tests.sh model
```

**Tests:**
- Minimum accuracy (60%)
- Minimum precision (50%)
- Minimum recall (50%)
- Minimum F1 score (55%)
- Minimum ROC-AUC (70%)
- No constant predictions
- Fairness across groups

**Example:**
```bash
pytest tests/model/test_model_performance.py -v
```

---

## 🎯 Test Markers

Tests are organized using pytest markers:

```bash
# Run specific marker
pytest -m unit
pytest -m integration
pytest -m data
pytest -m model
pytest -m api
pytest -m slow
pytest -m requires_model

# Combine markers
pytest -m "unit and not slow"
pytest -m "integration or api"

# Exclude markers
pytest -m "not slow"
```

---

## 📈 Coverage Requirements

### **Minimum Coverage: 70%**

Check coverage:
```bash
pytest --cov=src --cov=api --cov-report=term-missing
```

### **Coverage Reports Generated:**
1. **Terminal** - Summary in console
2. **HTML** - Detailed report in `htmlcov/`
3. **XML** - For CI/CD integration

### **View HTML Report:**
```bash
# Generate report
pytest --cov=src --cov=api --cov-report=html

# Open in browser
open htmlcov/index.html
```

---



## 📋 Test Runner Commands

### **Basic Commands**
```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run specific file
pytest tests/unit/test_data_ingestion.py

# Run specific test
pytest tests/unit/test_data_ingestion.py::test_function_name
```

### **Script Commands**
```bash
./scripts/run_tests.sh all        # All tests
./scripts/run_tests.sh unit       # Unit tests
./scripts/run_tests.sh integration # Integration tests
./scripts/run_tests.sh data       # Data tests
./scripts/run_tests.sh model      # Model tests
./scripts/run_tests.sh api        # API tests
./scripts/run_tests.sh fast       # Exclude slow tests
./scripts/run_tests.sh coverage   # With coverage
./scripts/run_tests.sh ci         # CI pipeline
./scripts/run_tests.sh clean      # Clean artifacts
```

---


## 📊 Performance Testing

### **Test Execution Time**
```bash
# Show slowest tests
pytest --durations=10

# Set timeout
pytest --timeout=60
```

### **Parallel Execution**
```bash
# Install plugin
pip install pytest-xdist

# Run in parallel
pytest -n auto
```

---


<!-- 

## ![alt text](image-3.png)Testing (Phase 4)

✅ Unit tests (70%+ coverage)
✅ Integration tests
✅ Data quality tests
✅ Model performance tests
✅ Automated test suite



## ![alt text](image-4.png)CI/CD (Phase 5)

✅ GitHub Actions workflows
✅ Automated testing
✅ Docker builds & pushes
✅ Security scanning
✅ Code quality checks
✅ Deployment automation

## Cloud Deployment (Phase 6)

✅ ![alt text](image-5.png)AWS EKS cluster
✅ Kubernetes orchestration
✅ Auto-scaling (HPA)
✅ Load balancing
✅ Monitoring & logging
✅ High availability -->
