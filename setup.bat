@echo off

:: Check if venv exists, skip creation if it does
IF EXIST venv (
    echo venv already exists, skipping creation...
) ELSE (
    echo Creating fresh venv...
    "C:\Program Files\Python310\python.exe" -m venv venv
)

:: Create the directory if it doesn't exist
mkdir ".\logs\setup" > nul 2>&1

:: Ensure Python uses only the venv packages
SET PYTHONNOUSERSITE=1
SET PYTHONPATH=

:: Deactivate the virtual environment to prevent error
call .\venv\Scripts\deactivate.bat

:: Activate the virtual environment
call .\venv\Scripts\activate.bat

REM first make sure we have setuptools available in the venv    
.\venv\Scripts\python.exe -m pip install --require-virtualenv --no-input -q -q setuptools

REM Check if the batch was started via double-click
IF /i "%comspec% /c %~0 " equ "%cmdcmdline:"=%" (
    REM echo This script was started by double clicking.
    cmd /k .\venv\Scripts\python.exe .\setup\setup_windows.py
) ELSE (
    REM echo This script was started from a command prompt.
    .\venv\Scripts\python.exe .\setup\setup_windows.py %*
)

:: Deactivate the virtual environment
call .\venv\Scripts\deactivate.bat 