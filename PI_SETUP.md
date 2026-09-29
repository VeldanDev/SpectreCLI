# SpectreCLI on Raspberry Pi Zero 2 W - Setup Guide

## System Requirements

- **OS:** Raspberry Pi OS (32-bit or 64-bit)
- **RAM:** Minimum 512MB (1GB recommended)
- **Storage:** 2GB free space
- **Python:** 3.8 or higher
- **Camera:** USB camera or Raspberry Pi Camera Module

---

## Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Python & Dependencies

```bash
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfbuzz0b libwebp6
sudo apt install -y libqtgui4 python3-pyqt5 libhdf5-dev libharfbuzz0b libwebp6 libtiff5
```

## Step 3: Install OpenCV (Lightweight)

For Pi Zero, use pre-built wheels:

```bash
pip3 install opencv-python-headless
```

Or for regular OpenCV with GUI:

```bash
pip3 install opencv-python
```

## Step 4: Install MediaPipe (Hand Detection)

```bash
pip3 install mediapipe
```

> **Note:** MediaPipe pre-compiled wheels may not be available for Pi Zero ARM32. If installation fails, compile from source or skip gesture authentication.

## Step 5: Install SpectreCLI Dependencies

```bash
cd ~/SpectreCLI
pip3 install -r requirements.txt
```

## Step 6: Camera Setup

### For USB Camera

```bash
# List connected cameras
lsusb

# Test camera access
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### For Raspberry Pi Camera Module

Enable camera in raspi-config:

```bash
sudo raspi-config
# Navigate: Interfacing Options → Camera → Enable
```

## Step 7: Run SpectreCLI

```bash
python3 spectra_cli.py
```

---

## 🔧 Optimization Tips

### 1. Reduce Face Recognition Timeout

Edit `face_auth.py`:

```python
if time.time() - start_time > 6:  # Reduced from 12
```

### 2. Lower Detection Confidence

Edit `gesture_auth.py`:

```python
min_detection_confidence=0.5  # Lower threshold
min_tracking_confidence=0.5
```

### 3. Disable Unused Features

Comment out imports in `spectra_cli.py`:

```python
# import whois  # Skip WHOIS on low-memory systems
```

### 4. Use Headless OpenCV

Already included in requirements for Pi Zero

---

## 🔌 Camera Troubleshooting

### Camera Not Detected

```bash
# Check if camera is initialized
v4l2-ctl --list-devices

# Reload camera drivers
sudo modprobe bcm2835_v4l2
```

### Low FPS / Lag

- Reduce frame resolution
- Lower detection confidence
- Disable preview window (set cv2.imshow() calls to pass)

### Permission Denied

```bash
# Add user to video group
sudo usermod -a -G video $USER
# Logout and login
```

---

## 📦 Create Startup Script

Create `start_spectre.sh`:

```bash
#!/bin/bash
cd /home/pi/SpectreCLI
python3 spectra_cli.py
```

Make executable:

```bash
chmod +x start_spectre.sh
```

Run on startup (add to crontab or systemd):

```bash
@reboot /home/pi/start_spectre.sh
```

---

## 🚀 Advanced: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM arm32v7/python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "spectra_cli.py"]
```

Build & run:

```bash
docker build -t spectrecli .
docker run -it --device=/dev/video0 spectrecli
```

---

## 📊 Performance Benchmarks

*On Raspberry Pi Zero 2 W:*

| Feature | Time |
| --- | --- |
| Face Registration (10 samples) | ~8 seconds |
| Face Authentication | ~3-4 seconds |
| Gesture Authentication | ~5-15 seconds |
| IP Lookup (with network) | ~2-3 seconds |
| DNS Query | ~1-2 seconds |

---

## 🐛 Known Issues

1. **MediaPipe on Pi Zero:** May not have pre-built wheels for 32-bit ARM
   - Solution: Build from source or use 64-bit OS
2. **Network requests timeout:** Pi Zero has slower connection
   - Solution: Increase timeout values in `spectra_cli.py`
3. **Memory overflow on large history**
   - Solution: Regularly export and clear history.json

---

## 📞 Support

For issues specific to Raspberry Pi, check:

- Raspberry Pi OS documentation
- OpenCV on Raspberry Pi guides
- MediaPipe GitHub issues

---

**Last Updated:** April 2024
