@echo off
cd /d "%~dp0"
echo Obnova sa tyka iba chybajuceho alebo neplatneho config.json.
echo Poskodeny subor sa pred nahradenim zalohuje. Kod ani nahravky sa nemenia.
call SPUSTIT-MIDI.cmd --repair-settings
pause
