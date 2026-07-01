@echo off
setlocal

if not exist .env (
    echo Missing .env file.
    echo Create .env from .env.example before building an embedded-env executable.
    exit /b 1
)

echo WARNING: This embeds your .env secrets inside the executable.
echo Only use this for your own trusted computers.
echo.

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "PYTHON_EXE=venv\Scripts\python.exe"
if exist "%~dp0..\..\venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0..\..\venv\Scripts\python.exe"
set "PYI_WORKPATH=%TEMP%\transit-tracker-pyinstaller-build"
set "PYI_SPECPATH=%TEMP%\transit-tracker-pyinstaller-spec"

"%PYTHON_EXE%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip was not found for %PYTHON_EXE%.
    echo Trying to install pip with ensurepip...
    "%PYTHON_EXE%" -m ensurepip --upgrade
    if errorlevel 1 (
        echo Could not install pip for %PYTHON_EXE%.
        echo Create a fresh local venv with a normal Windows Python install:
        echo   python -m venv .venv
        echo   .venv\Scripts\python -m pip install --upgrade pip
        exit /b 1
    )
)

"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

"%PYTHON_EXE%" -m PyInstaller ^
  --onefile ^
  --console ^
  --name transit-tracker ^
  --icon "%~dp0assets\ez-track-icon.ico" ^
  --collect-data certifi ^
  --collect-all mysql.connector ^
  --hidden-import openpyxl ^
  --exclude-module streamlit ^
  --exclude-module pandas ^
  --exclude-module plotly ^
  --add-data "%~dp0.env;." ^
  --noconfirm ^
  --workpath "%PYI_WORKPATH%" ^
  --specpath "%PYI_SPECPATH%" ^
  --distpath "%~dp0dist" ^
  main.py ^
  --clean
if errorlevel 1 exit /b 1

echo.
echo Build complete. Check dist\transit-tracker.exe.
echo This executable contains the .env values from this build machine.
