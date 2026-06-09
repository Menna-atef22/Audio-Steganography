# 🎯 Setup & Deployment Guide

## Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager available
- **Windows, macOS, or Linux** (all supported)

## Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd Audio-Steganography

# Install all required packages
pip install -r requirements.txt
```

### What gets installed:
- **scipy**: Signal processing (Fourier transforms)
- **numpy**: Numerical computations
- **librosa**: Audio library
- **soundfile**: WAV file I/O
- **pydub**: Audio manipulation
- **matplotlib**: Visualization
- **pytest**: Testing framework
- **flask**: Web framework for API
- **flask-cors**: CORS support for cross-origin requests
- **pywt**: Wavelet transforms

## Step 2: Start Both Servers

### Option A: Automatic Startup (Recommended)

#### Windows:
```bash
START_SERVERS.bat
```
This will automatically:
1. Verify dependencies are installed
2. Start Flask API on http://localhost:5000
3. Start static web server on http://localhost:8000
4. Show URLs in the console

#### macOS / Linux:
```bash
chmod +x start_servers.sh
./start_servers.sh
```

### Option B: Manual Startup (Separate Terminals)

**Terminal 1 - Flask API Server:**
```bash
python api_server.py
```
Expected output:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

**Terminal 2 - Static Web Server:**
```bash
python -m http.server 8000 --directory frontend
```
Expected output:
```
Serving HTTP on 0.0.0.0 port 8000
```

## Step 3: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

You should see the Audio Steganography home page with links to:
- 🔐 Encode (hide a message)
- 🔓 Decode (extract a message)
- 📊 Noise Test (test robustness)

## Step 4: Test the System

### Test Workflow:

1. **On Encode page** (http://localhost:8000/encode.html):
   - Click "Generate Test Audio (3 seconds)"
   - Type a message: `HELLO`
   - Click "Encode & Download"
   - File `encoded_test_audio_3s.wav` downloads

2. **On Decode page** (http://localhost:8000/decode.html):
   - Upload the `encoded_test_audio_3s.wav`
   - Click "Decode"
   - You should see: Message = `HELLO`, Confidence ~95%+

3. **On Noise page** (http://localhost:8000/noise.html):
   - Upload the encoded audio
   - Set SNR to 20 dB
   - Click "Test"
   - Message still recoverable!

## Architecture Overview

```
┌─────────────────────────────────────────┐
│     Browser (http://localhost:8000)     │
│  ┌─────────────────────────────────────┐│
│  │  HTML/CSS/JavaScript Frontend       ││
│  │  - encode.html                      ││
│  │  - decode.html                      ││
│  │  - noise.html                       ││
│  │  - style.css                        ││
│  │  - script.js                        ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
            ↓ HTTP/CORS ↑
┌─────────────────────────────────────────┐
│  Flask API Server (port 5000)           │
│  ┌─────────────────────────────────────┐│
│  │  api_server.py                      ││
│  │  - /api/encode-download             ││
│  │  - /api/decode                      ││
│  │  - /api/generate-test-audio         ││
│  │  - /api/noise-test                  ││
│  │  - /api/health                      ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
            ↓ Python imports ↑
┌─────────────────────────────────────────┐
│  Core Modules (core/)                   │
│  ┌─────────────────────────────────────┐│
│  │  encoder.py        DWT + Spread     ││
│  │  decoder.py        Phase extraction ││
│  │  audio_utils.py    File I/O         ││
│  │  noise_test.py     Robustness test  ││
│  │  metrics.py        Performance      ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## Port Configuration

| Service | Port | Purpose |
|---------|------|---------|
| Static Web Server | 8000 | HTML/CSS/JS frontend |
| Flask API | 5000 | REST API backend |
| Optional: Custom API | 5001+ | If port 5000 is busy |

### Change Flask Port

Edit `api_server.py`, last line:
```python
# Change from:
app.run(debug=False, host='0.0.0.0', port=5000)

# To:
app.run(debug=False, host='0.0.0.0', port=5001)
```

Then update `frontend/encode.html` and `frontend/decode.html`:
```javascript
// Change from:
const API_URL = 'http://localhost:5000';

// To:
const API_URL = 'http://localhost:5001';
```

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find what's using the port
# Windows:
netstat -ano | find "5000"
taskkill /PID [PID] /F

# macOS/Linux:
lsof -i :5000
kill -9 [PID]
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --upgrade
```

### CORS Error in Browser

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Make sure `api_server.py` is running (CORS is enabled)
```bash
python api_server.py
```

### Audio File Upload Fails

**Error:** `No file provided` or `No file selected`

**Solution:** 
- Check file is WAV format
- File size must be < 50 MB
- Ensure browser has permission to access files

### Message Won't Decode

**Possible Causes:**
1. Using different wavelet than encoding
2. Using different DWT level than encoding
3. Audio file is corrupted
4. Message exceeds capacity (max ~12 chars for 3s audio)

**Solution:**
- Regenerate test audio and try again
- Check encoding parameters match decoding
- Try with shorter message

## Performance Benchmarks

Typical performance on modern hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Encode (3s audio) | ~0.5s | DWT level 3 |
| Decode (3s audio) | ~0.3s | Phase extraction |
| Generate test audio | ~0.1s | Sine wave generation |
| Add noise | ~0.2s | Gaussian noise |

## File Structure After Installation

```
Audio-Steganography/
├── api_server.py              # Flask REST API
├── START_SERVERS.bat          # Windows startup script
├── start_servers.sh           # macOS/Linux startup script
├── requirements.txt           # Python dependencies
├── README.md                  # Full documentation
├── QUICK_START.md             # Quick reference
├── SETUP_GUIDE.md             # This file
│
├── core/
│   ├── encoder.py             # Encoding algorithm
│   ├── decoder.py             # Decoding algorithm
│   ├── audio_utils.py         # Audio I/O utilities
│   ├── noise_test.py          # Robustness testing
│   └── metrics.py             # Performance metrics
│
├── frontend/
│   ├── index.html             # Homepage
│   ├── encode.html            # Encoding UI (now with API)
│   ├── decode.html            # Decoding UI (now with API)
│   ├── noise.html             # Noise testing UI
│   ├── style.css              # Styling
│   └── script.js              # Shared JavaScript
│
├── tests/
│   ├── test_encoder.py
│   ├── test_decoder.py
│   └── test_system.py
│
├── audio/
│   ├── original/              # (Generated at runtime)
│   └── encoded/               # (Generated at runtime)
│
└── uploads/                   # (Created at runtime)
    └── (Temporary uploaded files)
```

## Running Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_encoder.py

# Run with verbose output
pytest -v

# Run with coverage
pip install pytest-cov
pytest --cov=core tests/
```

## Performance Optimization

### For Faster Encoding:
- Reduce DWT level (e.g., 2 instead of 3)
- Increase chip rate (e.g., 256 instead of 128)
- Use shorter audio files

### For Better Message Recovery:
- Increase DWT level (e.g., 4 instead of 3)
- Decrease chip rate (e.g., 64 instead of 128)
- Use longer audio files
- Avoid audio compression (keep as WAV)

### For Robustness Against Noise:
- Increase embedding strength (alpha parameter)
- Use lower frequencies (avoid high frequencies)
- Repeat encoding (add redundancy)

## Next Steps

1. **Basic Usage**: See QUICK_START.md
2. **API Integration**: Review api_server.py docstrings
3. **Algorithm Details**: Read comments in core/encoder.py and core/decoder.py
4. **Advanced Usage**: Check README.md

## Support & Development

### Running in Development Mode

For debugging:
```bash
# Terminal 1: Flask with debug mode
python -c "from api_server import app; app.run(debug=True, host='0.0.0.0', port=5000)"

# Terminal 2: Static server
python -m http.server 8000 --directory frontend
```

### Accessing API Directly

Test endpoints with curl:
```bash
# Health check
curl http://localhost:5000/api/health

# List test audio
curl "http://localhost:5000/api/generate-test-audio?duration=3" -o test.wav

# Decode
curl -X POST http://localhost:5000/api/decode -F "file=@encoded.wav"
```

---

**Installation complete!** You should now have:
✅ All dependencies installed
✅ Two servers running (Flask + HTTP)
✅ Web interface accessible at http://localhost:8000
✅ Ready to encode and decode messages
