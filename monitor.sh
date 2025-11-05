#!/bin/bash
# Monitoring script for Captcha Solver on ARM VPS

echo "================================================"
echo "Captcha Solver ARM - System Monitor"
echo "================================================"

echo -e "\n=== Docker Containers Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== Resource Usage ==="
docker stats --no-stream captcha-solver-api captcha-solver-dashboard

echo -e "\n=== Disk Usage ==="
echo "Models directory:"
du -sh models/ 2>/dev/null || echo "  No models uploaded yet"
echo "Database:"
du -sh database/ 2>/dev/null || echo "  Database not created yet"
echo "Temp results:"
du -sh temp_results/ 2>/dev/null || echo "  No temp files"

echo -e "\n=== API Health Check ==="
API_HEALTH=$(curl -s http://localhost:8000/ | grep -o '"message":"[^"]*"' || echo "API not responding")
echo "$API_HEALTH"

echo -e "\n=== Dashboard Check ==="
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
if [ "$DASHBOARD_STATUS" = "200" ]; then
    echo "Dashboard: OK (HTTP 200)"
else
    echo "Dashboard: ERROR (HTTP $DASHBOARD_STATUS)"
fi

echo -e "\n=== Recent Logs (last 20 lines) ==="
docker-compose logs --tail=20

echo -e "\n=== System Info ==="
echo "CPU Cores: $(nproc)"
echo "Memory:"
free -h | grep Mem

echo -e "\n================================================"
