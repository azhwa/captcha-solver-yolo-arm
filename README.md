# YOLO Captcha Solver - ARM64 with Web Dashboard

Captcha detection API using YOLOv8 dengan Web Dashboard untuk management, optimized untuk ARM64 VPS.

## 🚀 Features

- ✅ YOLOv8 object detection
- ✅ Web Dashboard untuk API key & model management
- ✅ API Key dengan expiration & rate limiting
- ✅ Model upload & hot-swapping
- ✅ Request logging & statistics
- ✅ JWT authentication untuk admin

## 📋 Prerequisites

- Docker & Docker Compose
- ARM64 VPS (Oracle Cloud, AWS Graviton, etc)
- YOLOv8 model file `best.pt`

## 🔧 Quick Start

### 1. Clone & Setup
```bash
<<<<<<< HEAD
git clone <your-repo>
=======
# 1. Clone repository
git clone https://github.com/azhwa/captcha-solver-yolo-arm.git
>>>>>>> 46fdea3432a18d98ac4b79f954ea273c8e4a5f58
cd captcha-solver-yolo-arm

# Create directories
mkdir -p models database temp_results
```

### 2. Configure Environment
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env based on your needs
nano .env

# ⚠️ Change admin credentials (IMPORTANT for production!)
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
ADMIN_EMAIL=admin@yourserver.com

# For 4-core, 8GB RAM VPS:
CPU_LIMIT=3.0
MEMORY_LIMIT=4G
OMP_NUM_THREADS=4
```

### 3. Place Model
```bash
cp /path/to/your/model.pt ./best.pt
```

### 4. Build & Deploy
```bash
# Build (first time: ~5-10 minutes)
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose logs -f
```

### 5. Access Dashboard
- **Dashboard**: http://your-server:3000
- **API**: http://your-server:8000
- **Login**: Use credentials from `.env` (default: `admin` / `admin123`)

⚠️ **IMPORTANT**: Change admin credentials in `.env` before deployment!

### 6. Monitor System
```bash
chmod +x monitor.sh
./monitor.sh
```

## 🎯 Using Web Dashboard

### Create API Key
1. Login ke dashboard
2. Tab **API Keys** → **Add New Key**
3. Isi form:
   - **Name**: identifier (e.g., "production-key")
   - **Expiration**: 
     - Never Expire (lifetime)
     - Duration (X days)
     - Custom Date
   - **Daily Limit**: 0 = unlimited
4. Click **Create** → Copy API key

### Upload Model
1. Tab **Models** → **Upload Model**
2. Select `.pt` file
3. Click **Activate** untuk menggunakan model

### Test Detection
1. Tab **Test**
2. Select API key
3. Upload image
4. View hasil detection

## 📡 API Usage

### Detection Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/detect?include_visual=true" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@image.png"
```

**Response:**
```json
{
  "boxes": [
    {"xyxy": [100.5, 200.3, 300.8, 400.2], "confidence": 0.95, "class": 0}
  ],
  "visualization": "base64_encoded_png..."
}
```

### Parameters
- `include_visual` (bool): Return base64 visualization (default: true)
- `save_file` (bool): Save result to temp folder (default: false)

## 🔐 Admin API Endpoints

### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Returns: {"access_token": "...", "token_type": "bearer"}
```

### API Keys Management (Requires JWT)
```bash
TOKEN="your_jwt_token"

# List keys
curl "http://localhost:8000/admin/keys" \
  -H "Authorization: Bearer $TOKEN"

# Create key
curl -X POST "http://localhost:8000/admin/keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-key",
    "expiration_type": "duration",
    "duration_days": 90,
    "daily_limit": 1000
  }'

# Renew key
curl -X PATCH "http://localhost:8000/admin/keys/1/renew" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expiration_type": "duration", "duration_days": 30}'

# Delete key
curl -X DELETE "http://localhost:8000/admin/keys/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Model Management
```bash
# Upload model
curl -X POST "http://localhost:8000/admin/models/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@new_model.pt"

# Activate model
curl -X PATCH "http://localhost:8000/admin/models/1/activate" \
  -H "Authorization: Bearer $TOKEN"
```

### Statistics
```bash
# Dashboard stats
curl "http://localhost:8000/admin/stats/dashboard" \
  -H "Authorization: Bearer $TOKEN"

# Request logs
curl "http://localhost:8000/admin/stats/logs?limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

## 🗂️ Services

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI backend |
| Dashboard | 3000 | Web UI (Nginx) |

## 🔧 Configuration

### Environment Variables
All configuration can be done via `.env` file:

```bash
# Admin Credentials (⚠️ Change in production!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# Docker Resources (for Docker deployment)
CPU_LIMIT=2.0
MEMORY_LIMIT=2G
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
```

See `.env.example` for all available options.

### Docker Resources
Edit `docker-compose.yml` or use `.env`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### CPU Threads
Adjust based on VPS cores via `.env`:
```bash
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
```

## 📊 Project Structure

```
captcha-solver-yolo-arm/
├── api/app/
│   ├── routers/        # API endpoints
│   ├── crud/           # Database operations
│   ├── models/         # DB & Pydantic models
│   ├── auth.py         # JWT authentication
│   ├── database.py     # SQLAlchemy setup
│   └── main.py         # FastAPI app
├── web/
│   ├── index.html      # Dashboard UI
│   └── app.js          # Frontend logic
├── models/             # Model files
├── database/           # SQLite database
├── temp_results/       # Detection outputs
└── docker-compose.yml
```

## 🖥️ Running Without Docker (Development)

For local development or testing without Docker:

### Prerequisites
- Python 3.9+
- pip

### Steps

**1. Install Dependencies**
```bash
pip install -r requirements.txt

# If bcrypt error occurs:
pip install bcrypt==4.0.1
```

**2. Setup Environment**
```bash
# Copy and edit .env (optional - uses defaults if not present)
cp .env.example .env
nano .env
```

**3. Ensure Model File Exists**
```bash
# Make sure best.pt is in root folder
ls best.pt
```

**4. Run Backend API**
```bash
python api/main.py
# API will run at http://localhost:8000
```

**5. Run Web UI (separate terminal)**
```bash
cd web
python -m http.server 3000
# Dashboard at http://localhost:3000
```

**6. Login**
- Open: `http://localhost:3000`
- Login with credentials from `.env` (default: admin/admin123)

### Notes
- Database auto-creates at `database/app.db`
- Admin user auto-creates on first run
- Web UI must use HTTP server (not `file://` protocol for CORS)

## 🛠️ Monitoring

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f captcha-api
```

### Check Status
```bash
docker-compose ps
docker stats captcha-solver-api-arm
```

### Database Access
```bash
docker exec -it captcha-solver-api-arm sqlite3 /app/database/app.db
```

## 🚀 Production Tips

1. **Change admin credentials** in `.env` before deployment:
   ```bash
   ADMIN_USERNAME=your_secure_username
   ADMIN_PASSWORD=your_strong_password_here
   ADMIN_EMAIL=admin@yourdomain.com
   ```
2. **Use HTTPS** (reverse proxy dengan Nginx/Caddy)
3. **Backup database** secara berkala:
   ```bash
   docker cp captcha-solver-api-arm:/app/database/app.db ./backup/
   ```
4. **Set expiration** untuk semua production API keys
5. **Monitor disk space** (models, database, logs)
6. **Keep `.env` secure** - never commit to git (already in .gitignore)

## 🐛 Troubleshooting

**API key tidak work?**
- Check status Active di dashboard
- Verify belum expired
- Check daily limit belum exceeded

**Model upload gagal?**
- Ensure file format `.pt`
- Check disk space
- Check logs: `docker-compose logs captcha-api`

**Dashboard tidak load?**
- Check containers: `docker ps`
- Verify API: `curl http://localhost:8000`
- Check browser console

## 📄 API Documentation

Swagger UI: http://localhost:8000/docs

## License

MIT License
