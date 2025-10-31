#!/bin/bash
# Convenience script to run load tests

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Political Agent Load Testing${NC}"
echo "================================"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Attempting to activate venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo "No venv found. Please activate your virtual environment first."
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Make sure your environment variables are set."
fi

echo ""
echo "Select test type:"
echo "  1) Quick test (3 queries, readable output)"
echo "  2) Light load test (10 iterations)"
echo "  3) Medium load test (25 iterations)"
echo "  4) Heavy load test (50 iterations)"
echo "  5) Stress test (100 iterations, 3 concurrent)"
echo "  6) Custom"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}Running quick test...${NC}\n"
        python test_quick.py
        ;;
    2)
        echo -e "\n${GREEN}Running light load test...${NC}\n"
        python test_load.py --iterations 10
        ;;
    3)
        echo -e "\n${GREEN}Running medium load test...${NC}\n"
        python test_load.py --iterations 25
        ;;
    4)
        echo -e "\n${GREEN}Running heavy load test...${NC}\n"
        python test_load.py --iterations 50
        ;;
    5)
        echo -e "\n${GREEN}Running stress test...${NC}\n"
        python test_load.py --iterations 100 --concurrent 3
        ;;
    6)
        read -p "Enter number of iterations: " iterations
        read -p "Enter concurrent requests: " concurrent
        echo -e "\n${GREEN}Running custom test...${NC}\n"
        python test_load.py --iterations $iterations --concurrent $concurrent
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Test complete!${NC}"
