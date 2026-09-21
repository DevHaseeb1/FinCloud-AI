
<h1 align="center">☁️ FinCloud AI</h1>

<p align="center" style="color:grey;"><i>AI-Driven Cloud Cost Anomaly & Waste Elimination Platform</i></p>


<p align="center">
  <a href="#-quick-start"><strong>🚀 Quick Start</strong></a>
  ·
  <a href="#-how-it-works"><strong>⚙️ How It Works</strong></a>
  ·
  <a href="#-tech-stack"><strong>🛠️ Tech Stack</strong></a>
  ·
  <a href="#-project-team"><strong>👥 Team</strong></a>
</p>
<br>

<p align="center">

  <!-- Languages & Frameworks -->
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <!-- Cloud Providers -->
  <img src="https://img.shields.io/badge/AWS-Cloud-232F3E?style=for-the-badge&logo=amazonaws&logoColor=FF9900" alt="AWS"/>
  <img src="https://img.shields.io/badge/Azure-Cloud-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Microsoft Azure"/>
  <img src="https://img.shields.io/badge/Google%20Cloud-Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=F4B400" alt="Google Cloud"/>
  <!-- Tools -->
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" />

</p>



## 💡 About the Project
FinCloud-AI is an AI-powered FinOps platform for monitoring AWS cloud spend, detecting unusual cost behavior, forecasting future usage, and suggesting practical optimization actions.

It combines a FastAPI backend, PostgreSQL + Redis infrastructure, and a modern Next.js dashboard to help teams reduce cloud waste and improve financial visibility.

## 🎯 Why this project matters

Cloud cost issues often stay hidden until monthly bills spike. FinCloud-AI helps teams:

- Track AWS spend trends across services and regions
- Identify unusual spikes and anomalies in real time
- Forecast upcoming costs using time-series ML
- Recommend cost-saving actions with confidence scores
- Visualize financial insights through a clean dashboard

## ✨ Key features

- AWS billing data upload and preprocessing
- CUR-style CSV ingestion for cloud usage analysis
- Cost summary and time-series trend monitoring
- Service and region breakdown analytics
- Anomaly detection for unexpected spending spikes
- Forecasting for upcoming cloud expenditure
- Optimization recommendations for cost reduction
- Modern dashboard built with Next.js and Tailwind
- Secure backend API structure with FastAPI

## 📊 System Architecture

<p align="center">
  <img src="architecture\backend.png"
       alt="FinCloud AI Backend and Cloud Architecture"
       width="1100"/>
</p>

<p align="center">
  <em>End-to-end backend architecture — from cloud billing data ingestion to ML-powered FinOps insights.</em>
</p>

## 🧠 What the app does

1. Upload AWS Cost and Usage Report data or sample dataset
2. Clean and normalize billing records
3. Aggregate cost by date, service, and region
4. Detect unusual spending with anomaly detection models
5. Forecast future cost using time-series prediction
6. Suggest savings opportunities and optimization strategies
7. Display everything in a real-time dashboard

## 🖥️ Frontend Architecture

<p align="center">
  <img src="architecture\frontend.png"
       alt="FinCloud AI Frontend Architecture and Dashboard"
       width="1100"/>
</p>

<p align="center">
  <em>Next.js frontend — authentication, dashboard analytics, anomalies, forecasting, recommendations, and smart alerts.</em>
</p>

### 🔄 From Cloud Data to Cost Intelligence

<p align="center">

**☁️ Collect** → **📥 Ingest** → **🧹 Transform** → **🤖 Analyze** → **🚨 Detect** → **📈 Forecast** → **💡 Optimize** → **📊 Visualize**

</p>

FinCloud AI takes raw cloud billing and usage data through an ETL and machine-learning pipeline, then turns it into cost trends, anomaly alerts, forecasts, and optimization insights through the dashboard.
## 🏗️ Tech stack

### Backend

- 🐍 Python
- ⚡ FastAPI
- 🗄️ SQLAlchemy
- 🐘 PostgreSQL
- 🔴 Redis
- ✅ Pydantic

### Frontend
- ▲ Next.js 16
- ⚛️ React 19
- 🔷 TypeScript
- 🎨 Tailwind CSS
- 📊 Recharts
- 🔗 Axios

### Data & Machine Learning
- 🐼 Pandas
- 🔢 NumPy
- 🤖 scikit-learn
- 📈 Prophet
- 🌲 XGBoost
- 🔄 ETL Pipelines

### Cloud & DevOps
- ☁️ AWS
- ☁️ Azure / GCP-ready architecture
- 🐳 Docker
- 🐙 Docker Compose
- 🔌 REST APIs


### 🧠 Machine Learning & Analytics
| Component                       | Purpose                                          |
| ------------------------------- | ------------------------------------------------ |
| 🌲 **Isolation Forest**         | Detect unusual cost and spending patterns        |
| 📈 **Prophet**                  | Time-series forecasting for cloud expenditure    |
| 🤖 **Random Forest / ML Logic** | Support recommendation and optimization analysis |
| 🐼 **Pandas**                   | Data cleaning, transformation, and aggregation   |
| 🔢 **NumPy**                    | Numerical processing                             |
| 🧩 **Feature Engineering**      | Prepare billing data for ML and analytics        |


## 🚀 Quick start (recommended)

The easiest setup is to start backend services with Docker, so you do not need to install PostgreSQL or Redis manually.

### 1) Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/FinCloud-AI.git
cd FinCloud-AI
```

### 2) Start backend services with Docker

```bash
cd backend
docker compose up --build
```

This starts:

- FastAPI backend
- PostgreSQL database
- Redis cache
- pgAdmin for database management

### 3) Check the backend

Open these links in your browser:

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health check: http://localhost:8000/health

If `/health` responds successfully, the backend is running correctly.

### 4) Start the frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
```

Create your environment file:

Windows:

```powershell
copy NUL .env.local
```

macOS / Linux:

```bash
touch .env.local
```

Add this value:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Then run:

```bash
npm run dev
```

Open the app at:

- http://localhost:3000

## 🔄 Full local startup flow

Use two terminals:

Terminal 1 — Backend

```bash
cd backend
docker compose up --build
```

Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Then visit:

- http://localhost:3000

## 🐳 Why Docker is recommended

Docker keeps the backend environment simple and repeatable.

Instead of installing:

- PostgreSQL
- Redis
- Python service dependencies
- supporting infrastructure

you can bring the required services up with a single command.

This makes local development cleaner and reduces setup mistakes.

## ⚙️ Local backend setup without Docker

If you want to run the backend directly instead of using Docker, use:

```bash
cd backend
python -m venv venv
```

Activate the environment:

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Run the backend:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Useful project commands

From the `backend/` directory:

```bash
python cli.py --help
python cli.py init-db
python cli.py generate-sample-data --num-records=1000
python cli.py import-data --file data/raw/your_file.csv
python cli.py status
python cli.py version
```

From the `frontend/` directory:

```bash
npm install
npm run dev
npm run build
npm run lint
```

## 🔌 API access

The application exposes endpoints for cost analysis, anomaly detection, forecasting, recommendations, and file upload.

Common routes:

```text
GET /health
GET /api/v1/cost/summary
GET /api/v1/cost/timeseries
GET /api/v1/anomalies
GET /api/v1/forecast/next-30-days
GET /api/v1/recommendations/summary
POST /api/v1/upload/data
```

## 📈 ML workflow

The pipeline is designed around real cloud-finance use cases:

1. Load raw AWS billing data
2. Clean and normalize dataset fields
3. Engineer cost-based features
4. Detect abnormal spending behavior
5. Forecast next-period usage and cost
6. Generate savings recommendations
7. Present all findings on the dashboard

## 📁 Data files included

This project already includes sample CUR-style datasets such as:

- `Fincloud-cur-00001.csv`
- `Fincloud-cur-enhanced.csv`
- `Fincloud-cur-enhanced-v2.csv`

These can be used to test upload and analytics flows without needing external AWS exports.

## 🛠️ Troubleshooting

### Frontend can't reach backend

Make sure your `.env.local` file contains:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Then restart the frontend:

```bash
npm run dev
```

### Docker containers fail to start

Check that Docker Desktop is running, then run:

```bash
cd backend
docker compose down
Docker compose up --build
```

### Backend health check fails

Verify the backend container is running and the server is listening on port 8000.


---

## 🎓 Academic Project

FinCloud AI was developed as a Final Year Project (FYP) focused on combining cloud computing, FinOps, data engineering, machine learning, and full-stack development into a practical cost-intelligence platform.


## 👥 Project Team

<div style="display: flex; justify-content: center; gap: 40px;">

  <div align="center">
    <a href="https://github.com/DevHaseeb1">
      <img src="https://github.com/DevHaseeb1.png?size=120" width="100px;" alt="Haseeb Perveez"/>
      <br /><sub><b>Haseeb Perveez</b></sub>
    </a>
    <br /><sub>Frontend Developer</sub>
  </div>
<br>
  <div align="center">
    <a href="https://github.com/usman-rizz">
      <img src="https://github.com/usman-rizz.png?size=120" width="100px;" alt="Team Member 2"/>
      <br /><sub><b>Muhammad Usman</b></sub>
    </a>
    <br /><sub>Solution Architecture</sub>
  </div>
<br>
  <div align="center">
    <a href="https://github.com/YOUR-GITHUB-3">
      <img src="https://github.com/YOUR-GITHUB-3.png?size=120" width="100px;" alt="Team Member 3"/>
      <br /><sub><b>Alishba</b></sub>
    </a>
    <br /><sub>ML workflow</sub>
  </div>
<br>
  <div align="center">
    <a href="https://github.com/YOUR-GITHUB-4">
      <img src="https://github.com/YOUR-GITHUB-4.png?size=120" width="100px;" alt="Team Member 4"/>
      <br /><sub><b>Bisma Khan</b></sub>
    </a>
    <br /><sub>AI workflow</sub>
  </div>

</div>


## 👨‍💻 Author
<p align="center"> <a href="https://github.com/usman-rizz"> <img src="https://github.com/usman-rizz.png?size=160" width="120px;" alt="Author"/> </a> <br>

<strong>Muhammad Usman</strong>

<br>

<sub>Computer Science Student • Data Engineering • Cloud • AI/ML</sub>


[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohammad-usman736/)  [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:usman.rizz6769@gmail.com)  [![Hotmail](https://img.shields.io/badge/Outlook-0078D4?style=for-the-badge&logo=microsoft-outlook&logoColor=white)](mailto:Muhammad_usman2023@hotmail.com)


## 📌 License

This project is intended for academic and final-year project use and can be customized further according to your project requirements.


## ⭐ Project

If you find the project interesting, feel free to star the repository and explore the code.

<p align="center">

☁️ FinCloud AI
Turning cloud cost data into actionable FinOps insights.

</p>


- Project: FinCloud-AI
- Type: Final Year Project (FYP)
- Domain: Cloud Computing • FinOps • Data Engineering • ML • AI
- Architecture: Full-stack web application
- Team: 4 Members


