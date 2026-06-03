@echo off
:: ─────────────────────────────────────────────────────────────
::  PixelPeel — Windows Setup & Launch Script
::
::  HOW TO RUN:
::    Option A (recommended): Double-click this file in Explorer
::    Option B (PowerShell):  .\install_and_run.bat
::    Option C (CMD):         install_and_run.bat
:: ─────────────────────────────────────────────────────────────
title PixelPeel Setup

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║          PixelPeel  v1.0.0                ║
echo  ║   AI Background Remover — 100%% Local     ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: ── Check Python ─────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR]  Python not found.
    echo           Please install Python 3.9+ from https://python.org
    echo           Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  Python %PYVER% detected.

:: ── Disable numba JIT (prevents pymatting crash on Python 3.12) ──
set NUMBA_DISABLE_JIT=1

:: ── Check pip ────────────────────────────────────────────────
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR]  pip not found. Re-install Python and enable pip.
    pause
    exit /b 1
)

:: ── Install dependencies ─────────────────────────────────────
echo  [1/3]  Upgrading pip...
python -m pip install --upgrade pip --quiet

echo  [2/3]  Installing dependencies (this may take a few minutes on first run)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR]  Dependency installation failed.
    echo           Try running manually:  pip install -r requirements.txt
    pause
    exit /b 1
)

:: ── Launch ───────────────────────────────────────────────────
echo  [3/3]  Launching PixelPeel...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR]  PixelPeel exited with an error.
    echo           Check the output above for details.
    pause
)
