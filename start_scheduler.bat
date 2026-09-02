@echo off
chcp 65001 > nul
echo ======================================================
echo    URUCHAMIANIE AGENTA X (10 POSTOW DZIENNIE)
echo ======================================================
cd /d "%~dp0"
python agent.py --schedule
pause
