#!/bin/bash
# ============================================================
#  DocuMind RAG Chatbot — Quick Start Script
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        DocuMind RAG Chatbot              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found.${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example backend/.env
        echo -e "${GREEN}✅ Created backend/.env from .env.example${NC}"
        echo -e "${RED}❗ Edit backend/.env and add your GROQ_API_KEY before continuing.${NC}"
        echo -e "   Get your free key at: ${CYAN}https://console.groq.com${NC}"
        echo ""
        read -p "Press Enter after adding your API key..."
    fi
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"

# Create virtual env if not exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}⏳ Creating virtual environment...${NC}"
    python3 -m venv backend/venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate and install
echo -e "${YELLOW}⏳ Installing dependencies (first run takes a few minutes)...${NC}"
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Load .env
export $(grep -v '^#' backend/.env | xargs)

# Start server
echo ""
echo -e "${GREEN}🚀 Starting DocuMind backend on http://localhost:8000${NC}"
echo -e "${CYAN}📖 Open your browser at: http://localhost:8000${NC}"
echo -e "   Press Ctrl+C to stop"
echo ""

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
