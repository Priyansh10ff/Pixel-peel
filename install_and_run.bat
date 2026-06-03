@echo off
:: ─────────────────────────────────────────────────────────────
::  PixelPeel — Windows Setup & Launch Script
::  Double-click to install dependencies and start the app.
:: ─────────────────────────────────────────────────────────────
title PixelPeel Setup

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║          PixelPeel  v1.0.0                ║
echo  ║   AI Background Remover — 100%% Local     ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR]  Python not found.
    echo           Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR]  pip not found. Re-install Python and enable pip.
    pause
    exit /b 1
)

echo  [1/3]  Upgrading pip...
python -m pip install --upgrade pip --quiet

echo  [2/3]  Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR]  Dependency installation failed.
    echo           Try:  pip install -r requirements.txt
    pause
    exit /b 1
)

echo  [3/3]  Launching PixelPeel...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR]  PixelPeel exited with an error.
    pause
)
