#!/bin/bash

# macOS Retail Analytics System - Complete Rebuild
# Double-click to run this script on macOS

clear
echo "🍎 macOS Retail Analytics System - Complete Rebuild"
echo "=" * 55

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "📥 Installing required packages..."
pip install pandas numpy matplotlib seaborn duckdb fastapi uvicorn tqdm

if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ All packages installed successfully"

# Remove existing database if it exists
if [ -f "sales_timeseries.db" ]; then
    echo "🗑️  Removing existing database..."
    rm sales_timeseries.db
    echo "✅ Database removed"
fi

# Generate new database
echo "⚡ Generating new comprehensive retail database..."
python3 main.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate database"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "🎉 SYSTEM REBUILD COMPLETE!"
echo "=" * 30
echo "📊 Database: sales_timeseries.db"
echo "🔧 Virtual environment: .venv/"
echo "📁 All files ready in: $SCRIPT_DIR"
echo ""
echo "🚀 Available tools:"
echo "   • python3 main.py --menu       (Launch retail menu)"
echo "   • python3 pack_csv.py          (CSV pack/unpack tool)"
echo "   • python3 app.py               (Start FastAPI server)"
echo "   • python3 retail_menu.py       (Direct menu access)"
echo ""

# Ask if user wants to launch the menu
read -p "🚀 Launch retail menu now? (y/n): " launch_menu
if [[ $launch_menu =~ ^[Yy]$ ]]; then
    echo "🚀 Starting retail menu..."
    python3 main.py --menu
fi

echo "👋 Script completed. You can close this window."
read -p "Press Enter to exit..."
