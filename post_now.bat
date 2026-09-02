@echo off
chcp 65001 > nul
echo ======================================================
echo    PUBLIKOWANIE 1 SWIEZEGO POSTA NA X
echo ======================================================
cd /d "%~dp0"
python agent.py --post-now
pause
