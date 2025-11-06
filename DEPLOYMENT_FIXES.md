# Deployment Fixes Applied - 2025-11-06

## Issues Fixed

### 1. ✅ Database Migration Error (CRITICAL)
**Problem:** `NOT NULL constraint failed: request_logs.api_key_id`
- Old database had orphaned request logs without api_key_id
- Caused 500 errors on UPDATE operations

**Solution:**
- Added automatic cleanup in `main.py` startup
- Deletes orphaned request logs on every startup
- File: `api/app/main.py`

### 2. ✅ Model Loading Error (HIGH)
**Problem:** `ERROR loading model: [Errno 21] Is a directory: '/app/best.pt'`
- Docker volume mount created directory instead of file
- Model couldn't load at startup

**Solution:**
- Removed `best.pt` volume mount from `docker-compose.yml`
- Changed to upload-based model management
- Models now uploaded via admin dashboard to `/app/models` directory
- Files: `docker-compose.yml`, `Dockerfile`, `api/app/config.py`

### 3. ✅ Auto-Create Admin User (MEDIUM)
**Problem:** Repetitive startup message about admin creation
- Admin creation message appeared on every restart

**Solution:**
- Improved logging to show "Admin user exists" when already created
- Better startup messages with checkmarks
- File: `api/app/main.py`

### 4. ✅ 500 Error on /api/v1/detect (HIGH)
**Problem:** Detection endpoint returning 500 errors
- Caused by model loading failure (issue #2)

**Solution:**
- Fixed by resolving model loading issue
- Added better error messages in detector
- Added directory check for mounted paths
- File: `api/app/detector.py`

## Changes Summary

### Modified Files
1. `api/app/main.py` - Database cleanup + improved logging
2. `docker-compose.yml` - Removed problematic volume mount
3. `Dockerfile` - Removed hardcoded MODEL_PATH env var
4. `api/app/config.py` - Updated default model path
5. `api/app/detector.py` - Better error messages + directory check
6. `README.md` - Updated deployment instructions

### Key Changes

**Before:**
```yaml
volumes:
  - ./best.pt:/app/best.pt:ro  # ❌ Creates directory if not exists
```

**After:**
```yaml
volumes:
  - ./models:/app/models        # ✅ Upload models via dashboard
  - ./database:/app/database
```

## Deployment Instructions

### Fresh Deployment

1. **Pull latest changes:**
```bash
cd /path/to/captcha-solver-yolo-arm
git pull
```

2. **Stop existing containers:**
```bash
docker-compose down
```

3. **Backup database (optional):**
```bash
cp database/app.db database/app.db.backup
```

4. **Rebuild and start:**
```bash
docker-compose up -d --build
```

5. **Check logs:**
```bash
docker-compose logs -f captcha-api
```

Expected output:
```
✓ Database migration: Cleaned X orphaned request logs
✓ Admin user exists: admin
✓ Model loaded successfully from /app/models/your_model.pt
```

6. **Upload model (first time only):**
- Go to http://your-server:3000
- Login with admin credentials from `.env`
- Navigate to **Models** tab
- Upload your `.pt` model file
- Click **Activate** on the uploaded model

### Existing Deployment (Migration)

If you already have a running deployment:

1. **Backup current state:**
```bash
docker-compose down
cp database/app.db database/app.db.backup
cp best.pt models/best.pt  # Move existing model to models folder
```

2. **Apply updates:**
```bash
git pull
docker-compose up -d --build
```

3. **Upload model via dashboard:**
- The old `best.pt` file won't be used anymore
- Upload your model file through the admin dashboard
- System will automatically use the uploaded model

## Verification Checklist

After deployment, verify:

- [ ] Container starts without errors
- [ ] No "Is a directory" errors in logs
- [ ] Admin login works at http://your-server:3000
- [ ] API health check: `curl http://your-server:8000/`
- [ ] Models tab loads in dashboard
- [ ] Can upload and activate model
- [ ] Detection endpoint works with valid API key

## Troubleshooting

### Container keeps restarting
```bash
docker-compose logs captcha-api
```
Check for:
- Database permission errors
- Port conflicts (8000, 3000)
- Resource limits in `.env`

### Model upload fails
- Check disk space: `df -h`
- Check models directory permissions: `ls -la models/`
- Check container logs for upload errors

### Detection returns 500 error
- Ensure a model is uploaded and activated
- Check API key is valid
- Review container logs: `docker-compose logs -f`

### Database errors persist
If orphaned records still cause issues:
```bash
docker-compose down
rm database/app.db  # ⚠️ This deletes all data!
docker-compose up -d
# Re-create API keys and upload model
```

## Rollback Plan

If issues occur:

1. **Stop containers:**
```bash
docker-compose down
```

2. **Restore database:**
```bash
cp database/app.db.backup database/app.db
```

3. **Revert code:**
```bash
git checkout 8a84f93  # Previous working commit
```

4. **Restart:**
```bash
docker-compose up -d
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review README.md for detailed documentation
- Check GitHub issues for similar problems
