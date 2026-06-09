#!/bin/bash

echo "================================================"
echo "  Audio Steganography - Multi-Server Startup"
echo "================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3"
    exit 1
fi

# Check if required packages are installed
python3 -c "import flask; import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Installing required packages..."
    pip install -r requirements.txt
    echo ""
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the API server in background
echo "Starting API Server on http://localhost:5000 ..."
python3 api_server.py &
API_PID=$!

# Wait a moment for the API server to start
sleep 2

# Start the static HTTP server in background
echo ""
echo "Starting Static Web Server on http://localhost:8000 ..."
cd frontend
python3 -m http.server 8000 &
WEB_PID=$!
cd ..

# Print instructions
echo ""
echo "================================================"
echo "  Servers are running..."
echo "================================================"
echo ""
echo "API Server:      http://localhost:5000"
echo "Web Interface:   http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait
