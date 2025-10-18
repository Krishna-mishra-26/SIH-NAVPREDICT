@echo off
REM NavPredict Setup Script for Windows

echo.
echo 🚀 NavPredict Setup Script
echo ==========================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    exit /b 1
)

echo ✓ Python and Node.js found

REM Setup backend
echo.
echo 📦 Setting up backend...
cd backend
pip install -r requirements.txt
cd ..

REM Setup frontend
echo.
echo 📦 Setting up frontend...
cd frontend
call npm install
cd ..

echo.
echo ✓ Setup complete!
echo.
echo 📝 Quick Start Guide:
echo 1. Start backend: cd backend ^&^& python app.py
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Open browser: http://localhost:3000
echo.
pause
