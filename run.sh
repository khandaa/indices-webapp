#!/bin/bash

# Indices Web Application Runner Script
# This script starts both the backend and frontend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application configuration
BACKEND_DIR="backend/api"
FRONTEND_DIR="frontend"
BACKEND_PORT=5050
FRONTEND_PORT=3050
VENV_DIR="venv"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    print_warning "Killing process on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv $VENV_DIR
        print_success "Virtual environment created"
    fi
    
    print_status "Activating virtual environment..."
    source $VENV_DIR/bin/activate
    
    print_status "Installing backend dependencies..."
    pip install -r backend/api/requirements.txt
    pip install pandas yfinance  # Additional dependencies
    print_success "Backend dependencies installed"
}

# Function to check if frontend port is in use
check_frontend_port() {
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use"
        read -p "Do you want to run the app on another port and start it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter the new port number: " FRONTEND_PORT
            start_frontend
        else
            print_error "Please free up port $FRONTEND_PORT and try again"
            exit 1
        fi
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend development server..."
    cd $FRONTEND_DIR
    
    # Start frontend in background
    PORT=$FRONTEND_PORT npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend started successfully
    if check_port $FRONTEND_PORT; then
        print_success "Frontend server started on port $FRONTEND_PORT (PID: $FRONTEND_PID)"
    else
        print_error "Frontend server failed to start"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    cd backend
    python setup_database.py
    cd ..
    print_success "Database setup completed"
}

# Function to install frontend dependencies
setup_frontend() {
    print_status "Installing frontend dependencies..."
    cd $FRONTEND_DIR
    npm install
    cd ..
    print_success "Frontend dependencies installed"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd $BACKEND_DIR
    
    # Activate virtual environment
    source ../../$VENV_DIR/bin/activate
    
    # Start backend in background
    python main.py &
    BACKEND_PID=$!
    cd ../..
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend started successfully
    if check_port $BACKEND_PORT; then
        print_success "Backend server started on port $BACKEND_PORT (PID: $BACKEND_PID)"
    else
        print_error "Backend server failed to start"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend development server..."
    cd $FRONTEND_DIR
    
    # Start frontend in background
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend started successfully
    if check_port $FRONTEND_PORT; then
        print_success "Frontend server started on port $FRONTEND_PORT (PID: $FRONTEND_PID)"
    else
        print_error "Frontend server failed to start"
        exit 1
    fi
}

# Function to cleanup processes
cleanup() {
    print_status "Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    # Kill any remaining processes on ports
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    print_success "All servers stopped"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "========================================"
    echo "  Indices Web Application Runner"
    echo "========================================"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    echo ""
    
    # Check if ports are available
    if check_port $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is already in use"
        read -p "Do you want to kill the process and continue? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port $BACKEND_PORT
        else
            print_error "Please free up port $BACKEND_PORT and try again"
            exit 1
        fi
    fi
    
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use"
        read -p "Do you want to kill the process and continue? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port $FRONTEND_PORT
        else
            print_error "Please free up port $FRONTEND_PORT and try again"
            exit 1
        fi
    fi
    
    echo ""
    
    # Setup and start services
    setup_venv
    setup_database
    setup_frontend
    
    echo ""
    print_status "Starting application services..."
    echo ""
    
    start_backend
    start_frontend
    
    echo ""
    echo "========================================"
    echo "  Application Started Successfully!"
    echo "========================================"
    echo ""
    echo "🚀 Frontend: http://localhost:$FRONTEND_PORT"
    echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
    echo "📚 API Docs: http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Skip setup if database already exists
    if [ -d "$BACKEND_DIR/database" ]; then
        print_status "Database already exists. Skipping database setup."
    else
        setup_database
    fi
    
    # Skip start backend if it's already running
    if check_port $BACKEND_PORT; then
        print_status "Backend server already running. Skipping backend start."
    else
        start_backend
    fi
    
    echo ""
    
    # Keep script running
    while true; do
        sleep 1
    done
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        print_status "Stopping all services..."
        kill_port $BACKEND_PORT
        kill_port $FRONTEND_PORT
        print_success "All services stopped"
        exit 0
        ;;
    "status")
        echo "Checking service status..."
        echo ""
        if check_port $BACKEND_PORT; then
            echo "✅ Backend: Running on port $BACKEND_PORT"
        else
            echo "❌ Backend: Not running"
        fi
        
        if check_port $FRONTEND_PORT; then
            echo "✅ Frontend: Running on port $FRONTEND_PORT"
        else
            echo "❌ Frontend: Not running"
        fi
        echo ""
        exit 0
        ;;
    "setup")
        print_status "Running setup only..."
        setup_venv
        setup_database
        setup_frontend
        print_success "Setup completed"
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo "Indices Web Application Runner"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)    Start the application (default)"
        echo "  setup        Run setup only (install dependencies, setup database)"
        echo "  status       Check if services are running"
        echo "  stop         Stop all running services"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0           # Start the application"
        echo "  $0 setup     # Run setup only"
        echo "  $0 status    # Check service status"
        echo "  $0 stop      # Stop all services"
        exit 0
        ;;
    "")
        # Default behavior - start the application
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
