#!/bin/bash

# Indices Web Application - Render Backend Deployment Script
# Deploys backend to Render.com

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  Render Backend Deployment Script"
echo "========================================"
echo ""

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy       Deploy to Render (requires render CLI)"
    echo "  up          Create and start Render service"
    echo "  down       Stop Render service"
    echo "  logs        View deployment logs"
    echo "  status      Check service status"
    echo "  update      Trigger new deployment"
    echo "  ssh         SSH into service"
    echo ""
    echo "Environment:"
    echo "  RENDER_API_KEY    Render API key (required)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 up"
    echo "  $0 logs"
}

check_prereqs() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required"
        exit 1
    fi
    
    print_status "Python version: $(python3 --version)"
}

deploy() {
    print_status "Deploying backend to Render..."
    
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not installed"
        print_status "Installing Render CLI..."
        pip install render-cli
    fi
    
    render deploy --spec render.yaml --yes
    
    print_success "Deployed to Render"
}

create_service() {
    print_status "Creating Render service..."
    
    if ! command -v render &> /dev/null; then
        print_warning "Installing Render CLI..."
        pip install render-cli
    fi
    
    render services create --spec render.yaml --yes
    
    print_success "Service created on Render"
}

stop_service() {
    print_status "Stopping Render service..."
    
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render services stop indices-backend
    
    print_success "Service stopped"
}

start_service() {
    print_status "Starting Render service..."
    
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render services start indices-backend
    
    print_success "Service started"
}

check_status() {
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render services get indices-backend
}

view_logs() {
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render logs indices-backend --tail 100
}

trigger_update() {
    print_status "Triggering new deployment..."
    
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render deploy --spec render.yaml --yes
    
    print_success "Deployment triggered"
}

ssh_service() {
    print_status "Opening SSH to Render service..."
    
    if ! command -v render &> /dev/null; then
        print_error "Render CLI not installed"
        exit 1
    fi
    
    render ssh indices-backend
}

setup_render() {
    print_status "Setting up Render account..."
    
    if ! command -v render &> /dev/null; then
        print_warning "Installing Render CLI..."
        pip install render-cli
    fi
    
    render login
    
    print_success "Render CLI configured"
}

init_project() {
    print_status "Checking project configuration..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "backend/api/main.py" ]; then
        print_error "backend/api/main.py not found"
        exit 1
    fi
    
    if [ ! -f "render.yaml" ]; then
        print_warning "render.yaml not found, creating..."
        cat > render.yaml << 'EOF'
services:
  - name: indices-backend
    type: web
    region: oregon
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend/api && python main.py
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 5050
EOF
        print_success "render.yaml created"
    fi
    
    print_success "Project ready for Render deployment"
}

case "${1:-}" in
    "deploy")
        check_prereqs
        deploy
        ;;
    "up")
        check_prereqs
        create_service
        ;;
    "down")
        stop_service
        ;;
    "start")
        start_service
        ;;
    "logs")
        view_logs
        ;;
    "status")
        check_status
        ;;
    "update")
        check_prereqs
        trigger_update
        ;;
    "ssh")
        ssh_service
        ;;
    "init")
        init_project
        ;;
    "setup")
        setup_render
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    "")
        usage
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac