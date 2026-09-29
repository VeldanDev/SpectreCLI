# 🔐 SpectreCLI - Biometric OSINT Framework

A lightweight, CLI-based OSINT and reconnaissance tool with biometric authentication for Raspberry Pi Zero 2 W.

**Developer:** VeldanDev  
**Framework:** Spectre Framework

---

## 🎯 Features

### 🔍 OSINT & Reconnaissance

- **IP Tracker** - Geolocate and analyze IP addresses using ipwho.is
- **Show My IP** - Display your local and public IP addresses
- **Phone Analyzer** - Analyze phone numbers (location, provider, timezone)
- **Username Lookup** - Search across 11+ social platforms
- **DNS Query** - Query DNS records (A, AAAA, MX, TXT, NS, CNAME, SOA)
- **Domain WHOIS** - Retrieve domain registration information
- **HTTP Headers** - Analyze HTTP response headers

### 🛡️ Biometric Security

- **Face Registration** - Capture and store facial encodings
- **Face Authentication** - Verify user identity via facial recognition
- **Gesture Authentication** - Secret hand gesture verification

### 📊 Logging & History

- **Audit Log** - JSON-based audit trail of all operations
- **History Viewer** - Browse scan history
- **Metadata Export** - Export results in JSON or TXT format

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- OpenCV with camera support
- MediaPipe for hand gesture recognition

### Quick Setup

#### 1. Clone/Copy the project

```bash
git clone <repo-url>
cd SpectreCLI
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For Raspberry Pi, you may need to build OpenCV from source or use pre-built wheels:

```bash
pip install opencv-python-headless
```

#### 3. Run the CLI

```bash
python3 spectra_cli.py
```

---

## 📋 First Run

On first run, the CLI will:

1. **Prompt face registration** - Position your face toward the camera, move slightly
2. **Face authentication** - Verify registered face (12-second timeout)
3. **Gesture authentication** - Input secret hand gesture sequence `[3, 1, 4]`
4. **Access granted** - Main menu becomes available

---

## 🎮 Main Menu

```text
1. IP Tracker           - Geolocate IP addresses
2. Show My IP           - Display local/public IP
3. Phone Analyzer       - Analyze phone numbers
4. Username Lookup      - Search social platforms
5. DNS Query            - Query DNS records
6. Domain WHOIS         - Get domain info
7. HTTP Headers         - Analyze HTTP responses
8. Metadata Viewer      - View last scan details
9. History Viewer       - Browse scan history
10. Export History      - Export results to file
0. Exit                 - Close application
```

---

## 🔐 Biometric Configuration

### Face Authentication

- **File:** `owner_face.pkl`
- **Stores:** Face encodings (128-dimensional vectors)
- **Tolerance:** 0.5 (tunable for security vs. ease)
- **Timeout:** 12 seconds

### Gesture Authentication

- **Secret Sequence:** `[3, 1, 4]` (hold fingers 0-5)
- **Stability Time:** 0.8 seconds per gesture
- **Time Limit:** 15 seconds total
- **Located in:** `gesture_auth.py` (modify `SECRET_GESTURE`)

---

## 📁 Project Structure

```text
SpectreCLI/
├── spectra_cli.py           # Main CLI entry point
├── face_register.py         # Face enrollment module
├── face_auth.py             # Face authentication module
├── gesture_auth.py          # Hand gesture authentication
├── requirements.txt         # Python dependencies
├── history.json             # Scan history log
├── audit.json               # Security audit trail
├── auth.json                # Authentication logs
└── owner_face.pkl           # Stored face encodings
```

---

## 🛠️ Development

### Adding New OSINT Tools

Add your function to `spectra_cli.py`, then update the main menu:

```python
def my_new_tool():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "My Tool\n")
    # Your implementation
    save_history("tool_name", target, result)
    save_audit_log("My Tool", {"data": result})
    input("\nPress Enter to continue...")
```

### Modifying Biometric Security

- **Face tolerance:** Edit `face_auth.py` line with `tolerance=0.5`
- **Gesture sequence:** Edit `gesture_auth.py` - change `SECRET_GESTURE`
- **Time limits:** Adjust `TIME_LIMIT` or `TIMEOUT` values

---

## ⚙️ Troubleshooting

### Camera Not Working

```bash
# Test camera access
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### DNS Module Errors

```bash
pip install dnspython --upgrade
```

### WHOIS Lookup Fails

```bash
pip install python-whois --upgrade
```

### Face Recognition Issues on Pi Zero

- Use lighter model versions
- Reduce face detection confidence values
- Consider running on Pi 4 for better performance

---

## 📝 JSON Data Format

### History Entry

```json
{
  "time": "2024-01-15 14:30:45",
  "type": "ip",
  "target": "8.8.8.8",
  "result": {
    "ip": "8.8.8.8",
    "country": "US",
    "city": "Mountain View"
  }
}
```

### Audit Entry

```json
{
  "IP Tracker": [
    {
      "query": "1.1.1.1",
      "resolved": "1.1.1.1",
      "status": "success",
      "time": "2024-01-15 14:30:45"
    }
  ]
}
```

---

## ⚠️ Legal Disclaimer

**SpectreCLI** is for authorized security research and testing only. Users are responsible for:

- Obtaining proper authorization before scanning networks or systems
- Complying with local laws and regulations
- Respecting privacy and data protection regulations (GDPR, CCPA, etc.)

Unauthorized access to computer systems is illegal.

---

## 🤝 Contributing

Found a bug or have a feature request? Submit an issue or pull request!

---

## 📜 License

Spectre Framework - All rights reserved  
Developed by: **VeldanDev**

---

## 🙏 Credits

- **IP Lookup:** ipwho.is API
- **Phone Analysis:** phonenumbers library
- **DNS:** dnspython
- **Face Recognition:** face_recognition library
- **Hand Tracking:** MediaPipe

---

**Last Updated:** April 2024  
**Version:** 2.1 (with DNS & WHOIS tools)
