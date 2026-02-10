#!/bin/bash
# run.sh — One-command startup for Asana Studio
set -e

cd "$(dirname "$0")"

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install deps
pip install -q -r backend/requirements.txt

echo ""
echo "🧘 Starting Asana Studio..."
echo "   Open http://localhost:8000"
echo ""

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
