# Quick Fix - Error Unhealthy Container

## Most Common Issue: Model File Missing

**Run these commands on your VPS:**

```bash
# 1. Check if best.pt exists
ls -lh best.pt

# If file NOT found, that's the problem!
# You need to upload your YOLO model file as best.pt
```

---

## Solution 1: Check Logs First

```bash
# Stop and view logs
docker-compose down
docker-compose up

# Look for errors (especially about best.pt)
# Press Ctrl+C when done
```

---

## Solution 2: If Model File Missing

```bash
# Upload your YOLO model and rename it to best.pt
# Example:
scp your-model.pt user@vps:/path/to/project/best.pt

# Then restart
cd /www/dk_project/dk_app/captcha-solver/captcha-solver-yolo-arm
docker-compose down
docker-compose up -d
```

---

## Solution 3: Start Without Health Check (Quick Test)

Edit `docker-compose.yml`, find this section:

```yaml
web-dashboard:
  depends_on:
    captcha-api:
      condition: service_healthy  # ← Comment this line
```

Change to:

```yaml
web-dashboard:
  depends_on:
    - captcha-api  # ← Simple dependency, no health check
```

Then:

```bash
docker-compose down
docker-compose up -d

# Check logs
docker logs captcha-solver-api
```

---

## Solution 4: Increase Healthcheck Timeout

Already updated in docker-compose.yml, but if still failing:

```yaml
healthcheck:
  start_period: 180s  # Increase to 3 minutes
```

---

## Check Status

```bash
# Run diagnostic script
chmod +x check-logs.sh
./check-logs.sh
```

---

## Manual Test API

```bash
# Wait 2 minutes after docker-compose up -d
sleep 120

# Test API directly
curl http://localhost:8000/

# If you see JSON response: {"message":"Welcome to Captcha Solver API","version":"2.0"}
# Then API is working!
```

---

## Most Likely Fix

**90% chance the issue is missing `best.pt` file.**

1. Check: `ls -lh best.pt`
2. If missing: Upload your YOLO model
3. Restart: `docker-compose restart captcha-api`

Done!
