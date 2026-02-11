#!/bin/bash
# Production deployment script

echo "🚀 Starting AI IT Project Delivery Assistant in Production Mode"

# Set production environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT=production

# Start with multiple workers for concurrency
# Each worker handles requests independently
# 4 workers = 4x concurrency capacity
uvicorn main:app \
    --workers 4 \
    --host 0.0.0.0 \
    --port 8000 \
    --access-log \
    --log-level info \
    --timeout-keep-alive 120 \
    --timeout-graceful-shutdown 30

echo "✅ Production server started with 4 workers"
echo "📊 Concurrency capacity: 4x"
echo "🎯 Target: Handle 100+ concurrent requests"
