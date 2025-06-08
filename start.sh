#!/bin/bash

# Chandigarh Policy Assistant - Hybrid Search System
# Startup script

echo "🚀 Starting Chandigarh Policy Assistant Hybrid Search System"
echo "============================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "⚠️  config.py not found. Please copy config.py.example to config.py and configure your settings."
    exit 1
fi

# Start the server
echo "🌐 Starting hybrid search server..."
python run_server.py 