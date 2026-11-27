@echo off
cd /d "%~dp0"
start "" "C:\Program Files (x86)\Steam\steamapps\common\VoiceAttack\VoiceAttack.exe"
timeout /t 3 /nobreak >nul
py "%~dp0IA_Elite.py"
