#!/bin/bash

# Linux Retail Analytics System - Complete Rebuild
# Run this script on Linux systems

clear
echo "🐧 Linux Retail Analytics System - Complete Rebuild"
echo "=" * 50

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
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
        echo "You may need to install python3-venv:"
        echo "  Ubuntu/Debian: sudo apt install python3-venv"
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
    echo "You may need to install additional development packages:"
    echo "  Ubuntu/Debian: sudo apt install python3-dev build-essential"
    echo "  CentOS/RHEL:   sudo yum groupinstall 'Development Tools'"
    echo "  Fedora:        sudo dnf groupinstall 'Development Tools'"
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

echo "👋 Script completed."
read -p "Press Enter to exit..."
