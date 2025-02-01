@echo off
REM Define the relative path to the virtual environment's activation script
set VENV_ACTIVATE=%~dp0venv\Scripts\activate.bat

REM Define the relative path to the Python script
set PYTHON_SCRIPT=%~dp0main_startup.py

REM Activate the virtual environment
call "%VENV_ACTIVATE%"

REM Run the Python script
python "%PYTHON_SCRIPT%"

REM Pause to keep the command prompt open
pause