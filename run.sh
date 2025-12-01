#!/bin/bash
# Linear Task Header - Unix Launcher
# This script launches the Linear Task Header application

echo "Starting Linear Task Header..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python version:"
python3 --version
echo

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "Dependencies not found. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo
echo "Starting application..."
echo "Press Ctrl+C to exit"
echo

# Run the application
python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Application exited with an error"
    read -p "Press Enter to exit..."
fi

