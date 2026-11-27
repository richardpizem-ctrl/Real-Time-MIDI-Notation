@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
where python >nul 2>nul
if errorlevel 1 goto py_launcher
python -m venv .venv
if errorlevel 1 goto error
goto install
:py_launcher
py -3 -m venv .venv
if errorlevel 1 goto error
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Priprava dokoncena. Spustite SPUSTIT-MIDI.cmd.
pause
exit /b 0
:error
echo Priprava zlyhala. Potrebny je Python 3.10 alebo novsi a pripojenie na internet.
pause
exit /b 1
