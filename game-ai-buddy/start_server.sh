#!/bin/bash
echo "========================================"
echo "  Game AI Buddy Server - Mac/Linux"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install -r server/requirements.txt
fi

echo "Starting Game AI Buddy Server..."
echo "Open config.json to add your Gemini API key."
echo ""
venv/bin/python server/main.py
