#!/bin/bash

# Indices Web Application Deployment Script
# Supports deployment to Vercel (frontend) and various backend hosting options

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configurations
DEFAULT_FRONTEND_URL="https://your-app.vercel.app"
DEFAULT_BACKEND_URL="https://your-backend.onrender.com"

# Function to print colored output
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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
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
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Setup environment files
setup_environment() {
    local backend_url=${1:-$DEFAULT_BACKEND_URL}
    
    print_status "Setting up environment..."
    
    # Create .env.production for frontend
    cat > frontend/.env.production << EOF
REACT_APP_API_URL=$backend_url
REACT_APP_ENV=production
EOF
    
    # Create .env for backend if it doesn't exist
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
DATABASE_URL=sqlite:///database/index-database.db
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3050
ENVIRONMENT=production
EOF
    fi
    
    print_success "Environment files configured"
}

# Build frontend for production
build_frontend() {
    print_status "Building frontend for production..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Build for production
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Frontend built successfully"
        echo "Build output: frontend/build"
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    cd ..
}

# Deploy to Vercel
deploy_vercel() {
    local backend_url=${1:-$DEFAULT_BACKEND_URL}
    
    print_status "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    cd frontend
    
    # Set production API URL
    echo "REACT_APP_API_URL=$backend_url" > .env.production
    
    # Deploy to Vercel
    vercel --prod --yes
    
    if [ $? -eq 0 ]; then
        print_success "Deployed to Vercel successfully"
        
        # Get deployment URL
        DEPLOYMENT_URL=$(vercel ls --scope=vercel 2>/dev/null | grep -E '^\s*.*?https://.*vercel\.app' | head -1 | sed 's/.*\(https:\/\/[^)]*\).*/\1/' || echo "$DEFAULT_FRONTEND_URL")
        
        echo "🚀 Frontend URL: $DEPLOYMENT_URL"
        echo "🔧 Backend API: $backend_url"
    else
        print_error "Vercel deployment failed"
        exit 1
    fi
    
    cd ..
}

# Deploy to Render (backend)
deploy_render() {
    print_status "Deploying backend to Render..."
    
    # Check if render CLI is installed
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not found. Manual deployment required."
        echo "Visit: https://render.com/docs/deploy"
        echo ""
        echo "Manual deployment steps:"
        echo "1. Connect your GitHub repository"
        echo "2. Select 'Web Service' as service type"
        echo "3. Choose 'Python' as runtime"
        echo "4. Set build command: 'cd backend/api && python main.py'"
        echo "5. Add environment variables as needed"
        return 1
    fi
    
    # Deploy using Render CLI
    render deploy --service-type web --runtime python --build-command "cd backend/api && python main.py"
    
    if [ $? -eq 0 ]; then
        print_success "Backend deployed to Render successfully"
        
        # Get deployment URL
        BACKEND_URL=$(render ps 2>/dev/null | grep -E '.*?https://.*\.onrender\.com' | head -1 || echo "$DEFAULT_BACKEND_URL")
        
        echo "🔧 Backend URL: $BACKEND_URL"
    else
        print_error "Render deployment failed"
        exit 1
    fi
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying backend to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Manual deployment required."
        echo "Visit: https://railway.app/docs"
        return 1
    fi
    
    # Login and deploy
    railway login
    railway deploy
    
    if [ $? -eq 0 ]; then
        print_success "Backend deployed to Railway successfully"
        
        # Get deployment URL
        BACKEND_URL=$(railway status 2>/dev/null | grep -E '.*?https://.*\.railway\.app' | head -1 || echo "$DEFAULT_BACKEND_URL")
        
        echo "🔧 Backend URL: $BACKEND_URL"
    else
        print_error "Railway deployment failed"
        exit 1
    fi
}

# Deploy to Heroku
deploy_heroku() {
    print_status "Deploying backend to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_warning "Heroku CLI not found. Installing..."
        npm install -g heroku
    fi
    
    # Login if not already logged in
    heroku auth:whoami 2>/dev/null || heroku login
    
    # Create app if doesn't exist
    APP_NAME="indices-api-$(date +%s)"
    heroku create $APP_NAME 2>/dev/null || true
    
    # Deploy
    heroku container:push web
    
    if [ $? -eq 0 ]; then
        print_success "Backend deployed to Heroku successfully"
        echo "🔧 Backend URL: https://$APP_NAME.herokuapp.com"
    else
        print_error "Heroku deployment failed"
        exit 1
    fi
}

# Deploy to PythonAnywhere
deploy_pythonanywhere() {
    print_status "Deploying backend to PythonAnywhere..."
    
    # Check if PythonAnywhere CLI is installed
    if ! command -v pa &> /dev/null; then
        print_warning "PythonAnywhere CLI not found. Installing..."
        pip install pythonanywhere
    fi
    
    # Deploy
    pa deploy
    
    if [ $? -eq 0 ]; then
        print_success "Backend deployed to PythonAnywhere successfully"
        
        # Get deployment URL
        BACKEND_URL=$(pa list 2>/dev/null | grep -E '.*?https://.*\.pythonanywhere\.com' | head -1 || echo "$DEFAULT_BACKEND_URL")
        
        echo "🔧 Backend URL: $BACKEND_URL"
    else
        print_error "PythonAnywhere deployment failed"
        exit 1
    fi
}

# Full stack deployment
deploy_full_stack() {
    local backend_url=${1:-$DEFAULT_BACKEND_URL}
    
    print_status "Starting full stack deployment..."
    
    # Setup environment
    setup_environment $backend_url
    
    # Build frontend
    build_frontend
    
    # Deploy frontend to Vercel
    deploy_vercel $backend_url
    
    # Deploy backend to selected service
    local backend_service=${2:-render}
    
    case $backend_service in
        "render")
            deploy_render
            ;;
        "railway")
            deploy_railway
            ;;
        "heroku")
            deploy_heroku
            ;;
        "pythonanywhere")
            deploy_pythonanywhere
            ;;
        *)
            print_warning "Unknown backend service: $backend_service"
            echo "Available options: render, railway, heroku, pythonanywhere"
            echo "Defaulting to Render..."
            deploy_render
            ;;
    esac
    
    print_success "Full stack deployment completed!"
}

# Check deployment status
check_status() {
    print_status "Checking deployment status..."
    
    # Check Vercel deployment
    if command -v vercel &> /dev/null; then
        echo ""
        echo "🌐 Frontend (Vercel):"
        vercel ls --scope=vercel
    fi
    
    # Check backend deployment (try multiple services)
    echo ""
    echo "🔧 Backend Services:"
    
    if command -v render &> /dev/null; then
        echo "  Render: $(render ps 2>/dev/null | grep -E '.*?https://.*' | head -1 || echo 'Not deployed')"
    fi
    
    if command -v railway &> /dev/null; then
        echo "  Railway: $(railway status 2>/dev/null | grep -E '.*?https://.*' | head -1 || echo 'Not deployed')"
    fi
    
    if command -v heroku &> /dev/null; then
        echo "  Heroku: $(heroku apps --json 2>/dev/null | grep -o '"web_url"' | cut -d'"' -f4 || echo 'Not deployed')"
    fi
    
    if command -v pa &> /dev/null; then
        echo "  PythonAnywhere: $(pa list 2>/dev/null | grep -E '.*?https://.*' | head -1 || echo 'Not deployed')"
    fi
}

# Initialize deployment
init_deployment() {
    print_status "Initializing deployment configuration..."
    
    # Create vercel.json if it doesn't exist
    if [ ! -f "frontend/vercel.json" ]; then
        cat > frontend/vercel.json << EOF
{
  "version": 2,
  "name": "indices-webapp",
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "installCommand": "npm install",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/\$1"
    }
  ]
}
EOF
        print_success "Created vercel.json"
    fi
    
    # Create render.yaml if it doesn't exist
    if [ ! -f "backend/render.yaml" ]; then
        cat > backend/render.yaml << EOF
services:
  - type: web
    name: indices-api
    env: python
    buildCommand: cd backend/api && pip install -r requirements.txt
    startCommand: cd backend/api && python main.py
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        value: sqlite:///database/index-database.db
      - key: CORS_ORIGINS
        value: \${VERCEL_URL:-https://localhost:3050}
EOF
        print_success "Created render.yaml"
    fi
    
    print_success "Deployment configuration initialized"
}

# Show usage
usage() {
    echo "Indices Web Application Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  frontend                   Build frontend for production"
    echo "  vercel                     Deploy frontend to Vercel"
    echo "  render                     Deploy backend to Render"
    echo "  railway                    Deploy backend to Railway"
    echo "  heroku                     Deploy backend to Heroku"
    echo "  pythonanywhere             Deploy backend to PythonAnywhere"
    echo "  full [backend_url] [service]  Deploy full stack (frontend + backend)"
    echo "  status                     Check deployment status"
    echo "  init                        Initialize deployment configuration"
    echo ""
    echo "Options:"
    echo "  backend_url               Backend API URL for frontend"
    echo "  service                   Backend service (render, railway, heroku, pythonanywhere)"
    echo ""
    echo "Environment Variables:"
    echo "  BACKEND_URL              Backend API URL"
    echo "  VERCEL_API_URL           Vercel API URL (for debugging)"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 frontend"
    echo "  $0 vercel https://api.example.com"
    echo "  $0 full https://api.example.com render"
    echo "  $0 full https://api.example.com railway"
    echo "  $0 status"
    echo ""
    echo "Note: Backend requires separate deployment to Python hosting service"
}

# Main execution
main() {
    echo "========================================"
    echo "  Deployment Script"
    echo "========================================"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    case "${1:-}" in
        "init")
            init_deployment
            ;;
        "frontend")
            build_frontend
            ;;
        "vercel")
            deploy_vercel "${2:-$DEFAULT_BACKEND_URL}"
            ;;
        "render")
            deploy_render
            ;;
        "railway")
            deploy_railway
            ;;
        "heroku")
            deploy_heroku
            ;;
        "pythonanywhere")
            deploy_pythonanywhere
            ;;
        "full")
            deploy_full_stack "${2:-$DEFAULT_BACKEND_URL}" "${3:-render}"
            ;;
        "status")
            check_status
            ;;
        "help"|"-h"|"--help")
            usage
            ;;
        "")
            usage
            ;;
        *)
            print_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
