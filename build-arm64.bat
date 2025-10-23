@echo off
REM Build script for ARM64 Docker image (Windows)
REM This builds for ARM64 platform using Docker BuildX

echo ================================================
echo   Captcha Solver API - ARM64 Build Script
echo ================================================
echo.

REM Check Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [INFO] Docker version:
docker --version
echo.

echo [1/5] Checking Docker BuildX...
docker buildx version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker BuildX not available!
    echo Please enable BuildX in Docker Desktop settings
    pause
    exit /b 1
)
docker buildx version
echo.

echo [2/5] Creating builder instance for cross-platform build...
docker buildx create --name arm64-builder --use --platform linux/arm64 2>nul || docker buildx use arm64-builder
echo.

echo [3/5] Building Docker image for ARM64...
echo This may take 10-15 minutes on first build...
echo.
docker buildx build ^
    --platform linux/arm64 ^
    --tag captcha-solver-api:arm64 ^
    --tag captcha-solver-api:latest-arm64 ^
    --load ^
    .

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/5] Checking image...
docker images | findstr captcha-solver-api

echo.
echo [5/5] Build complete!
echo.
echo ================================================
echo   ARM64 Image Ready!
echo ================================================
echo.
echo Image: captcha-solver-api:arm64
echo.
echo NEXT STEPS:
echo.
echo [Option 1] Test locally (if you have ARM64 Docker/QEMU):
echo   docker run -d -p 8000:8000 ^
echo     -e API_KEYS='["your-key"]' ^
echo     captcha-solver-api:arm64
echo.
echo [Option 2] Export and upload to ARM64 VPS:
echo   docker save captcha-solver-api:arm64 ^| gzip ^> captcha-api-arm64.tar.gz
echo   scp captcha-api-arm64.tar.gz user@vps-ip:~/
echo   # On VPS:
echo   docker load ^< captcha-api-arm64.tar.gz
echo.
echo [Option 3] Push to Docker Hub:
echo   docker login
echo   docker tag captcha-solver-api:arm64 YOUR_USERNAME/captcha-solver-api:arm64
echo   docker push YOUR_USERNAME/captcha-solver-api:arm64
echo   # On ARM64 VPS:
echo   docker pull YOUR_USERNAME/captcha-solver-api:arm64
echo.
echo ================================================
echo.
pause
