@echo off
setlocal

set "LOCAL_PYTHON=C:\Users\nosam\AppData\Local\Python\pythoncore-3.14-64\python.exe"

if exist "%LOCAL_PYTHON%" (
    "%LOCAL_PYTHON%" -m uvicorn app.main:app --reload
    exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -m uvicorn app.main:app --reload
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -m uvicorn app.main:app --reload
    exit /b %ERRORLEVEL%
)

echo Could not find a Python interpreter.
echo Install Python 3.11+ or run:
echo C:\Users\nosam\AppData\Local\Python\pythoncore-3.14-64\python.exe -m uvicorn app.main:app --reload
exit /b 1
