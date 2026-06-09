# 🚀 Audio Steganography - Quick Start Guide

## Installation
```bash
pip install -r requirements.txt
```

## Running the System

### Windows (Easiest)
```bash
START_SERVERS.bat
```
Then open: **http://localhost:8000**

### macOS / Linux
```bash
chmod +x start_servers.sh
./start_servers.sh
```
Then open: **http://localhost:8000**

### Manual (Separate Terminals)
```bash
# Terminal 1
python api_server.py

# Terminal 2
python -m http.server 8000 --directory frontend
```

## Key Features

| Feature | Limit | Notes |
|---------|-------|-------|
| **Message Length** | ~12 characters | For 3-second audio at 44.1 kHz |
| **Audio Format** | WAV, PCM, 16-bit | Mono or stereo supported |
| **Sample Rate** | 44.1 - 48 kHz | Most common rates |
| **Alphanumeric** | A-Z, 0-9, spaces | Only uppercase letters |
| **Encoding Time** | < 1 second | For 3-second audio |
| **Robustness** | ±20 dB SNR | Survives moderate noise |

## Workflow Examples

### 1️⃣ Encode a Message
1. Open http://localhost:8000/encode.html
2. Upload a WAV file
3. Type your message (e.g., "HELLO")
4. Click "Encode & Download"
5. File downloads as `encoded_[filename].wav`

### 2️⃣ Decode the Message
1. Open http://localhost:8000/decode.html
2. Upload the encoded file
3. Click "Decode"
4. See the extracted message with confidence %

### 3️⃣ Test with Noise
1. Open http://localhost:8000/noise.html
2. Upload encoded audio
3. Select noise level (SNR)
4. Click "Test"
5. See if message is still recoverable

### 4️⃣ Generate Test Audio
- On any page, click "Generate Test Audio (3 seconds)"
- Gets automatically selected for encoding
- Perfect for testing without your own files

## What's Hidden?

When you encode a message:

```
Your Message: "HELLO"
       ↓
Binary: 01001000 01000101 01001100 01001100 01001111
       ↓
Wavelet Transform (DWT, level 3, db4 wavelet)
       ↓
Spread Spectrum Modulation (chip rate 128)
       ↓
Embedding into Mid-Frequency Coefficients (alpha = 0.03)
       ↓
Inverse Transform → Encoded Audio
       ↓
Result: Sounds IDENTICAL to original! 🎵
```

## Ports

| Service | Port | URL |
|---------|------|-----|
| Web Frontend | 8000 | http://localhost:8000 |
| Flask API | 5000 | http://localhost:5000 |

## Troubleshooting

### "Connection refused" on port 5000?
- Make sure `api_server.py` is running
- Check if another app is using port 5000
- Run: `netstat -ano | find "5000"` (Windows) or `lsof -i :5000` (Mac/Linux)

### "Message too long" error?
- Maximum capacity is ~12 characters for 3-second audio
- Use longer audio files to hide longer messages
- Or increase chip_rate in the encoder

### Audio quality seems degraded?
- This is normal - the embedding adds slight artifacts
- The audio is designed to be imperceptible to human ears
- SNR remains > 19 dB

### File download not working?
- Check browser console (F12) for errors
- Ensure both servers are running
- Check CORS is enabled (it is, in api_server.py)

## Testing with Command Line

```bash
# Encode and download
curl -X POST http://localhost:5000/api/encode-download \
  -F "file=@test.wav" \
  -F "message=HELLO" \
  -o encoded.wav

# Decode
curl -X POST http://localhost:5000/api/decode \
  -F "file=@encoded.wav"

# Generate test audio
curl "http://localhost:5000/api/generate-test-audio?duration=3.0&sr=44100" \
  -o test.wav
```

## Key Files

| File | Purpose |
|------|---------|
| `api_server.py` | Flask REST API backend |
| `core/encoder.py` | DWT + Spread Spectrum encoding |
| `core/decoder.py` | Phase extraction + message recovery |
| `frontend/encode.html` | Upload & encode interface |
| `frontend/decode.html` | Upload & decode interface |
| `frontend/script.js` | JavaScript for API calls |
| `START_SERVERS.bat` | Run both servers (Windows) |
| `start_servers.sh` | Run both servers (Mac/Linux) |

## Performance Metrics

Typical results from test run:

```
✅ Message Encoded: "HELLO WORLD"
   SNR: 19.78 dB
   Correlation: 0.9997 (99.97%)
   Confidence: 97.85%
```

---

**Need help?** Check README.md or review the code comments in `core/` directory.
