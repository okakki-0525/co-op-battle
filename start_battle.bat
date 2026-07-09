@echo off
cd /d "%~dp0"

set PYTHONUTF8=1

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" app.py
  goto end
)

if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" app.py
  goto end
)

where py >nul 2>nul
if not errorlevel 1 (
  py app.py
  goto end
)

where python >nul 2>nul
if not errorlevel 1 (
  python app.py
  goto end
)

echo Python was not found, so the game could not start.
echo.
echo Install Python and enable "Add python.exe to PATH".
echo If you use a virtual environment, place it as .venv or venv in this project folder.

:end
pause
