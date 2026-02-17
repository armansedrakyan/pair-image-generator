#!/bin/bash

echo "========================================="
echo "Image Generator - Dependency Setup"
echo "========================================="
echo ""

# Install python3-venv if not already installed
echo "Step 1: Installing python3-venv..."
sudo apt install python3.12-venv -y

if [ $? -ne 0 ]; then
    echo "Error: Failed to install python3-venv"
    exit 1
fi

echo ""
echo "Step 2: Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Step 3: Installing Python packages..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install packages"
    exit 1
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run the image generator:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the script: python generate_images.py"
echo ""
