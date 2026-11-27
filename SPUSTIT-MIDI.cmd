@echo off
cd /d "%~dp0"
set PYTHONDONTWRITEBYTECODE=1
if not exist ".venv\Scripts\python.exe" goto prepare
".venv\Scripts\python.exe" -B -X utf8 main.py %*
if errorlevel 1 pause
exit /b
:prepare
echo Najprv spustite PRIPRAVIT-MIDI.cmd na pripravu Python prostredia.
pause
