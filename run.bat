@echo off
title Ztop Spectop
chcp 65001 >nul
cd /d "%~dp0"

:: Check for virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

:: Run Ztop Spectop using Python
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python main.py %*
    goto finish
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 main.py %*
    goto finish
)

echo.
echo [ERROR] Python was not found in your system PATH.
echo Please install Python 3.10+ from https://www.python.org/ or add it to PATH.
echo.
pause
exit /b 1

:finish
:: If the application exited abnormally, keep the window open so errors can be inspected
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
