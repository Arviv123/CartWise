#!/bin/bash
# CartWise Pro - Quick Setup Script
# ==================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         CartWise Pro - Quick Setup                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Install dependencies
echo ""
echo "[2/5] Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env from example
echo ""
echo "[3/5] Creating configuration file..."
if [ ! -f "config/.env" ]; then
    cp config/.env.example config/.env
    echo "✓ Created config/.env"
    echo "⚠️  Please edit config/.env with your credentials"
else
    echo "✓ config/.env already exists"
fi

# Create necessary directories
echo ""
echo "[4/5] Creating directories..."
mkdir -p logs
mkdir -p data
echo "✓ Directories created"

# Test import
echo ""
echo "[5/5] Testing installation..."
python3 -c "
import sys
sys.path.append('src')
from hardware.rs485 import RS485Controller
from sms.inforu import InforuSMSProvider
from sms.otp import OTPManager
print('✓ All modules loaded successfully')
"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit config/.env with your credentials"
echo "2. Run: python3 src/api/main.py"
echo "3. Open: http://localhost:8001"
echo ""
echo "For more info, see README.md"
echo ""
