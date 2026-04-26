#!/bin/bash

# FinCloud-AI Backend Quick Start Script

set -e

echo "🚀 FinCloud-AI Backend - Quick Start"
echo "===================================="

# Check Python
echo "✓ Checking Python..."
python --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Cython first (required for building NumPy, Pandas, etc.)
echo "📦 Installing build dependencies..."
pip install Cython

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python cli.py init-db || true

# Generate sample data
echo "📊 Generating sample data..."
python cli.py generate-sample-data --num-records=1000 || true

# Start server
echo ""
echo "🎉 Starting FinCloud-AI Backend..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 Documentation at: http://localhost:8000/api/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
