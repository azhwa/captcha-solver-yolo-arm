# Troubleshooting Guide

## Error: "dependency failed to start: container captcha-solver-api is unhealthy"

### Quick Diagnosis

```bash
# 1. Check container status
docker ps -a

# 2. View API logs
docker logs captcha-solver-api

# 3. Check health status
docker inspect captcha-solver-api --format='{{json .State.Health}}'
```

---

## Common Issues & Solutions

### Issue 1: Model File `best.pt` Not Found ⚠️

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/app/best.pt'
```

**Solution:**
```bash
# Check if best.pt exists
ls -lh best.pt

# If missing, place your YOLO model
cp /path/to/your/yolo-model.pt best.pt

# Restart
docker-compose restart captcha-api
```

---

### Issue 2: Database Permission Error

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/app/database/app.db'
```

**Solution:**
```bash
# Fix permissions
sudo chmod -R 755 database/
sudo chown -R $(whoami):$(whoami) database/

# Restart
docker-compose restart captcha-api
```

---

### Issue 3: Python Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Solution:**
```bash
# Rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Issue 4: Healthcheck Timeout (Model Loading Too Slow)

**Symptom:**
- Container starts but marked unhealthy
- Logs show: `INFO: Uvicorn running on http://0.0.0.0:8000`
- Container restarts repeatedly

**Solution:**
Already fixed in `docker-compose.yml` (start_period: 120s). If still fails:

```bash
# Increase timeout manually
# Edit docker-compose.yml:
# start_period: 180s  # 3 minutes
```

---

### Issue 5: Out of Memory

**Symptom:**
```
Killed
# Or container exits with code 137
```

**Solution:**
```bash
# Edit .env file
nano .env

# Reduce memory limits
MEMORY_LIMIT=1.5G
MEMORY_RESERVE=768M

# Restart
docker-compose down
docker-compose up -d
```

---

## Debugging Commands

### View Logs in Real-time
```bash
# All containers
docker-compose logs -f

# API only
docker logs -f captcha-solver-api

# Dashboard only
docker logs -f captcha-solver-dashboard
```

### Check Container Health
```bash
# Health status
docker inspect captcha-solver-api --format='{{.State.Health.Status}}'

# Last health check output
docker inspect captcha-solver-api --format='{{json .State.Health}}' | jq
```

### Test API Manually
```bash
# Enter container
docker exec -it captcha-solver-api bash

# Inside container:
curl http://localhost:8000/
ps aux | grep uvicorn
ls -lh /app/best.pt
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
df -h
du -sh database/ models/ temp_results/
```

---

## Step-by-Step Debugging

### 1. Start in Foreground (See All Logs)
```bash
# Stop containers
docker-compose down

# Start in foreground
docker-compose up

# Watch for errors
# Press Ctrl+C to stop
```

### 2. Start API Only (Isolate Issue)
```bash
# Start only API
docker-compose up -d captcha-api

# Wait 2 minutes (for model loading)
sleep 120

# Check status
docker ps

# Check logs
docker logs captcha-solver-api

# Test endpoint
curl http://localhost:8000/
```

### 3. Verify All Files
```bash
# Check model file
ls -lh best.pt
file best.pt  # Should show: data

# Check directories
ls -ld database/ models/ temp_results/

# Check permissions
ls -la | grep -E "database|models|temp_results"
```

---

## Quick Fixes

### Fix 1: Restart Everything
```bash
docker-compose down
docker-compose up -d
docker logs -f captcha-solver-api
```

### Fix 2: Rebuild from Scratch
```bash
docker-compose down -v  # ⚠️ This removes volumes!
docker-compose build --no-cache
docker-compose up -d
```

### Fix 3: Start Without Health Check (Temporary)
Edit `docker-compose.yml`:

```yaml
web-dashboard:
  depends_on:
    - captcha-api  # Remove: condition: service_healthy
```

Then:
```bash
docker-compose down
docker-compose up -d
```

---

## Advanced Debugging

### Check Network
```bash
docker network inspect captcha-network
docker exec captcha-solver-api ping captcha-solver-dashboard
```

### Check Environment Variables
```bash
docker exec captcha-solver-api env | grep -E "MODEL|THREAD"
```

### Check Python Environment
```bash
docker exec captcha-solver-api /app/venv/bin/pip list
docker exec captcha-solver-api python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

---

## Still Not Working?

### Collect Debug Info
```bash
# Create debug report
cat > debug-report.txt << EOF
=== System Info ===
$(uname -a)
$(docker --version)
$(docker-compose --version)

=== Container Status ===
$(docker ps -a)

=== API Logs (last 50 lines) ===
$(docker logs --tail=50 captcha-solver-api 2>&1)

=== Health Check ===
$(docker inspect captcha-solver-api --format='{{json .State.Health}}')

=== Files ===
$(ls -lh best.pt 2>&1)
$(ls -ld database/ models/ temp_results/ 2>&1)

=== Resource Usage ===
$(free -h)
$(df -h)
EOF

cat debug-report.txt
```

Share `debug-report.txt` untuk bantuan lebih lanjut.

---

## Prevention Tips

1. **Always verify `best.pt` exists** before deploy
2. **Check logs immediately** after `docker-compose up`
3. **Monitor resources** dengan `docker stats`
4. **Use `.env` file** untuk easy configuration
5. **Backup database** regularly: `cp database/app.db backup/`

---

## Common Error Messages

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `best.pt not found` | Model file missing | Place model file |
| `Permission denied` | Directory permissions | `chmod 755` |
| `Module not found` | Build failed | Rebuild with `--no-cache` |
| `Killed` or `137` | Out of memory | Reduce MEMORY_LIMIT |
| `Connection refused` | API not started | Wait longer or check logs |
| `unhealthy` | Healthcheck failed | Check logs, increase timeout |

---

## Emergency Commands

### Stop Everything
```bash
docker-compose down
```

### Remove Everything (Fresh Start)
```bash
# ⚠️ WARNING: This removes all data!
docker-compose down -v
rm -rf database/*
docker-compose up -d
```

### Quick Health Check
```bash
curl http://localhost:8000/ && echo "API OK" || echo "API FAILED"
curl http://localhost:3000/ && echo "Dashboard OK" || echo "Dashboard FAILED"
```
