@echo off
setlocal EnableDelayedExpansion
title PixelPeel Installer

:: ─────────────────────────────────────────────────────────────
::  PixelPeel — Windows One-Click Installer
::  Installs dependencies, generates icon, and creates a
::  permanent Desktop shortcut.  Run once; launch forever.
:: ─────────────────────────────────────────────────────────────

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
set "VENV_DIR=%APP_DIR%\.venv"
set "ICON_PATH=%APP_DIR%\assets\pixelpeel.ico"
set "VBS_PATH=%APP_DIR%\pixelpeel_launch.vbs"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║           PixelPeel  v1.0.0  — Installer                ║
echo  ║   100%% Local Background Remover  ^|  No Cloud, No AI   ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Step 0: Verify Python ────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR]  Python was not found on your PATH.
    echo           Please install Python 3.9+ from https://python.org
    echo           During install, tick "Add Python to PATH".
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [✓]  Python %PYVER% found.

:: ── Step 1: Create virtual environment ──────────────────────
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo  [1/5]  Virtual environment already exists — skipping creation.
) else (
    echo  [1/5]  Creating virtual environment in .venv ...
    python -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo  [ERROR]  Could not create virtual environment.
        pause & exit /b 1
    )
    echo  [✓]  Virtual environment created.
)

:: ── Step 2: Upgrade pip + install dependencies ───────────────
echo  [2/5]  Installing dependencies (may take a minute on first run) ...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%VENV_DIR%\Scripts\pip.exe" install -r "%APP_DIR%\requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR]  Dependency installation failed.
    echo           Run manually: "%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt
    pause & exit /b 1
)
echo  [✓]  Dependencies installed.

:: ── Step 3: Generate app icon ────────────────────────────────
echo  [3/5]  Generating app icon ...
if not exist "%APP_DIR%\assets" mkdir "%APP_DIR%\assets"
"%VENV_DIR%\Scripts\python.exe" "%APP_DIR%\assets\create_icon.py" "%ICON_PATH%" 2>nul
if exist "%ICON_PATH%" (
    echo  [✓]  Icon created.
) else (
    echo  [!]  Icon generation skipped (non-fatal).
    set "ICON_PATH="
)

:: ── Step 4: Write VBScript launcher (no console window) ──────
echo  [4/5]  Writing silent launcher ...
(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.CurrentDirectory = "%APP_DIR:\=\\%"
    echo WshShell.Run """" ^& "%VENV_DIR:\=\\%\Scripts\pythonw.exe" ^& """" ^& " """ ^& "%APP_DIR:\=\\%\main.py" ^& """", 0, False
) > "%VBS_PATH%"
echo  [✓]  Launcher written.

:: ── Step 5: Create Desktop shortcut via PowerShell ───────────
echo  [5/5]  Creating Desktop shortcut ...

set "PS1=%TEMP%\pixelpeel_shortcut.ps1"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\PixelPeel.lnk"

(
    echo $ws = New-Object -ComObject WScript.Shell
    echo $s  = $ws.CreateShortcut('%DESKTOP_LNK:\=\\%'^)
    echo $s.TargetPath       = 'wscript.exe'
    echo $s.Arguments        = '"%VBS_PATH:\=\\%"'
    echo $s.WorkingDirectory = '%APP_DIR:\=\\%'
    if defined ICON_PATH (
        echo $s.IconLocation = '%ICON_PATH:\=\\%,0'
    )
    echo $s.Description      = 'PixelPeel - Background Remover'
    echo $s.Save^(^)
) > "%PS1%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" >nul 2>&1
del "%PS1%" 2>nul

if exist "%DESKTOP_LNK%" (
    echo  [✓]  Desktop shortcut created: %DESKTOP_LNK%
) else (
    echo  [!]  Could not auto-create shortcut.  To launch manually:
    echo       wscript "%VBS_PATH%"
)

:: ── Done ─────────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   Installation complete!                                ║
echo  ║                                                         ║
echo  ║   ▶  Double-click  "PixelPeel"  on your Desktop        ║
echo  ║      to launch the app at any time — no terminal       ║
echo  ║      or scripts needed.                                 ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause
