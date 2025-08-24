#!/bin/bash
# AutoCraftCV Setup Script for Unix/Linux/macOS
# This script automates the setup process

echo "============================================"
echo "   AutoCraftCV Setup Script"
echo "============================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager or https://python.org"
    exit 1
fi

echo "✅ Python is installed"
echo

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "✅ Found manage.py - in correct directory"
echo

# Run the Python setup script
echo "🚀 Running Python setup script..."
python3 setup.py

if [ $? -ne 0 ]; then
    echo "❌ Setup failed. Please check the errors above."
    exit 1
fi

echo
echo "============================================"
echo "   Setup Complete! 🎉"
echo "============================================"
echo
echo "Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Start development server: python manage.py runserver"
echo "   3. Open browser to: http://127.0.0.1:8000"
echo
echo "For API configuration (paid version):"
echo "   - Edit .env file with your API keys"
echo "   - Set APP_VERSION=paid in .env"
echo
echo "For help, see README.md"
echo
