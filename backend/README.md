# FinCloud-AI Backend System

Production-grade FastAPI backend for cloud cost optimization and FinOps analytics.

## 🚀 Features

- **AWS Billing Data Processing**: Ingest and preprocess AWS cost data (CUR format)
- **Advanced ML Models**:
  - Anomaly Detection (Isolation Forest)
  - Time Series Forecasting (Prophet)
  - Cost Optimization Recommendations (Random Forest)
- **Clean ETL Pipeline**: Robust data preprocessing with feature engineering
- **REST APIs**: Comprehensive endpoints for cost analytics, anomalies, forecasts, and recommendations
- **PostgreSQL Database**: Persistent storage with ORM (SQLAlchemy)
- **Production-Ready**: Modular architecture, error handling, logging, validation

## 📋 Requirements

- Python 3.9+
- PostgreSQL 12+
- Optional: Redis (for caching and Celery)
- Optional: Docker & Docker Compose

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── cost.py         # Cost APIs
│   │   │   ├── anomaly.py      # Anomaly detection APIs
│   │   │   ├── forecast.py     # Forecasting APIs
│   │   │   ├── recommendations.py  # Recommendation APIs
│   │   │   └── upload.py       # Data upload APIs
│   │
│   ├── core/
│   │   ├── database.py         # Database connection & session
│   │   └── settings.py         # Application settings
│   │
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── services/
│   │   ├── preprocessing.py    # ETL pipeline
│   │   ├── anomaly_detection.py
│   │   ├── forecasting.py
│   │   └── optimization.py
│   │
│   ├── ml/
│   │   ├── isolation_forest.py # Anomaly detection model
│   │   ├── prophet_model.py    # Forecasting model
│   │   └── random_forest.py    # Optimization model
│   │
│   └── utils/
│       └── helpers.py          # Utility functions
│
├── data/
│   ├── raw/                    # Raw input data
│   └── processed/              # Processed data
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── docker-compose.yml          # Docker compose
├── Dockerfile                  # Docker image
└── README.md                   # Documentation
```

## 🔧 Installation & Setup

### 1. Clone and Setup

```bash
cd FinCloud-AI/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Ensure PostgreSQL is running, then create database:

```bash
createdb fincloud_db
```

### 4. Configure Environment

Copy `.env` and adjust database URL if needed:

```bash
cp .env .env.local
# Edit .env.local with your settings
```

### 5. Run Application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000/api/docs` for interactive API documentation

## 🐳 Docker Setup

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:

- FastAPI backend on `http://localhost:8000`
- PostgreSQL database
- Optional: Redis (for caching)

## 📊 Database Schema

### Tables

1. **raw_cost_data**: Raw AWS billing data
2. **processed_cost_data**: Cleaned and aggregated costs
3. **anomalies**: Detected cost anomalies
4. **forecasts**: Cost predictions
5. **recommendations**: Optimization suggestions

## 🔌 API Endpoints

### Cost APIs

- `GET /api/v1/cost/summary` - Cost summary
- `GET /api/v1/cost/timeseries` - Historical costs
- `GET /api/v1/cost/service-breakdown` - Costs by service
- `GET /api/v1/cost/region-breakdown` - Costs by region

### Anomaly APIs

- `GET /api/v1/anomalies` - List anomalies
- `GET /api/v1/anomalies/latest` - Latest anomalies
- `GET /api/v1/anomalies/by-service` - Service anomalies

### Forecast APIs

- `GET /api/v1/forecast` - All forecasts
- `GET /api/v1/forecast/next-30-days` - 30-day forecast
- `GET /api/v1/forecast/by-service` - Service forecast

### Recommendation APIs

- `GET /api/v1/recommendations` - All recommendations
- `GET /api/v1/recommendations/high-priority` - High priority
- `GET /api/v1/recommendations/by-service` - Service recommendations
- `GET /api/v1/recommendations/summary` - Summary

### Upload APIs

- `POST /api/v1/upload/data` - Upload CSV data
- `POST /api/v1/upload/sample-data` - Generate sample data

## **🧹 ETL Pipeline**

### Step 1: Data Cleaning

- Remove null values
- Fix invalid timestamps
- Normalize service/region names
- Convert types

### Step 2: Feature Engineering

- Daily/hourly cost aggregation
- Rolling averages (7d, 30d)
- Cost velocity (rate of change)
- Service/region grouping

### Step 3: Aggregation

- Group by date, service, region
- Sum metrics

### Step 4: Storage

- Save to PostgreSQL

## 🧠 ML Models

### 1. Anomaly Detection (Isolation Forest)

- Detects unusual cost spikes
- Output: anomaly_flag (0/1), anomaly_score (0-1)

### 2. Forecasting (Prophet)

- Predicts 7-30 day costs
- Output: predicted_cost, lower_bound, upper_bound

### 3. Optimization (Random Forest)

- Identifies cost-saving opportunities
- Output: recommendation_type, estimated_savings, confidence_score
---------------------------------------------------------------------------------------------------


# 🛠️ Technology Stack

### Cloud Platform

- AWS

### Programming Language

- Python

### Data Processing

- Pandas
- NumPy

### Database

- PostgreSQL

### Machine Learning

- Scikit-Learn
- Prophet
- RandomForest

### Visualization

- Website

### Version Control

- Git
- GitHub

---

## 📈 Sample API Response

```json
{
  "status": "success",
  "data": {
    "total_cost": 15234.5,
    "average_daily_cost": 507.82,
    "highest_service": "ec2",
    "highest_service_cost": 8500.0
  },
  "message": "Cost summary retrieved successfully"
}
```

## 🧪 Testing

### Run Tests

```bash
pytest
pytest -v  # Verbose
pytest --cov  # Coverage
```

### Generate Sample Data

```bash
curl -X POST http://localhost:8000/api/v1/upload/sample-data?num_records=1000
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure database with strong credentials
- [ ] Use environment variables for secrets
- [ ] Enable CORS appropriately
- [ ] Set up monitoring/logging
- [ ] Configure rate limiting
- [ ] Use reverse proxy (Nginx)
- [ ] Enable SSL/TLS
- [ ] Set up CI/CD pipeline

### Deployment Options

1. **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Instances
2. **Kubernetes**: Use provided Helm charts
3. **Traditional Servers**: Use Gunicorn + Nginx

## 📝 Configuration

Edit `.env` or environment variables:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
DEBUG=False
LOG_LEVEL=INFO
ANOMALY_CONTAMINATION=0.05
FORECAST_PERIODS=30
```

## 🔍 Monitoring & Logging

- Logs: Check `app.main` logger
- Health Check: `GET /health`
- Metrics: Available at `/metrics` (if configured)
- Debugging: Use `/api/docs` for interactive testing


# **🤝 Contributing**

1. Create feature branch
2. Make changes
3. Add tests
4. Create pull request

# **📄 License**

Proprietary - FinCloud-AI

# **📞 Contact**

**Muhammad Usman**

📧 Email: usman.rizz6769@gmail.com

💼 LinkedIn: https://www.linkedin.com/in/mohammad-usman736

🐙 GitHub: https://github.com/usman-rizz

---

For project-related queries, collaboration opportunities, or technical discussions, feel free to reach out through email or LinkedIn.

If you discover any issues or have suggestions for improvement, please open an issue in this repository.

---

**Last Updated**: 2026
