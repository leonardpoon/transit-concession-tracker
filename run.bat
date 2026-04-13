@echo off
cd /d "%~dp0"
echo ========================================
echo    Transit Tracker
echo ========================================
echo.
echo   [1] Launch CMD app
echo   [2] Launch Dashboard
echo.
set /p choice="Enter choice: "

if "%choice%"=="1" (
    "D:\personal-projects\venv\Scripts\python.exe" main.py
)
if "%choice%"=="2" (
    "D:\personal-projects\venv\Scripts\python.exe" -m streamlit run dashboard.py
)
pause