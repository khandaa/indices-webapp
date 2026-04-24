#!/bin/bash

# Setup YFinance Data Fetcher
# This script installs dependencies and sets up the yfinance data fetcher

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if virtual environment exists
VENV_DIR="../venv"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Virtual environment not found. Creating..."
    python3 -m venv $VENV_DIR
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies
print_status "Installing yfinance dependencies..."
pip install -r requirements_yfinance.txt

print_success "YFinance data fetcher setup completed!"
echo ""
echo "Usage examples:"
echo "  python fetch_yfinance_data.py all                    # Fetch all indices data"
echo "  python fetch_yfinance_data.py all 2023-01-01       # Fetch from specific date"
echo "  python fetch_yfinance_data.py single NIFTYBEES       # Fetch single index"
echo "  python fetch_yfinance_data.py status                 # Show data status"
