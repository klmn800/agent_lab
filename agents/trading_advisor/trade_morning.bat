@echo off
cd /d E:\options_scanner\agents\trading_advisor
set TA_SESSION_TYPE=morning
echo.
echo   Trading Advisor - Morning Brief
echo   %date%
echo.
claude --permission-mode auto @morning_brief_prompt.md
