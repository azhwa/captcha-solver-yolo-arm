#!/bin/bash

# Build script for ARM64 Docker image
# Run this on ARM64 machine or with Docker BuildX

set -e

echo "================================================"
echo "  Captcha Solver API - ARM64 Build Script"
echo "================================================"
echo ""

# Detect platform
ARCH=$(uname -m)
echo "[INFO] Current architecture: $ARCH"

if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    echo "[WARNING] You are not on ARM64 platform!"
    echo "Current platform: $ARCH"
    echo ""
    read -p "Continue with cross-platform build? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Build cancelled."
        exit 1
    fi
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed!"
    exit 1
fi

echo ""
echo "[1/5] Checking Docker BuildX..."
if ! docker buildx version &> /dev/null; then
    echo "[INFO] Installing Docker BuildX..."
    mkdir -p ~/.docker/cli-plugins
    BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -sSL "https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-arm64" -o ~/.docker/cli-plugins/docker-buildx
    chmod +x ~/.docker/cli-plugins/docker-buildx
fi
echo "[INFO] BuildX version: $(docker buildx version)"

echo ""
echo "[2/5] Creating builder instance..."
docker buildx create --name arm64-builder --use --platform linux/arm64 || docker buildx use arm64-builder

echo ""
echo "[3/5] Building Docker image for ARM64..."
docker buildx build \
    --platform linux/arm64 \
    --tag captcha-solver-api:arm64 \
    --tag captcha-solver-api:latest-arm64 \
    --load \
    .

echo ""
echo "[4/5] Checking image..."
docker images | grep captcha-solver-api

echo ""
echo "[5/5] Build complete!"
echo ""
echo "================================================"
echo "  ✓ ARM64 Image Ready!"
echo "================================================"
echo ""
echo "Image: captcha-solver-api:arm64"
echo ""
echo "To run:"
echo "  docker-compose up -d"
echo ""
echo "Or manually:"
echo "  docker run -d -p 8000:8000 \\"
echo "    -e API_KEYS='[\"your-key\"]' \\"
echo "    --name captcha-api \\"
echo "    captcha-solver-api:arm64"
echo ""
echo "To push to Docker Hub:"
echo "  docker login"
echo "  docker tag captcha-solver-api:arm64 YOUR_USERNAME/captcha-solver-api:arm64"
echo "  docker push YOUR_USERNAME/captcha-solver-api:arm64"
echo ""
echo "================================================"
