@echo off
REM FinCloud-AI Backend Quick Start Script for Windows

REM Always run from this script's directory (backend/)
pushd "%~dp0"

echo.
echo 🚀 FinCloud-AI Backend - Quick Start
echo ====================================

REM Check Python
echo ✓ Checking Python...
python --version

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install Cython first (required for building NumPy, Pandas, etc.)
echo 📦 Installing build dependencies...
pip install Cython

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Dependencies installed successfully!
echo.
echo 📖 Next steps:
echo   1. Set up PostgreSQL and update DATABASE_URL in .env
echo   2. Run: python cli.py init-db (to initialize database)
echo   3. Run: python cli.py generate-sample-data (to create sample data)
echo   4. Run: python -m uvicorn app.main:app --reload (to start server)
echo.
echo 🌐 Server will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/api/docs
echo.
popd
pause
