# YOLO Captcha Solver - ARM64

Captcha detection API using YOLOv8, optimized for ARM64 VPS (Oracle Cloud, AWS Graviton, etc).

## Prerequisites

- Docker & Docker Compose
- ARM64 VPS
- YOLOv8 model file `best.pt`

## Quick Start

```bash
# 1. Clone repository
git clone <your-repo>
cd captcha-solver-yolo-arm

# 2. Setup environment
cp .env.example .env
nano .env  # Edit API_KEYS

# 3. Run
docker-compose up -d
```

## Testing

### Health Check
```bash
curl -H "X-API-Key: yourkey1" http://localhost:8000/api/v1/health

```

### Detect Captcha
```bash
curl -X POST "http://localhost:8000/api/v1/detect?include_visual=true&save_file=false" \
  -H "X-API-Key: yourkey1" \
  -F "file=@/path/to/image.png"
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
  "visualization": "base64_encoded_png..."
}
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/detect` | Detect objects in image | API Key |
| GET | `/api/v1/health` | Health check | API Key |

### Parameters `/detect`
- `file`: Image file (multipart/form-data)
- `include_visual`: Return base64 visualization (default: true)
- `save_file`: Save result to temp folder (default: false)

## Configuration

Edit `.env` file:

```env
# API Keys (JSON array)
API_KEYS=["key1", "key2", "key3"]

# ARM64 CPU threads (adjust based on VPS cores)
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
```

**Resource Limits** (edit in `docker-compose.yml`):
- CPU: 1-2 cores
- Memory: 1-2 GB

## Logs

```bash
# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## Notes

- YOLOv8 model must exist in root folder as `best.pt`
- Default port: `8000`
- Visualizations saved to `./temp_results/` (if `save_file=true`)
- Health check: `http://localhost:8000/api/v1/health`
