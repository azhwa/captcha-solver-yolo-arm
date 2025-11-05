#!/bin/bash
# Quick log checker for debugging

echo "======================================"
echo "Captcha Solver - Quick Diagnostics"
echo "======================================"
echo ""

# Check if containers are running
echo "1. Container Status:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep captcha

echo ""
echo "2. API Health Status:"
HEALTH=$(docker inspect captcha-solver-api --format='{{.State.Health.Status}}' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "✅ API is HEALTHY"
elif [ "$HEALTH" = "unhealthy" ]; then
    echo "❌ API is UNHEALTHY"
    echo ""
    echo "Last health check:"
    docker inspect captcha-solver-api --format='{{range .State.Health.Log}}{{.Output}}{{end}}' | tail -5
else
    echo "⚠️  API container not found or no healthcheck"
fi

echo ""
echo "3. API Logs (last 20 lines):"
echo "-----------------------------------"
docker logs --tail=20 captcha-solver-api 2>&1

echo ""
echo "4. Files Check:"
if [ -f "best.pt" ]; then
    SIZE=$(ls -lh best.pt | awk '{print $5}')
    echo "✅ best.pt exists ($SIZE)"
else
    echo "❌ best.pt NOT FOUND!"
fi

if [ -d "database" ]; then
    echo "✅ database/ directory exists"
else
    echo "❌ database/ directory NOT FOUND!"
fi

echo ""
echo "5. Quick Test:"
if curl -sf http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ API responding on port 8000"
else
    echo "❌ API not responding on port 8000"
fi

if curl -sf http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Dashboard responding on port 3000"
else
    echo "❌ Dashboard not responding on port 3000"
fi

echo ""
echo "======================================"
echo "For detailed logs run:"
echo "  docker logs -f captcha-solver-api"
echo "======================================"
