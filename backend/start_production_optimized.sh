#!/bin/bash
# Production deployment script - Single Worker with Threading

echo "🚀 Starting AI IT Project Delivery Assistant in Production Mode"
echo "📊 Using single worker with ThreadPool for concurrency"

# Set production environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT=production

# Start with single worker to avoid model loading conflicts
# ThreadPoolExecutor handles concurrency internally
uvicorn main:app \
    --workers 1 \
    --host 0.0.0.0 \
    --port 8001 \
    --access-log \
    --log-level info \
    --timeout-keep-alive 120 \
    --timeout-graceful-shutdown 30

echo "✅ Production server started with optimized threading"
echo "🎯 Concurrency handled by ThreadPoolExecutor (10 workers)"
echo "📈 Target: Handle 100+ concurrent requests efficiently"
