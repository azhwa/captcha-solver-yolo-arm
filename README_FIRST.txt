========================================
  CAPTCHA SOLVER API - ARM64 VERSION
========================================

This is the ARM64-optimized version of Captcha Solver API
Designed for ARM64 processors (AWS Graviton, Oracle ARM, Raspberry Pi, Apple Silicon)


========================================
FILES IN THIS PACKAGE
========================================

📁 api/                    - API source code
📄 best.pt                 - YOLOv8 model (22MB)
📄 Dockerfile              - ARM64-optimized Docker image
📄 docker-compose.yml      - Docker orchestration for ARM64
📄 requirements.txt        - Python dependencies
📄 .env.example            - Environment variables template

📘 README.md               - Main documentation
📘 ARM64_GUIDE.txt         - Complete ARM64 deployment guide
📘 QUICK_START.txt         - Fastest way to deploy
📘 README_FIRST.txt        - This file

🔧 build-arm64.sh          - Build script for Linux/Mac
🔧 build-arm64.bat         - Build script for Windows


========================================
COMPATIBLE PLATFORMS
========================================

✅ Cloud VPS ARM64:
   - AWS Graviton (t4g instances)
   - Oracle Cloud ARM (FREE FOREVER!)
   - Azure ARM VMs
   - Google Cloud Tau T2A

✅ Single Board:
   - Raspberry Pi 4/5
   - NVIDIA Jetson
   - Rock Pi

✅ Development:
   - Apple Silicon (M1/M2/M3)
   - ARM laptops


========================================
QUICK START (5 MINUTES)
========================================

[On ARM64 VPS/Server]

1. Install Docker:
   curl -fsSL https://get.docker.com | sudo sh
   sudo usermod -aG docker $USER

2. Upload this folder to server:
   scp -r captcha-solver-yolo-arm user@server-ip:~/

3. SSH & Deploy:
   ssh user@server-ip
   cd captcha-solver-yolo-arm
   nano docker-compose.yml  # Edit API_KEYS
   docker-compose up -d --build

4. Test:
   curl http://localhost:8000/api/v1/health

Done! 🎉


========================================
WHICH FILE TO READ?
========================================

Just getting started?
→ Read: QUICK_START.txt

Need detailed guide?
→ Read: ARM64_GUIDE.txt

Want API documentation?
→ Read: README.md

Using Oracle Cloud ARM Free?
→ Read: ARM64_GUIDE.txt (section: ORACLE CLOUD ARM)

Using Raspberry Pi?
→ Read: ARM64_GUIDE.txt (section: RASPBERRY PI)

Building from Windows?
→ Run: build-arm64.bat

Building from Linux/Mac?
→ Run: build-arm64.sh


========================================
RECOMMENDED: ORACLE CLOUD ARM
========================================

Oracle offers ARM64 VPS completely FREE forever!

Specs (Always Free):
- 4 ARM CPU cores
- 24GB RAM
- 200GB storage
- FREE forever!

Perfect for this API!

Guide: ARM64_GUIDE.txt (search for "ORACLE CLOUD")


========================================
SUPPORT
========================================

API Endpoints:
- Health: http://SERVER_IP:8000/api/v1/health
- Detect: http://SERVER_IP:8000/api/v1/detect
- Docs:   http://SERVER_IP:8000/docs

Troubleshooting:
→ Check logs: docker-compose logs -f
→ Check guide: ARM64_GUIDE.txt (section: TROUBLESHOOTING)

Performance Issues:
→ Increase threads: Edit docker-compose.yml
   OMP_NUM_THREADS=8 (match your CPU cores)


========================================
WHAT'S DIFFERENT FROM x86 VERSION?
========================================

✅ Optimized for ARM64 architecture
✅ OpenBLAS integration for faster computation
✅ Multi-threading optimization
✅ Reduced memory footprint
✅ Platform-specific base image
✅ ARM-specific dependencies

Performance:
- Build time: 10-15 min (first time)
- Inference: 50-150ms per image
- Memory: ~1.5GB


========================================
NEXT STEPS
========================================

1. Choose your platform (Oracle Free recommended!)
2. Read QUICK_START.txt or ARM64_GUIDE.txt
3. Deploy in 5-10 minutes
4. Start detecting captchas!


========================================

Questions? Check ARM64_GUIDE.txt for detailed answers!

Happy detecting! 🚀
