# FinCloud-AI Backend - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Next.js)                     │
└─────────────────┬──────────────────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼──────────────────────────────────────────────┐
│              FastAPI Backend (Uvicorn)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API Layer                              │   │
│  │  ├── /api/v1/cost/* - Cost Analytics                     │   │
│  │  ├── /api/v1/anomalies/* - Anomaly Detection            │   │
│  │  ├── /api/v1/forecast/* - Time Series Forecasting       │   │
│  │  ├── /api/v1/recommendations/* - Optimization           │   │
│  │  └── /api/v1/upload/* - Data Ingestion                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 Service Layer                            │   │
│  │  ├── DataPreprocessor - ETL Pipeline                    │   │
│  │  ├── AnomalyDetectionService - Anomaly Detection        │   │
│  │  ├── ForecastingService - Time Series                   │   │
│  │  └── OptimizationService - Recommendations              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ML Layer                              │   │
│  │  ├── IsolationForest - Anomaly Detection                │   │
│  │  ├── Prophet - Time Series Forecasting                 │   │
│  │  └── RandomForest - Cost Optimization                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Data Access Layer (ORM)                     │   │
│  │  └── SQLAlchemy with Pydantic Models                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────┬──────────────────────────────────────────────┘
                  │ SQL
┌─────────────────▼──────────────────────────────────────────────┐
│              PostgreSQL Database                                │
│  ├── raw_cost_data - Raw AWS billing                           │
│  ├── processed_cost_data - Cleaned & aggregated               │
│  ├── anomalies - Detected anomalies                            │
│  ├── forecasts - Cost predictions                              │
│  └── recommendations - Optimization suggestions               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Cache Layer (Redis)                          │
│  ├── Cost summaries                                             │
│  ├── Forecast results                                           │
│  └── Anomaly summaries                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Background Tasks (Optional - Celery)              │
│  ├── Anomaly Detection (hourly)                                │
│  ├── Forecasting (daily)                                        │
│  └── Optimization Analysis (weekly)                            │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Component Architecture

### 1. API Layer (`app/api/routes/`)

**Responsibility**: Handle HTTP requests and responses

```
Routes:
├── cost.py
│   ├── GET /cost/summary - Cost overview
│   ├── GET /cost/timeseries - Historical data
│   ├── GET /cost/service-breakdown - By service
│   └── GET /cost/region-breakdown - By region
│
├── anomaly.py
│   ├── GET /anomalies - List all anomalies
│   ├── GET /anomalies/latest - Recent anomalies
│   └── GET /anomalies/by-service - Service-specific
│
├── forecast.py
│   ├── GET /forecast - All forecasts
│   ├── GET /forecast/next-30-days - 30-day outlook
│   └── GET /forecast/by-service - Service forecast
│
├── recommendations.py
│   ├── GET /recommendations - All recommendations
│   ├── GET /recommendations/high-priority - Priority filter
│   ├── GET /recommendations/by-service - Service-specific
│   └── GET /recommendations/summary - Aggregated summary
│
└── upload.py
    ├── POST /upload/data - Upload CSV
    └── POST /upload/sample-data - Generate test data
```

### 2. Service Layer (`app/services/`)

**Responsibility**: Business logic and orchestration

```
Services:
├── preprocessing.py
│   ├── DataPreprocessor - ETL pipeline
│   │   ├── clean_raw_data() - Step 1: Cleaning
│   │   ├── feature_engineering() - Step 2: Features
│   │   ├── aggregate_data() - Step 3: Aggregation
│   │   └── full_preprocessing_pipeline() - Full ETL
│   └── DataValidator - Data quality checks
│
├── anomaly_detection.py
│   └── AnomalyDetectionService
│       ├── train() - Train Isolation Forest
│       ├── detect_anomalies() - Find anomalies
│       └── get_top_anomalies() - Anomalies ranking
│
├── forecasting.py
│   └── ForecastingService
│       ├── train() - Train Prophet model
│       ├── forecast_total_cost() - Aggregate forecast
│       ├── forecast_by_service() - Per-service forecast
│       └── get_forecast_summary() - Statistics
│
└── optimization.py
    └── OptimizationService
        ├── train() - Train Random Forest
        ├── get_recommendations() - Generate suggestions
        └── get_feature_importance() - Feature analysis
```

### 3. ML Layer (`app/ml/`)

**Responsibility**: Machine learning models

```
ML Models:
├── isolation_forest.py
│   └── IsolationForestModel
│       ├── train() - Training
│       ├── predict() - Predictions
│       ├── get_anomaly_score() - Anomaly scoring
│       └── detect_anomalies() - End-to-end detection
│
├── prophet_model.py
│   └── ProphetForecastingModel
│       ├── train() - Training
│       ├── forecast() - Generate forecast
│       ├── get_forecast_components() - Decomposition
│       └── forecast_service_timeseries() - Multi-service
│
└── random_forest.py
    └── RandomForestOptimizer
        ├── train() - Training
        ├── predict() - Predictions
        ├── get_feature_importance() - Features
        └── identify_optimization_opportunities() - Suggestions
```

### 4. Data Layer (`app/models/`)

**Responsibility**: Data persistence and validation

```
Models:
├── db_models.py (SQLAlchemy ORM)
│   ├── RawCostData - Raw AWS billing data
│   ├── ProcessedCostData - Cleaned data
│   ├── Anomaly - Anomalies
│   ├── Forecast - Forecasts
│   └── Recommendation - Recommendations
│
└── schemas.py (Pydantic validation)
    ├── RawCostDataCreate/Response
    ├── ProcessedCostDataResponse
    ├── AnomalyResponse
    ├── ForecastResponse
    ├── RecommendationResponse
    └── APIResponse - Standard wrapper
```

## 🔄 Data Flow

### 1. Data Ingestion & Preprocessing

```
CSV Upload
    ↓
Validation (DataValidator)
    ↓
Save to raw_cost_data table
    ↓
Preprocessing Pipeline (ETL):
    ├── Step 1: Clean (remove nulls, fix timestamps)
    ├── Step 2: Feature Engineering (rolling avg, velocity)
    ├── Step 3: Aggregation (group by date/service/region)
    └── Step 4: Validation
    ↓
Save to processed_cost_data table
```

### 2. Anomaly Detection Flow

```
Processed Cost Data
    ↓
Feature Preparation:
    ├── Select relevant features (cost, velocity, rolling avg)
    ├── Fill NaN values
    └── Normalize features
    ↓
Isolation Forest Model
    ├── Train (optional, if not already trained)
    └── Predict: anomaly_flag, anomaly_score
    ↓
Generate Explanations
    ↓
Save to anomalies table
```

### 3. Forecasting Flow

```
Processed Cost Data
    ↓
Group by service/region
    ↓
For each group:
    ├── Format data for Prophet (ds, y columns)
    ├── Train Prophet model
    ├── Generate forecast (30 periods)
    ├── Extract: predicted_cost, lower_bound, upper_bound
    └── Save to forecasts table
```

### 4. Optimization Flow

```
Processed Cost Data
    ↓
Feature Engineering:
    ├── Cost metrics
    ├── Service/region encoding
    └── Aggregation by service+region
    ↓
Random Forest Analysis:
    ├── Identify high variability → right-sizing
    ├── Identify usage patterns → reserved capacity
    └── Identify unused resources → consolidation
    ↓
Generate Recommendations
    ├── Assign priority
    ├── Calculate savings
    └── Set confidence score
    ↓
Save to recommendations table
```

## 🗄️ Database Schema

### Tables

```sql
raw_cost_data
├── id (PK)
├── timestamp
├── service
├── region
├── cost
├── usage_quantity
├── instance_type
├── account_id
└── created_at, updated_at

processed_cost_data
├── id (PK)
├── date
├── service
├── region
├── total_cost
├── daily_cost
├── hourly_cost
├── rolling_avg_7d
├── rolling_avg_30d
├── cost_velocity
├── usage_quantity
└── created_at, updated_at

anomalies
├── id (PK)
├── date
├── service
├── region
├── anomaly_score
├── anomaly_flag
├── cost_value
├── explanation
└── created_at

forecasts
├── id (PK)
├── date
├── service
├── region
├── predicted_cost
├── lower_bound
├── upper_bound
└── created_at

recommendations
├── id (PK)
├── service
├── region
├── recommendation_type
├── suggestion
├── estimated_savings
├── confidence_score
├── priority
└── created_at
```

### Indexes

```sql
CREATE INDEX idx_raw_timestamp ON raw_cost_data(timestamp);
CREATE INDEX idx_raw_service ON raw_cost_data(service);
CREATE INDEX idx_processed_date ON processed_cost_data(date);
CREATE INDEX idx_processed_service ON processed_cost_data(service);
CREATE INDEX idx_anomaly_date ON anomalies(date);
CREATE INDEX idx_forecast_date ON forecasts(date);
CREATE INDEX idx_forecast_service ON forecasts(service);
```

## 🔐 Security Architecture

### Authentication & Authorization

```
API Request
    ↓
CORS Check
    ↓
Rate Limiting (optional)
    ↓
Input Validation (Pydantic schemas)
    ↓
Business Logic
    ↓
Response Formatting (APIResponse wrapper)
```

### Data Security

- Database: Strong credentials, SSL/TLS
- Environment variables: Secrets management
- API: HTTPS enforcement
- Logging: Sensitive data masking

## 📊 Performance Considerations

### Caching Strategy

```
L1: In-Memory (LRU Cache)
    ├── Cost summaries (5 min TTL)
    └── Forecast results (1 hour TTL)

L2: Redis Cache
    ├── Service breakdowns
    ├── Recommendation summaries
    └── Anomaly counts

L3: Database
    └── Full historical data
```

### Query Optimization

```
Techniques:
├── Database indexes on date, service, region
├── Connection pooling (20 connections)
├── Query result pagination
├── Lazy loading of relationships
└── Query result caching
```

### Batch Processing

```
Background Jobs (Celery - Optional):
├── Hourly: Anomaly detection on new data
├── Daily: Forecast generation
├── Weekly: Optimization analysis
└── Monthly: Data cleanup & archival
```

## 🔄 Error Handling

### Error Flow

```
Request
    ↓
Try-Catch Block
    ├── Validation Error → 400 Bad Request
    ├── Database Error → 500 Internal Server Error
    ├── ML Model Error → 500 Internal Server Error
    └── Success → 200 OK
    ↓
Log Error (with context)
    ↓
Return StandardErrorResponse
```

### Logging

```
Log Levels:
├── DEBUG - Detailed development info
├── INFO - General information events
├── WARNING - Warning conditions
├── ERROR - Error conditions
└── CRITICAL - Critical conditions
```

## 🧪 Testing Architecture

```
Unit Tests (services, models)
    ↓
Integration Tests (API endpoints)
    ↓
End-to-End Tests (full workflows)
    ↓
Load Tests (performance)
    ↓
Penetration Tests (security)
```

## 📈 Scalability Strategy

### Horizontal Scaling

```
Load Balancer (Nginx/ALB)
    ├── Backend Instance 1
    ├── Backend Instance 2
    └── Backend Instance N

Shared Resources:
├── PostgreSQL (managed RDS)
├── Redis Cluster
└── ML Model Store (S3/GCS)
```

### Vertical Scaling

```
Increase:
├── CPU cores
├── Memory (RAM)
├── Connection pool size
└── Worker processes
```

## 📊 Monitoring & Observability

### Metrics to Monitor

```
Application:
├── Request rate
├── Response time (p50, p95, p99)
├── Error rate
└── Active connections

Database:
├── Query execution time
├── Connection pool usage
├── Disk I/O
└── Replication lag

ML Models:
├── Training time
├── Prediction latency
└── Model accuracy metrics
```

### Observability Tools

```
Logging:
├── Application logs → CloudWatch/Datadog
├── Database logs → CloudWatch/RDS logs
└── Error tracking → Sentry

Metrics:
├── Prometheus metrics
├── CloudWatch dashboards
└── Custom dashboards

Tracing:
├── Distributed tracing (Jaeger)
└── Request flow analysis
```

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2024
