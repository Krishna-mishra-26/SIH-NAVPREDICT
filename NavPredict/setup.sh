#!/bin/bash

# NavPredict Setup Script

echo "🚀 NavPredict Setup Script"
echo "========================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

echo "✓ Python and Node.js found"

# Setup backend
echo -e "\n📦 Setting up backend..."
cd backend
pip install -r requirements.txt
cd ..

# Setup frontend
echo -e "\n📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo -e "\n✓ Setup complete!"
echo -e "\n📝 Quick Start Guide:"
echo "1. Start backend: cd backend && python app.py"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Open browser: http://localhost:3000"
