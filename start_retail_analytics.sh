#!/bin/bash

# 🏪 Retail Analytics System Launcher
# Quick launcher script for the retail analytics menu

echo "🏪 RETAIL ANALYTICS SYSTEM LAUNCHER"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -f "retail_menu.py" ]; then
    echo "❌ Error: retail_menu.py not found in current directory"
    echo "📁 Please run this script from the python project directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "🔧 Please ensure .venv directory exists"
    exit 1
fi

# Check if database exists
if [ ! -f "sales_timeseries.db" ]; then
    echo "⚠️  Warning: Database not found"
    echo "💡 You'll need to create the database (Menu Option 1)"
    echo ""
fi

echo "🚀 Starting Retail Analytics System..."
echo ""

# Launch the menu system
.venv/bin/python retail_menu.py
