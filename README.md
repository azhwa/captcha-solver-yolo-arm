# Captcha Solver API - ARM64 Version

FastAPI-based REST API untuk deteksi captcha menggunakan YOLOv8, **optimized untuk ARM64 processors**.

## 🎯 ARM64 Compatible Platforms

✅ **Cloud VPS ARM:**
- AWS Graviton (EC2 t4g, a1 instances)
- Oracle Cloud ARM (Ampere A1)
- Azure ARM-based VMs
- Google Cloud Tau T2A

✅ **Single Board Computers:**
- Raspberry Pi 4 (4GB+ RAM recommended)
- Raspberry Pi 5
- NVIDIA Jetson Nano/Xavier
- Rock Pi 4

✅ **Development:**
- Apple Silicon (M1, M2, M3 Mac)
- ARM-based Windows laptops

## 🚀 Quick Start

### Requirements
- ARM64 processor
- Docker & Docker Compose
- 2GB+ RAM (4GB recommended)
- Port 8000 available

### Deploy

```bash
# Clone atau upload project ke ARM64 machine
cd captcha-solver-yolo-arm

# Build & Start
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Test
curl http://localhost:8000/api/v1/health
```

## 📡 API Endpoints

Same as x86 version:

### Health Check
```
GET /api/v1/health
```

### Detect Captcha
```
POST /api/v1/detect
Headers: X-API-Key: your-api-key
Form Data:
  - file: image file
  - include_visual: boolean (default: true)
  - save_file: boolean (default: false)
```

### Example
```bash
curl -X POST http://localhost:8000/api/v1/detect \
  -H "X-API-Key: your-api-key" \
  -F "file=@captcha.png" \
  -F "save_file=true"
```

## ⚡ ARM64 Optimizations

This version includes:
- ✅ OpenBLAS for faster matrix operations
- ✅ Multi-threading optimization (OMP_NUM_THREADS=4)
- ✅ Memory-efficient dependencies
- ✅ Platform-specific base image
- ✅ Reduced resource limits

## 🔧 Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  - API_KEYS=["your-secure-key"]
  
deploy:
  resources:
    limits:
      cpus: '2.0'    # Adjust based on your CPU
      memory: 2G     # Adjust based on your RAM
```

## 📊 Performance Notes

**Expected performance on ARM64:**
- Build time: 10-15 minutes (first time)
- Inference time: 50-150ms per image (depends on CPU)
- Memory usage: ~1.5GB

**Recommended specs:**
- 2+ CPU cores
- 2GB+ RAM
- 10GB+ storage

## 🐛 Troubleshooting

### Build fails on ARM64
```bash
# Clean and rebuild
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
```

### Out of memory
```bash
# Reduce resource limits in docker-compose.yml
limits:
  memory: 1G
```

### Slow inference
```bash
# Increase thread count
environment:
  - OMP_NUM_THREADS=8  # Match your CPU cores
```

## 📚 Documentation

- Full deployment guide: `ARM64_GUIDE.txt`
- API docs: `http://localhost:8000/docs`

## 🔐 Security

Change API_KEYS in docker-compose.yml before deploying!

## 📝 License

Private Project
