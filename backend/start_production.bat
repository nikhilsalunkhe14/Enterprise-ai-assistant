@echo off
REM Production deployment script for Windows

echo 🚀 Starting AI IT Project Delivery Assistant in Production Mode

REM Set production environment
set PYTHONPATH=%PYTHONPATH%;%CD%
set ENVIRONMENT=production

REM Start with multiple workers for concurrency
REM Each worker handles requests independently
REM 4 workers = 4x concurrency capacity
uvicorn main:app ^
    --workers 4 ^
    --host 0.0.0.0 ^
    --port 8000 ^
    --access-log ^
    --log-level info ^
    --timeout-keep-alive 120 ^
    --timeout-graceful-shutdown 30

echo ✅ Production server started with 4 workers
echo 📊 Concurrency capacity: 4x
echo 🎯 Target: Handle 100+ concurrent requests
pause
