#!/bin/bash

# Indices Web Application Deployment Script
# Deploys frontend to Vercel
# Note: Backend (FastAPI) needs to be deployed separately to a Python hosting service

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  Vercel Deployment Script"
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
    echo "  build         Build frontend for production"
    echo "  deploy       Deploy to Vercel (requires Vercel CLI)"
    echo "  both        Build and deploy"
    echo "  status      Check Vercel deployment status"
    echo "  logs        View Vercel deployment logs"
    echo ""
    echo "Environment Variables:"
    echo "  VERCEL_API_URL    Backend API URL (required for production)"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  VERCEL_API_URL=https://api.example.com $0 deploy"
    echo "  $0 both"
}

build_frontend() {
    print_status "Building frontend..."
    
    cd frontend
    
    if [ -f "../.env" ]; then
        print_status "Using .env.production for build..."
        cp -n ../.env .env.production 2>/dev/null || true
    elif [ -n "$VERCEL_API_URL" ]; then
        print_status "Setting VERCEL_API_URL for build..."
        echo "REACT_APP_API_URL=$VERCEL_API_URL" > .env.production
    fi
    
    npm run build
    
    cd ..
    
    print_success "Frontend built successfully"
    echo "Build output: frontend/build"
}

deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not installed"
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    cd frontend
    
    if [ -n "$VERCEL_API_URL" ]; then
        print_status "Setting production API URL: $VERCEL_API_URL"
        echo "REACT_APP_API_URL=$VERCEL_API_URL" > .env.production
    fi
    
    vercel --prod --yes
    
    cd ..
    
    print_success "Deployed to Vercel"
}

check_status() {
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not installed"
        exit 1
    fi
    
    vercel ps
}

view_logs() {
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not installed"
        exit 1
    fi
    
    vercel logs
}

init_vercel() {
    print_status "Initializing Vercel project..."
    
    cd frontend
    
    if [ -n "$VERCEL_API_URL" ]; then
        echo "REACT_APP_API_URL=$VERCEL_API_URL" > .env.local
    fi
    
    vercel link --yes --cwd .
    
    cd ..
    
    print_success "Vercel project initialized"
}

case "${1:-}" in
    "build")
        build_frontend
        ;;
    "deploy")
        deploy_vercel
        ;;
    "both")
        build_frontend
        deploy_vercel
        ;;
    "status")
        check_status
        ;;
    "logs")
        view_logs
        ;;
    "init")
        init_vercel
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