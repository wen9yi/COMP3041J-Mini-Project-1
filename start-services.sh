#!/bin/bash

# Campus Buzz - Quick Start Script
echo "Starting Campus Buzz services..."

# Check dependencies
echo "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check Node.js and npm (with nvm support)
if ! command -v node &> /dev/null; then
    # Try to load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    if ! command -v node &> /dev/null; then
        echo "Error: Node.js is not installed. Please install Node.js from https://nodejs.org/"
        echo "Or install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        exit 1
    fi
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install Node.js which includes npm."
    exit 1
fi

echo "All dependencies found. Proceeding..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
if ! pip install -r requirements.txt; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# Start Data Service in background
echo "Starting Data Service on port 5002..."
cd services/data-service
python api.py &
DATA_PID=$!
cd ../..

# Wait a moment
sleep 2

# Start Workflow Service in background
echo "Starting Workflow Service on port 5001..."
cd services/workflow
SUBMISSION_EVENT_URL=http://localhost:8080/event DATA_SERVICE_URL=http://localhost:5002 python main.py &
WORKFLOW_PID=$!
cd ../..

# Wait a moment
sleep 2

# Start Submission Event Function in background
echo "Starting Submission Event Function on port 8080..."
cd functions/submission-event
PROCESSOR_URL=http://localhost:8081/process node index.js &
SUBMISSION_EVENT_PID=$!
cd ../../

# Wait a moment
sleep 2

# Start Processor Function in background
echo "Starting Processor Function on port 8081..."
cd functions/processor
RESULT_UPDATE_URL=http://localhost:8082/update python app.py &
PROCESSOR_PID=$!
cd ../../

# Wait a moment
sleep 2

# Start Result Update Function in background
echo "Starting Result Update Function on port 8082..."
cd functions/result-update
DATA_SERVICE_URL=http://localhost:5002 python app.py &
RESULT_UPDATE_PID=$!
cd ../../

# Wait a moment
sleep 2

# Start Frontend (with nvm support)
echo "Starting React Frontend on port 3000..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd services/presentation
if ! npm install; then
    echo "Error: Failed to install npm dependencies."
    kill $DATA_PID $WORKFLOW_PID $SUBMISSION_EVENT_PID $PROCESSOR_PID $RESULT_UPDATE_PID 2>/dev/null
    exit 1
fi

npm start &
FRONTEND_PID=$!

cd ../..

echo ""
echo "All services started successfully!"
echo "Frontend: http://localhost:3000"
echo "Workflow API: http://localhost:5001"
echo "Data API: http://localhost:5002"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $DATA_PID $WORKFLOW_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
