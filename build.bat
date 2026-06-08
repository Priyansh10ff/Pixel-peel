@echo off
setlocal EnableDelayedExpansion
title PixelPeel — Windows Build
color 0A

:: ─────────────────────────────────────────────────────────────
::  PixelPeel — Windows Build Script
::  Produces  dist\PixelPeel\PixelPeel.exe
::  Users only need the dist\PixelPeel\ folder — no Python.
::
::  Usage:  build.bat
::  Output: dist\PixelPeel-Windows.zip  (ready to upload to GitHub Releases)
:: ─────────────────────────────────────────────────────────────

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
set "VENV=%APP_DIR%\.venv"
set "PY=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         PixelPeel — Windows Build Script                ║
echo  ║   Output: dist\PixelPeel\PixelPeel.exe                  ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Ensure venv exists ───────────────────────────────────────
if not exist "%PY%" (
    echo  [setup]  No .venv found — running installer first...
    call "%APP_DIR%\install.bat"
    if !errorlevel! neq 0 ( pause & exit /b 1 )
)

:: ── Install / upgrade PyInstaller ────────────────────────────
echo  [1/4]  Installing PyInstaller...
"%PIP%" install pyinstaller --upgrade --quiet
if !errorlevel! neq 0 ( echo  [ERROR]  pip failed. & pause & exit /b 1 )
echo  [✓]  PyInstaller ready.

:: ── Generate icon ────────────────────────────────────────────
echo  [2/4]  Generating icon...
if not exist "%APP_DIR%\assets" mkdir "%APP_DIR%\assets"
"%PY%" "%APP_DIR%\assets\create_icon.py" "%APP_DIR%\assets\pixelpeel.ico" 2>nul
if exist "%APP_DIR%\assets\pixelpeel.ico" (
    echo  [✓]  Icon generated.
) else (
    echo  [!]  Icon generation skipped (non-fatal).
)

:: ── PyInstaller build ────────────────────────────────────────
echo  [3/4]  Building with PyInstaller (1–3 minutes) ...
"%VENV%\Scripts\pyinstaller.exe" "%APP_DIR%\pixelpeel.spec" ^
    --distpath "%APP_DIR%\dist" ^
    --workpath "%APP_DIR%\build" ^
    --noconfirm

if !errorlevel! neq 0 (
    echo.
    echo  [ERROR]  Build failed. Check output above.
    echo           Common fixes:
    echo           - Delete build\ and dist\ then retry
    echo           - pip install --upgrade pyinstaller
    pause & exit /b 1
)
echo  [✓]  Build complete:  dist\PixelPeel\PixelPeel.exe

:: ── Zip for distribution ─────────────────────────────────────
echo  [4/4]  Creating release ZIP...
if exist "%APP_DIR%\dist\PixelPeel-Windows.zip" (
    del "%APP_DIR%\dist\PixelPeel-Windows.zip"
)
powershell -NoProfile -Command ^
    "Compress-Archive -Path '%APP_DIR%\dist\PixelPeel' -DestinationPath '%APP_DIR%\dist\PixelPeel-Windows.zip'"

if exist "%APP_DIR%\dist\PixelPeel-Windows.zip" (
    echo  [✓]  dist\PixelPeel-Windows.zip  created.
) else (
    echo  [!]  Zip failed — folder dist\PixelPeel\ is still usable.
)

:: ── Done ─────────────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   Build complete!                                       ║
echo  ║                                                         ║
echo  ║   Test  :  dist\PixelPeel\PixelPeel.exe                ║
echo  ║   Upload:  dist\PixelPeel-Windows.zip                  ║
echo  ║            → GitHub Releases (tag: v1.0.0)             ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause
