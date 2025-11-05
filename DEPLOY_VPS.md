# Deployment Guide untuk ARM Ampere VPS

## Quick Deploy

### 1. Transfer Files ke VPS
```bash
# Dari local machine
scp -r captcha-solver-yolo-arm/ user@your-vps-ip:~/

# Atau gunakan git
ssh user@your-vps-ip
git clone <your-repo>
cd captcha-solver-yolo-arm
```

### 2. Pre-deployment Check
```bash
# Check architecture (should show aarch64)
uname -m

# Check available resources
free -h
nproc

# Verify Docker installed
docker --version
docker-compose --version
```

### 3. Adjust Configuration
```bash
# Edit .env based on your VPS specs
nano .env

# Example untuk 4-core, 8GB RAM VPS:
CPU_LIMIT=3.0
CPU_RESERVE=1.0
MEMORY_LIMIT=4G
MEMORY_RESERVE=2G
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
```

### 4. Create Directories
```bash
mkdir -p models database temp_results
chmod 755 models database temp_results
```

### 5. Verify Model File
```bash
# Ensure best.pt exists
ls -lh best.pt

# If not, upload it
scp best.pt user@your-vps-ip:~/captcha-solver-yolo-arm/
```

### 6. Build & Deploy
```bash
# Build images (first time: ~5-10 minutes)
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### 7. Verify Deployment
```bash
# Check logs
docker-compose logs -f

# Test API
curl http://localhost:8000/

# Test dashboard
curl http://localhost:3000/

# Run monitoring script
chmod +x monitor.sh
./monitor.sh
```

### 8. Access Dashboard
- Dashboard: http://your-vps-ip:3000
- API: http://your-vps-ip:8000
- Login: `admin` / `admin123`

⚠️ **IMPORTANT**: Change admin password immediately!

---

## Firewall Configuration

### UFW (Ubuntu)
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow dashboard
sudo ufw allow 3000/tcp

# Allow API (optional, if public)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### Firewalld (CentOS/RHEL)
```bash
# Allow services
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## Performance Tuning

### Check Current Performance
```bash
# Monitor while running
docker stats

# Check threads
echo "OMP threads: $OMP_NUM_THREADS"
echo "BLAS threads: $OPENBLAS_NUM_THREADS"
```

### Optimize for Your VPS
Edit `.env` based on test results:

**2-core VPS (4GB RAM)**:
```env
CPU_LIMIT=1.5
CPU_RESERVE=0.5
MEMORY_LIMIT=2G
MEMORY_RESERVE=1G
OMP_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2
```

**4-core VPS (8GB RAM)**:
```env
CPU_LIMIT=3.0
CPU_RESERVE=1.0
MEMORY_LIMIT=4G
MEMORY_RESERVE=2G
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
```

**8-core VPS (16GB RAM)**:
```env
CPU_LIMIT=6.0
CPU_RESERVE=2.0
MEMORY_LIMIT=6G
MEMORY_RESERVE=3G
OMP_NUM_THREADS=6
OPENBLAS_NUM_THREADS=6
```

After changing `.env`:
```bash
docker-compose down
docker-compose up -d
```

---

## Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild
docker-compose build

# Restart
docker-compose down
docker-compose up -d
```

### Backup Database
```bash
# Create backup
docker cp captcha-solver-api:/app/database/app.db ./backup-$(date +%Y%m%d).db

# Schedule automatic backup (crontab)
0 2 * * * docker cp captcha-solver-api:/app/database/app.db ~/backups/db-$(date +\%Y\%m\%d).db
```

### Clean Temp Files
```bash
# Manual cleanup
find temp_results/ -mtime +7 -delete

# Automatic cleanup (crontab - daily at 3 AM)
0 3 * * * find ~/captcha-solver-yolo-arm/temp_results/ -mtime +7 -delete
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs -f captcha-api

# Last 100 lines
docker-compose logs --tail=100
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs captcha-api

# Check if port already used
sudo netstat -tulpn | grep :8000

# Force rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Reduce limits in .env
MEMORY_LIMIT=1.5G
MEMORY_RESERVE=768M

# Restart
docker-compose down
docker-compose up -d
```

### Slow Performance
```bash
# Check CPU usage
top
docker stats

# Increase threads (if you have more cores)
# Edit .env
OMP_NUM_THREADS=6
OPENBLAS_NUM_THREADS=6

# Restart
docker-compose restart captcha-api
```

### Network Issues
```bash
# Check network
docker network ls
docker network inspect captcha-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Setup firewall (UFW/firewalld)
- [ ] Use HTTPS (setup reverse proxy)
- [ ] Regular database backups
- [ ] Monitor disk space
- [ ] Set API key expiration
- [ ] Limit API key daily requests
- [ ] Keep Docker updated
- [ ] Monitor logs for suspicious activity

---

## Monitoring Script Usage

```bash
# Make executable
chmod +x monitor.sh

# Run manually
./monitor.sh

# Schedule monitoring (every hour)
crontab -e
0 * * * * /path/to/captcha-solver-yolo-arm/monitor.sh >> /var/log/captcha-monitor.log 2>&1
```

---

## Need Help?

Check logs and run monitoring script for diagnostics:
```bash
./monitor.sh
docker-compose logs --tail=50
```
