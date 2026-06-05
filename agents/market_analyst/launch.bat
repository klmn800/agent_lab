@echo off
REM Interactive Market Analyst launch (no prompt file — for ad-hoc sessions)
REM For scheduled research/Saturday/Sunday sessions, use the scheduled_tasks\start_market_analyst_*.bat files.

cd /d E:\options_scanner\agents\market_analyst
echo ================================================
echo  Market Analyst - Interactive
echo ================================================
echo.
claude --permission-mode auto
