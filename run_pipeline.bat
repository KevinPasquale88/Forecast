@echo off
setlocal EnableExtensions EnableDelayedExpansion
 
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
 
echo =====================================================
echo   🚀 STARTING FULL PIPELINE - PYTHON PROJECT
echo =====================================================
 
echo.
echo [INFO] Checking for Python...
 
set PYTHON_EXE=
where py >nul 2>nul
if not errorlevel 1 (
    set PYTHON_EXE=py -3
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set PYTHON_EXE=python
    )
)
 
if not defined PYTHON_EXE (
    echo [WARN] Python was not found.
    where winget >nul 2>nul
    if not errorlevel 1 (
        echo [INFO] Attempting to install Python with Winget...
        winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        echo [INFO] Please reopen the terminal and run this script again.
        exit /b 1
    ) else (
        echo [ERROR] Python 3 was not found. Install it from https://www.python.org/downloads/windows/
        exit /b 1
    )
)
 
echo [OK] Python found: %PYTHON_EXE%
 
rem ======================================================
rem 1) Virtual Environment + requirements
rem ======================================================
 
echo.
echo [INFO] Checking virtual environment...
 
if not exist "env\Scripts\python.exe" (
    echo [INFO] Creating new Python virtual environment...
    %PYTHON_EXE% -m venv env
)
 
echo [INFO] Activating virtual environment...
call env\Scripts\activate.bat
 
echo.
echo [INFO] Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
 
rem ======================================================
rem 2) Start Ollama
rem ======================================================
 
echo.
echo [INFO] Checking Ollama status...
 
where ollama >nul 2>nul
if not errorlevel 1 (
    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe" >NUL
    if not errorlevel 1 (
        echo [OK] Ollama is already running.
    ) else (
        echo [INFO] Starting Ollama...
        start "" ollama serve
        timeout /t 5 >nul
    )
) else (
    echo [ERROR] Ollama was not found in PATH. Install it from https://ollama.com/download/windows
    exit /b 1
)
 
rem ======================================================
rem 3) Verify required models
rem ======================================================
 
echo.
echo [INFO] Checking Ollama models...
 
set MODELS[0]=jeffh/intfloat-e5-base-v2:q8_0
set MODELS[1]=twwch/m3e-base
set MODELS[2]=zyw0605688/gte-large-zh
set MODELS[3]=jeffh/intfloat-multilingual-e5-large-instruct:q8_0
 
for /L %%i in (0,1,3) do (
    set MODEL=!MODELS[%%i]!
    ollama list | findstr /C:"!MODEL!" >nul
    if not errorlevel 1 (
        echo [OK] Model '!MODEL!' is already installed.
    ) else (
        echo [DOWNLOAD] Downloading model '!MODEL!'...
        ollama pull !MODEL!
    )
)
 
rem ======================================================
rem 4) Run Python pipeline
rem ======================================================
 
echo.
echo =====================================================
echo        🚀 STARTING PYTHON PIPELINE STEPS
echo =====================================================
 
echo >>> START MAIN
%PYTHON_EXE% main.py %*
if errorlevel 1 exit /b 1
 
rem ======================================================
rem 5) Finish
rem ======================================================
 
echo.
echo =====================================================
echo      🎉 PIPELINE COMPLETED SUCCESSFULLY!
echo  Results available in /results/
echo  Report generated: report.md + report.pdf