# FinCloud-AI Backend - Quick Reference Guide

## 🎯 Quick Start (60 seconds)

### Windows

```bash
cd c:\Users\Haseeb\Desktop\FinCloud-AI\backend
start.bat
```

### Linux/Mac

```bash
cd ~/Desktop/FinCloud-AI/backend
./start.sh
```

### Manual

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python cli.py init-db
python cli.py generate-sample-data
python -m uvicorn app.main:app --reload
```

**Then visit:** http://localhost:8000/api/docs

---

## 📁 Key Files

### Configuration

- `.env` - Environment variables
- `app/config.py` - Constants and enums
- `app/core/settings.py` - Settings class

### Main Application

- `app/main.py` - FastAPI app entry point
- `app/main.py` - Health check, root endpoints

### Database

- `app/core/database.py` - Connection & session
- `app/models/db_models.py` - SQLAlchemy models (5 tables)
- `app/models/schemas.py` - Pydantic schemas

### API Routes

- `app/api/routes/cost.py` - Cost analytics (4 endpoints)
- `app/api/routes/anomaly.py` - Anomalies (3 endpoints)
- `app/api/routes/forecast.py` - Forecasts (3 endpoints)
- `app/api/routes/recommendations.py` - Recommendations (4 endpoints)
- `app/api/routes/upload.py` - Data upload (2 endpoints)

### Services (Business Logic)

- `app/services/preprocessing.py` - ETL pipeline
- `app/services/anomaly_detection.py` - Anomaly service
- `app/services/forecasting.py` - Forecasting service
- `app/services/optimization.py` - Optimization service

### ML Models

- `app/ml/isolation_forest.py` - Anomaly detection model
- `app/ml/prophet_model.py` - Time series forecasting
- `app/ml/random_forest.py` - Cost optimization

### Utilities

- `app/utils/helpers.py` - Helper functions
- `cli.py` - CLI commands

---

## 🔌 API Endpoints (15 Total)

### Cost APIs

```
GET /api/v1/cost/summary
GET /api/v1/cost/timeseries?days=30&service=ec2
GET /api/v1/cost/service-breakdown
GET /api/v1/cost/region-breakdown
```

### Anomaly APIs

```
GET /api/v1/anomalies?min_score=0.5
GET /api/v1/anomalies/latest?limit=10
GET /api/v1/anomalies/by-service?service=ec2
```

### Forecast APIs

```
GET /api/v1/forecast?days=30
GET /api/v1/forecast/next-30-days
GET /api/v1/forecast/by-service?service=ec2
```

### Recommendation APIs

```
GET /api/v1/recommendations?min_confidence=0.7
GET /api/v1/recommendations/high-priority
GET /api/v1/recommendations/by-service?service=ec2
GET /api/v1/recommendations/summary
```

### Upload APIs

```
POST /api/v1/upload/data (multipart/form-data with file)
POST /api/v1/upload/sample-data?num_records=1000
```

### System APIs

```
GET / (root)
GET /health
GET /api/docs (Swagger UI)
GET /api/redoc (ReDoc)
```

---

## 💾 Database Tables

```sql
raw_cost_data           -- Raw AWS billing data
processed_cost_data     -- Cleaned & aggregated
anomalies               -- Detected anomalies
forecasts               -- Cost predictions
recommendations         -- Optimization suggestions
```

---

## 🧠 ML Models

| Model                | Purpose           | Algorithm    | Output                      |
| -------------------- | ----------------- | ------------ | --------------------------- |
| **Isolation Forest** | Anomaly Detection | Unsupervised | anomaly_flag, anomaly_score |
| **Prophet**          | Forecasting       | Time Series  | predicted_cost, bounds      |
| **Random Forest**    | Optimization      | Supervised   | recommendations, savings    |

---

## 📊 Data Pipeline

```
CSV Upload
    ↓
DataValidator (check quality)
    ↓
DataPreprocessor.full_preprocessing_pipeline()
    ├── clean_raw_data (step 1)
    ├── feature_engineering (step 2)
    ├── aggregate_data (step 3)
    └── validate
    ↓
Save to PostgreSQL
    ├── raw_cost_data
    └── processed_cost_data
    ↓
ML Models Process
    ├── AnomalyDetectionService
    ├── ForecastingService
    └── OptimizationService
    ↓
Store Results
    ├── anomalies table
    ├── forecasts table
    └── recommendations table
```

---

## 🔧 CLI Commands

```bash
# Database
python cli.py init-db
python cli.py drop-db

# Data
python cli.py generate-sample-data --num-records=1000
python cli.py import-data --file=data.csv

# System
python cli.py status
python cli.py version
```

---

## 📦 Requirements Summary

**Core:**

- FastAPI 0.104.1
- Uvicorn (ASGI server)
- SQLAlchemy (ORM)
- PostgreSQL driver

**Data Processing:**

- Pandas, NumPy

**ML Libraries:**

- scikit-learn (Isolation Forest, Random Forest)
- Prophet (Time Series Forecasting)

**Validation:**

- Pydantic

---

## 🐳 Docker Commands

```bash
# Build image
docker build -t fincloud-ai-backend:latest .

# Run with Docker Compose
docker-compose up -d
docker-compose down

# View logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_services.py

# Run specific test
pytest tests/test_services.py::TestDataPreprocessor::test_clean_raw_data
```

---

## 📝 Configuration

### .env Variables

```
APP_NAME                     = Application name
DEBUG                        = True/False
DATABASE_URL                 = postgres://...
HOST                         = 0.0.0.0
PORT                         = 8000
API_PREFIX                   = /api/v1
ANOMALY_CONTAMINATION        = 0.05 (5%)
FORECAST_PERIODS             = 30 days
FORECAST_INTERVAL_WIDTH      = 0.95 (95%)
MAX_UPLOAD_SIZE_MB          = 100 MB
```

---

## 🔍 Debugging

### Check Database Connection

```bash
python cli.py status
```

### View Health Status

```bash
curl http://localhost:8000/health
```

### Check Logs

```bash
# In app/main.py, logs are output to console
# Search for ERROR, WARNING levels
```

### Test API Endpoint

```bash
curl -X GET http://localhost:8000/api/v1/cost/summary
```

---

## 📚 Documentation

| File               | Content                      |
| ------------------ | ---------------------------- |
| README.md          | Main documentation           |
| ARCHITECTURE.md    | System design & architecture |
| DEPLOYMENT.md      | Production deployment guide  |
| API_EXAMPLES.md    | API usage examples           |
| PROJECT_SUMMARY.md | Project overview             |

---

## 🚀 Typical Workflow

### 1. Initialize System

```bash
python cli.py init-db
python cli.py generate-sample-data --num-records=1000
```

### 2. Start Server

```bash
python -m uvicorn app.main:app --reload
```

### 3. Access API

```
Browser: http://localhost:8000/api/docs
Curl: curl http://localhost:8000/api/v1/cost/summary
```

### 4. Upload Data (Optional)

```bash
python cli.py import-data --file=your_data.csv
# Or via API:
curl -F "file=@data.csv" http://localhost:8000/api/v1/upload/data
```

### 5. Query Results

```bash
# Get cost summary
curl http://localhost:8000/api/v1/cost/summary?days=30

# Get anomalies
curl http://localhost:8000/api/v1/anomalies?min_score=0.5

# Get forecasts
curl http://localhost:8000/api/v1/forecast/next-30-days

# Get recommendations
curl http://localhost:8000/api/v1/recommendations/high-priority
```

---

## ⚠️ Common Issues

### Issue: "Port 8000 already in use"

```bash
# Change port in .env or use:
uvicorn app.main:app --port 8001
```

### Issue: "Database connection failed"

```bash
# Check .env DATABASE_URL
# Make sure PostgreSQL is running
# Test with: python cli.py status
```

### Issue: "ModuleNotFoundError"

```bash
# Ensure virtual environment is activated
# Reinstall: pip install -r requirements.txt
```

### Issue: "CSV import fails"

```bash
# Check CSV format (must have: timestamp, service, region, cost)
# Ensure no invalid values in cost column
```

---

## 📊 Example Responses

### Cost Summary

```json
{
  "status": "success",
  "data": {
    "total_cost": 15234.5,
    "average_daily_cost": 507.82,
    "highest_service": "ec2",
    "highest_service_cost": 8500.0,
    "period_start": "2024-01-01T00:00:00",
    "period_end": "2024-01-31T23:59:59"
  },
  "message": "Cost summary retrieved successfully"
}
```

### Anomaly Detection

```json
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "date": "2024-01-15T10:30:00",
        "service": "ec2",
        "anomaly_score": 0.8724,
        "cost_value": 1500.5,
        "explanation": "Severe anomaly detected in ec2 costs"
      }
    ]
  },
  "message": "Retrieved 1 anomalies"
}
```

### Forecast

```json
{
  "status": "success",
  "data": {
    "period": "next 30 days",
    "total_predicted_cost": 8500.0,
    "average_daily_cost": 283.33,
    "forecasts": [
      {
        "date": "2024-02-01",
        "predicted_cost": 285.5,
        "lower_bound": 260.25,
        "upper_bound": 310.75
      }
    ]
  },
  "message": "30-day forecast retrieved"
}
```

### Recommendations

```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "service": "ec2",
        "region": "us-east-1",
        "suggestion": "Right-size ec2 instances",
        "estimated_savings": 2500.0,
        "confidence_score": 0.85,
        "priority": 1
      }
    ],
    "total_potential_savings": 12500.0
  },
  "message": "Retrieved 1 recommendations"
}
```

---

## 🎓 Learning Resources

- **FastAPI Official:** https://fastapi.tiangolo.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Pandas Guide:** https://pandas.pydata.org/
- **scikit-learn:** https://scikit-learn.org/
- **Prophet Docs:** https://facebook.github.io/prophet/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

## 🚀 Production Checklist

- [ ] Set DEBUG=False
- [ ] Configure strong database password
- [ ] Update CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Enable API rate limiting
- [ ] Configure backups
- [ ] Test health checks
- [ ] Load test the system
- [ ] Set up CI/CD
- [ ] Document deployment process

---

## 📞 Support

- **API Documentation:** http://localhost:8000/api/docs
- **Examples:** See API_EXAMPLES.md
- **Architecture:** See ARCHITECTURE.md
- **Deployment:** See DEPLOYMENT.md

---

**Happy Coding! 🚀**

For more details, see the full documentation in README.md, ARCHITECTURE.md, and DEPLOYMENT.md
