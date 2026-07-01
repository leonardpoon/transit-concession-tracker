@echo off
setlocal

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "PYTHON_EXE=venv\Scripts\python.exe"
if exist "%~dp0..\..\venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0..\..\venv\Scripts\python.exe"
set "PYI_WORKPATH=%TEMP%\transit-tracker-pyinstaller-build"

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

"%PYTHON_EXE%" -m PyInstaller transit-tracker.spec --noconfirm --workpath "%PYI_WORKPATH%" --distpath "%~dp0dist"
if errorlevel 1 exit /b 1

echo.
echo Build complete. Check the dist\transit-tracker folder.
echo Put a filled .env file beside transit-tracker.exe before running it.
