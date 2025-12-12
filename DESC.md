# Why Multi-Stage Builds vs Normal Dockerfiles

🔴 Traditional Single-Stage Dockerfile (The Old Way)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install build tools AND runtime dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libgomp1 \
    curl

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

❌ Problems with Single-Stage:

1. Bloated Image: Final image contains unnecessary build tools (gcc, g++, make)
2. Larger Size: ~800MB - 1.2GB for a simple app
3. Security Risk: More packages = more potential vulnerabilities
4. Slower Deployment: Larger images take longer to push/pull

🟢 Multi-Stage Dockerfile (Modern Way)
Stage 1: Builder

```
dockerfileFROM python:3.10-slim AS builder
# Purpose: Compile and build dependencies
```

What happens here:

- Installs build tools (gcc, make, compilers)
- Compiles Python packages with C extensions (numpy, pandas, scikit-learn)
- Creates wheel files and compiled binaries
- This stage is DISCARDED after use!

Stage 2: Runtime

```dockerfile
FROM python:3.10-slim
# Purpose: Run the application


# **What happens here:**
# - Starts with a FRESH, clean base image
# - Copies ONLY the compiled packages from builder
# - Installs ONLY runtime dependencies
# - No build tools included
# - **This becomes your final image**


## 📊 Size Comparison Example

| Type | Size | Contains |
|------|------|----------|
| **Single-Stage** | 1.2 GB | App + Build tools + Runtime deps |
| **Multi-Stage** | 450 MB | App + Runtime deps only |
| **Savings** | **~60% smaller!** | ✅ |



## 🎯 Real-World Analogy

Imagine building a house:

### Single-Stage = Building + Living in Construction Site

🏗️ Construction tools (hammers, saws, cement mixers)
🏠 Your house
🛋️ Your furniture
👷 Construction workers still there

Everything stays forever, even after construction is done!

### Multi-Stage = Construction Site → Clean House

Stage 1 (Builder):
🏗️ Construction site with all tools
👷 Workers build the house
✅ House is completed

Stage 2 (Runtime):
🏠 Only the finished house is moved to final location
🛋️ Your furniture
❌ All construction tools left behind
❌ Workers go home
```

Only the finished product moves forward!

🔍 Step-by-Step: What Happens in Your Dockerfile
Builder Stage (Temporary):

```dockerfile
FROM python:3.10-slim AS builder
# Installs: gcc, g++, make (needed to compile packages)

RUN pip install -r requirements.txt
# Compiles packages like:
# - numpy (needs C compiler)
# - pandas (needs C++ compiler)
# - scikit-learn (needs gcc)
```

Result: Compiled .so files (Linux binaries) in /usr/local/lib/python3.10/site-packages

Runtime Stage (Final):

```dockerfile
FROM python:3.10-slim  # ← Fresh start, builder is gone!

# Copy ONLY the compiled packages
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

**Result:** You get the compiled packages WITHOUT the compilers!


## 💡 Key Benefits Breakdown

### 1. **Smaller Images**
Builder stage: 1.5 GB (with all build tools)
                ↓
Runtime stage: 450 MB (only essentials)


### 2. **Faster Deployments**
- Pulling 450 MB vs 1.2 GB from Docker registry
- Faster container startup
- Less bandwidth usage

### 3. **Better Security**
Single-stage: 200+ packages (including build tools)
Multi-stage: 80 packages (only runtime)

Fewer packages = fewer security vulnerabilities

### 4. **Cleaner Containers**

Single-stage: ps aux shows gcc, make processes
Multi-stage: Only your app processes
```

5. Layer Caching

```dockerfile
# Builder stage runs only when requirements.txt changes
# Runtime stage can use cached layers if app code changes


## 🛠️ When to Use Each Approach

### Use **Single-Stage** when:
- ✅ Quick prototyping/development
- ✅ No compiled dependencies
- ✅ Pure Python packages only
- ✅ Image size doesn't matter

### Use **Multi-Stage** when:
- ✅ Production deployments
- ✅ Packages with C/C++ extensions (numpy, pandas, pillow)
- ✅ Need smaller images
- ✅ Security is important
- ✅ Deploying to cloud (bandwidth costs)


## 📝 Visual Flow of Your Dockerfile

┌─────────────────────────────────────┐
│     STAGE 1: BUILDER                │
│  (python:3.10-slim + build tools)   │
├─────────────────────────────────────┤
│ 1. Install gcc, g++, make           │
│ 2. Copy requirements.txt            │
│ 3. pip install (compiles packages)  │
│ 4. Creates compiled binaries        │
└──────────────┬──────────────────────┘
               │
               │ COPY --from=builder
               │ (only compiled packages)
               ↓
┌─────────────────────────────────────┐
│     STAGE 2: RUNTIME                │
│     (fresh python:3.10-slim)        │
├─────────────────────────────────────┤
│ 1. Install only runtime deps       │
│ 2. Copy compiled packages           │
│ 3. Copy application code            │
│ 4. Configure & run app              │
└─────────────────────────────────────┘
               │
               ↓
        FINAL IMAGE (450 MB)
```

🎓 Summary

- Normal Dockerfile = Kitchen with all cooking equipment left out forever
- Multi-Stage = Kitchen after meal prep (only plates and food remain, all pots/pans put away)
- The multi-stage approach is the modern, production-ready way to build Docker images because it creates smaller, faster, and more secure containers by separating the build environment from the runtime environment.

## 📝 Detailed Commands for Docker

### **Building Images**

```bash
# Build all images
./scripts/build_images.sh

# Build with specific version
./scripts/build_images.sh v1.0.0

# Build individual image
docker build -t username/churn-prediction-api:latest -f docker/Dockerfile.api .
```

### **Running Containers**

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### **Managing Services**

```bash
# Check status
docker-compose ps

# Restart service
docker-compose restart api

# Scale service (if needed)
docker-compose up -d --scale api=3

# Execute command in container
docker-compose exec api bash
```

### **Using Helper Script**

```bash
# Start services
./scripts/run_docker.sh start

# Stop services
./scripts/run_docker.sh stop

# Restart services
./scripts/run_docker.sh restart

# View logs
./scripts/run_docker.sh logs

# View status
./scripts/run_docker.sh status

# Run training
./scripts/run_docker.sh train

# Cleanup
./scripts/run_docker.sh cleanup
```

---

---

---

## 🔧 Test Configuration

### **pytest.ini**

```ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    data: Data quality tests
    model: Model performance tests
    api: API tests
    slow: Slow tests
addopts = -v --strict-markers --cov-fail-under=70
```

### **.coveragerc**

```ini
[run]
source = src,api
omit = */tests/*, */venv/*

[report]
precision = 2
show_missing = True
```

---

## 🧩 Test Fixtures

Located in `tests/conftest.py`, available to all tests:

### **Configuration Fixtures**

- `test_config` - Test configuration
- `temp_dir` - Temporary directory

### **Data Fixtures**

- `sample_customer_data` - Single customer dict
- `sample_dataframe` - DataFrame with 5 customers
- `sample_csv_file` - Temporary CSV file

### **Model Fixtures**

- `mock_model` - Trained model mock
- `mock_preprocessor` - Preprocessor mock
- `prediction_pipeline_mock` - Complete pipeline mock

### **API Fixtures**

- `api_client` - FastAPI test client

### **Utility Fixtures**

- `mock_logger` - Suppress log output
- `mock_mlflow` - Mock MLflow tracking

---

## 🎨 Writing New Tests

### **Example Unit Test**

```python
import pytest

@pytest.mark.unit
def test_my_function(sample_dataframe):
    """Test my function works correctly."""
    result = my_function(sample_dataframe)
    assert result is not None
    assert len(result) > 0
```

### **Example Integration Test**

```python
@pytest.mark.integration
@pytest.mark.api
def test_api_endpoint(api_client):
    """Test API endpoint."""
    response = api_client.get("/health")
    assert response.status_code == 200
```

### **Example Parametrized Test**

```python
@pytest.mark.parametrize("input,expected", [
    (0.1, 'Low'),
    (0.5, 'High'),
    (0.8, 'Critical'),
])
def test_risk_levels(input, expected):
    """Test risk level calculation."""
    assert calculate_risk(input) == expected
```

---

## 🔍 Debugging Tests

### **Run with Debug Info**

```bash
pytest -vv --tb=long
```

### **Show Print Statements**

```bash
pytest -s
```

### **Drop into Debugger on Failure**

```bash
pytest --pdb
```

### **Show Fixtures**

```bash
pytest --fixtures
```

### **Collect Tests Without Running**

```bash
pytest --collect-only
```

---

## 🚀 CI/CD Integration

### **GitHub Actions Example**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov=api --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

---

---


---------------------
<h1 align=center>Deploy to AWS</h1>
---------------------

```bash
aws ecs register-task-definition --cli-input-json file://C:\Users\44787\Desktop\Chunk_Prediction-MLOps-\.github\workflows\task_defination1.json
```
