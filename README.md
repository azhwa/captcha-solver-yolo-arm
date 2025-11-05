# Captcha Solver - YOLOv8 API with Web Dashboard

FastAPI-based captcha detection service using YOLOv8 with a complete web dashboard for API key management, model deployment, and monitoring.

## Features

- 🤖 YOLOv8 object detection for captcha solving
- 🎛️ Web Dashboard for management (API keys, models, stats)
- 🔐 JWT authentication with configurable admin credentials
- 📊 Request logging and statistics
- ⚡ Hot-swappable models
- 🐳 Docker support with ARM64 optimization

## Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- YOLOv8 model file (`.pt`)

### Setup

**1. Clone and Configure**
```bash
git clone <your-repo>
cd captcha-solver-yolo-arm

# Copy environment template
cp .env.example .env
```

**2. Configure Admin Credentials**

Edit `.env` and change default credentials:
```bash
# ⚠️ CHANGE THESE IN PRODUCTION!
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_secure_password
ADMIN_EMAIL=admin@yourdomain.com

# Resource limits (adjust based on VPS)
CPU_LIMIT=2.0
MEMORY_LIMIT=2G
OMP_NUM_THREADS=4
```

**3. Place Model**
```bash
# Copy your trained model to root
cp /path/to/your/model.pt ./best.pt
```

**4. Deploy**
```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f
```

**5. Access**
- **Dashboard**: http://your-server:3000
- **API**: http://your-server:8000
- **API Docs**: http://your-server:8000/docs

Login with credentials from `.env`.

## Manual Run (Without Docker)

For local development:

**1. Install Dependencies**
```bash
pip install -r requirements.txt

# If bcrypt error:
pip install bcrypt==4.0.1
```

**2. Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

**3. Run Backend**
```bash
python api/main.py
# Runs at http://localhost:8000
```

**4. Run Web UI (separate terminal)**
```bash
cd web
python -m http.server 3000
# Dashboard at http://localhost:3000
```

## Using the Dashboard

### 1. Login
- Navigate to dashboard URL
- Use admin credentials from `.env`

### 2. Create API Key
- Go to **API Keys** tab
- Click **Add New Key**
- Set name, expiration, and daily limit
- Copy the generated API key

### 3. Upload Model (Optional)
- Go to **Models** tab
- Upload new `.pt` file
- Activate to use

### 4. Test Detection
- Go to **Test** tab
- Select API key
- Upload captcha image
- View detection results

## API Usage

### Detection Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/detect?include_visual=true" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@captcha.png"
```

**Response:**
```json
{
  "boxes": [
    {
      "xyxy": [100.5, 200.3, 300.8, 400.2],
      "confidence": 0.95,
      "class": 0
    }
  ],
  "visualization": "base64_encoded_image..."
}
```

**Parameters:**
- `include_visual` (bool): Return annotated image as base64 (default: true)
- `save_file` (bool): Save result to temp folder (default: false)

### Admin API

**Login:**
```bash
curl -X POST "http://localhost:8000/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Create API Key:**
```bash
curl -X POST "http://localhost:8000/admin/keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-key",
    "expiration_type": "duration",
    "duration_days": 90,
    "daily_limit": 1000
  }'
```

**View Statistics:**
```bash
curl "http://localhost:8000/admin/stats/dashboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Full API documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

All settings in `.env`:

```bash
# Admin Credentials (required)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# Docker Resources (for Docker deployment)
CPU_LIMIT=2.0              # CPU cores limit
CPU_RESERVE=1.0            # CPU cores reservation
MEMORY_LIMIT=2G            # Memory limit
MEMORY_RESERVE=1G          # Memory reservation

# Performance Tuning
OMP_NUM_THREADS=4          # OpenMP threads (set to CPU cores)
OPENBLAS_NUM_THREADS=4     # OpenBLAS threads
```

See `.env.example` for all options.

### Resource Recommendations

| VPS Specs | CPU_LIMIT | MEMORY_LIMIT | OMP_NUM_THREADS |
|-----------|-----------|--------------|-----------------|
| 2 cores, 4GB | 1.5 | 2G | 2 |
| 4 cores, 8GB | 3.0 | 4G | 4 |
| 8 cores, 16GB | 6.0 | 8G | 8 |

## Project Structure

```
captcha-solver-yolo-arm/
├── api/app/
│   ├── routers/          # API endpoints
│   ├── crud/             # Database operations
│   ├── models/           # Database & Pydantic models
│   ├── auth.py           # JWT authentication
│   ├── database.py       # SQLAlchemy setup
│   └── main.py           # FastAPI application
├── web/
│   ├── index.html        # Dashboard UI
│   └── app.js            # Frontend logic
├── models/               # Uploaded models storage
├── database/             # SQLite database
├── temp_results/         # Detection output files
├── .env                  # Environment configuration
└── docker-compose.yml    # Docker orchestration
```

## Production Deployment

### Security Checklist

1. **Change Admin Credentials** in `.env`:
   ```bash
   ADMIN_USERNAME=secure_username
   ADMIN_PASSWORD=VeryStr0ng!P@ssw0rd
   ADMIN_EMAIL=admin@yourdomain.com
   ```

2. **Use HTTPS** with reverse proxy (Nginx/Caddy)

3. **Secure `.env`**: Never commit to git (already in `.gitignore`)

4. **Set API Key Expiration**: Use duration-based keys, not lifetime

5. **Monitor Resources**: Use `docker stats` or monitoring tools

### Backup

**Database:**
```bash
# Backup
docker cp captcha-solver-api-arm:/app/database/app.db ./backup/

# Restore
docker cp ./backup/app.db captcha-solver-api-arm:/app/database/
```

**Models:**
```bash
docker cp captcha-solver-api-arm:/app/models ./backup/
```

### Monitoring

**View Logs:**
```bash
docker-compose logs -f
docker-compose logs -f captcha-api
```

**Check Status:**
```bash
docker-compose ps
docker stats captcha-solver-api-arm
```

**Monitor Script:**
```bash
chmod +x monitor.sh
./monitor.sh
```

## Troubleshooting

**Container fails to start:**
- Check logs: `docker-compose logs captcha-api`
- Verify `best.pt` exists in root folder
- Check resource limits in `.env`

**Login fails:**
- Verify credentials in `.env` match your input
- Check database created: `ls database/app.db`
- Restart containers: `docker-compose restart`

**API key not working:**
- Verify key is Active in dashboard
- Check expiration date
- Verify daily limit not exceeded

**Model upload fails:**
- Ensure file is `.pt` format
- Check disk space: `df -h`
- Verify container has write access

**Web UI won't connect:**
- Ensure backend is running (check port 8000)
- For manual run: Use HTTP server, not `file://`
- Check CORS settings (default allows all origins)

## License

MIT License

---

For issues or questions, please open a GitHub issue.
