# FinCloud-AI Backend - API Examples

## 📊 Cost APIs

### Get Cost Summary

```bash
curl -X GET "http://localhost:8000/api/v1/cost/summary?days=30" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "total_cost": 15234.5,
    "average_daily_cost": 507.82,
    "highest_service": "ec2",
    "highest_service_cost": 8500.0,
    "lowest_service": "lambda",
    "lowest_service_cost": 150.0,
    "period_start": "2024-01-01T00:00:00",
    "period_end": "2024-01-31T23:59:59",
    "num_records": 1000
  },
  "message": "Cost summary retrieved successfully"
}
```

### Get Cost Time Series

```bash
curl -X GET "http://localhost:8000/api/v1/cost/timeseries?days=30&service=ec2" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "timeseries": [
      {
        "timestamp": "2024-01-01T00:00:00",
        "value": 285.5,
        "service": "ec2",
        "region": "us-east-1"
      },
      {
        "timestamp": "2024-01-02T00:00:00",
        "value": 295.75,
        "service": "ec2",
        "region": "us-east-1"
      }
    ]
  },
  "message": "Retrieved 30 time series points"
}
```

### Get Service Breakdown

```bash
curl -X GET "http://localhost:8000/api/v1/cost/service-breakdown?days=30" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "breakdown": [
      {
        "service": "ec2",
        "total_cost": 8500.0,
        "percentage": 55.8,
        "trend": "up"
      },
      {
        "service": "s3",
        "total_cost": 3500.0,
        "percentage": 22.95,
        "trend": "stable"
      },
      {
        "service": "rds",
        "total_cost": 2000.0,
        "percentage": 13.12,
        "trend": "down"
      }
    ]
  },
  "message": "Service breakdown retrieved"
}
```

### Get Region Breakdown

```bash
curl -X GET "http://localhost:8000/api/v1/cost/region-breakdown?days=30" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "breakdown": [
      {
        "region": "us-east-1",
        "total_cost": 9500.0,
        "percentage": 62.33,
        "services_count": 5
      },
      {
        "region": "us-west-2",
        "total_cost": 5734.5,
        "percentage": 37.67,
        "services_count": 3
      }
    ]
  },
  "message": "Region breakdown retrieved"
}
```

---

## 🚨 Anomaly APIs

### Get Anomalies

```bash
curl -X GET "http://localhost:8000/api/v1/anomalies?days=30&min_score=0.5" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "id": 1,
        "date": "2024-01-15T10:30:00",
        "service": "ec2",
        "region": "us-east-1",
        "cost_value": 1500.5,
        "anomaly_score": 0.8724,
        "explanation": "Severe anomaly detected in ec2 costs"
      }
    ],
    "total_count": 5,
    "returned_count": 1
  },
  "message": "Retrieved 1 anomalies"
}
```

### Get Latest Anomalies

```bash
curl -X GET "http://localhost:8000/api/v1/anomalies/latest?limit=5" \
  -H "accept: application/json"
```

### Get Anomalies by Service

```bash
curl -X GET "http://localhost:8000/api/v1/anomalies/by-service?service=ec2&days=30" \
  -H "accept: application/json"
```

---

## 🔮 Forecast APIs

### Get Forecasts

```bash
curl -X GET "http://localhost:8000/api/v1/forecast?days=30&service=ec2" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "forecasts": [
      {
        "date": "2024-02-01T00:00:00",
        "service": "ec2",
        "region": "us-east-1",
        "predicted_cost": 285.5,
        "lower_bound": 260.25,
        "upper_bound": 310.75,
        "confidence_interval": "[260.25, 310.75]"
      }
    ]
  },
  "message": "Retrieved 30 forecast records"
}
```

### Get 30-Day Forecast

```bash
curl -X GET "http://localhost:8000/api/v1/forecast/next-30-days" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "period": "next 30 days",
    "total_predicted_cost": 8500.0,
    "average_daily_cost": 283.33,
    "forecast_records": 30,
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

---

## 💡 Recommendation APIs

### Get Recommendations

```bash
curl -X GET "http://localhost:8000/api/v1/recommendations?min_confidence=0.7" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "id": 1,
        "service": "ec2",
        "region": "us-east-1",
        "recommendation_type": "right_sizing",
        "suggestion": "Right-size ec2 instances in us-east-1",
        "estimated_savings": 2500.0,
        "confidence_score": 0.85,
        "priority": 1,
        "created_at": "2024-01-31T10:00:00"
      }
    ],
    "total_count": 5,
    "returned_count": 1,
    "total_potential_savings": 12500.0
  },
  "message": "Retrieved 1 recommendations"
}
```

### Get High-Priority Recommendations

```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/high-priority?limit=10" \
  -H "accept: application/json"
```

### Get Recommendations by Service

```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/by-service?service=ec2" \
  -H "accept: application/json"
```

### Get Recommendations Summary

```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/summary" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "total_recommendations": 12,
    "total_potential_savings": 50000.0,
    "by_priority": {
      "1": 5,
      "2": 4,
      "3": 3
    },
    "by_type": {
      "right_sizing": 5,
      "reserved_capacity": 4,
      "cost_consolidation": 3
    }
  },
  "message": "Recommendations summary retrieved"
}
```

---

## 📤 Upload APIs

### Upload CSV Data

```bash
curl -X POST "http://localhost:8000/api/v1/upload/data" \
  -H "accept: application/json" \
  -F "file=@cost_data.csv"
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "filename": "cost_data.csv",
    "rows_uploaded": 1000,
    "rows_processed": 1000,
    "status": "completed"
  },
  "message": "Successfully processed 1000 records"
}
```

### Generate Sample Data

```bash
curl -X POST "http://localhost:8000/api/v1/upload/sample-data?num_records=1000" \
  -H "accept: application/json"
```

---

## 🔑 Health & Info Endpoints

### Health Check

```bash
curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json"
```

**Response:**

```json
{
  "status": "healthy",
  "service": "FinCloud-AI Backend",
  "database": "connected"
}
```

### Root Endpoint

```bash
curl -X GET "http://localhost:8000/" \
  -H "accept: application/json"
```

---

## 📋 Sample CSV Data Format

```csv
timestamp,service,region,cost,usage_quantity,instance_type,account_id
2024-01-01T00:00:00,ec2,us-east-1,100.50,5000,t3.large,123456789012
2024-01-01T01:00:00,s3,us-west-2,50.25,10000,N/A,123456789012
2024-01-01T02:00:00,rds,eu-west-1,200.75,1000,db.r5.large,123456789012
```

---

## 🧪 Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get cost summary
response = requests.get(f"{BASE_URL}/cost/summary?days=30")
print(response.json())

# Get anomalies
response = requests.get(f"{BASE_URL}/anomalies?min_score=0.5")
print(response.json())

# Get forecast
response = requests.get(f"{BASE_URL}/forecast/next-30-days")
print(response.json())

# Get recommendations
response = requests.get(f"{BASE_URL}/recommendations?min_confidence=0.7")
print(response.json())

# Upload file
with open('cost_data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/upload/data", files=files)
    print(response.json())
```
