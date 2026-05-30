@echo off
title richl3rrrrr Firmware Flasher
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python not found.
    echo     Install from Microsoft Store or https://python.org
    echo     Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo [*] Installing dependencies...
python -m pip install pyserial --quiet 2>nul

echo [*] Launching richl3rrrrr Flasher...
pythonw flasher_gui.py
