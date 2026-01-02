#!/bin/bash
# Quick Start Script for Offline AI Chatbot (Linux/Mac)

echo "============================================================"
echo "OFFLINE AI CHATBOT - QUICK START"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "envi" ]; then
    echo "Creating virtual environment..."
    python3 -m venv envi
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source envi/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "============================================================"
echo "SETUP COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Install Ollama from https://ollama.ai"
echo "2. Run: ollama pull gemma:2b"
echo "3. Add documents to data/documents/"
echo "4. Run: python ingest.py"
echo "5. Start Ollama: ollama serve"
echo "6. Run chatbot: python app.py"
echo "7. Open http://localhost:5000"
echo ""
echo "For system check, run: python test_setup.py"
echo "============================================================"
