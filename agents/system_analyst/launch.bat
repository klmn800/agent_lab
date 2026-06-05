@echo off
cd /d E:\options_scanner\agents\system_analyst
echo ================================================
echo  System Analyst — Session Launch
echo ================================================
echo.
echo Starting Claude Code with System Analyst prompt...
echo.
start "" cmd /k "cd /d E:\options_scanner\agents\system_analyst && claude --model claude-opus-4-7 --permission-mode auto @PROMPT.md"
