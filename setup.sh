#!/bin/bash

# SOQL Query Generator Setup Script
# This script sets up the Python environment for the SOQL Query Generator project

echo "Setting up Python environment for SOQL Query Generator..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required."
    echo "Current version: $python_version"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "Python $python_version detected."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        echo "Please make sure you have the venv module installed."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! The Python environment is now ready."
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the example script, run:"
echo "  python example.py"
echo ""
echo "To run the main application, run:"
echo "  python main.py"
echo ""