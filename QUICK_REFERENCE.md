# ⚡ Quick Reference Card - Audio Steganography System

## 🚀 Start the System (30 seconds)

### Windows
```bash
START_SERVERS.bat
```

### macOS/Linux
```bash
./start_servers.sh
```

Then open: **http://localhost:8000**

---

## 📋 Common Commands

### Generate Test Audio
```bash
curl "http://localhost:5000/api/generate-test-audio?duration=3" -o test.wav
```

### Encode Message
```bash
curl -X POST http://localhost:5000/api/encode-download \
  -F "file=@audio.wav" \
  -F "message=HELLO" \
  -o encoded.wav
```

### Decode Message
```bash
curl -X POST http://localhost:5000/api/decode \
  -F "file=@encoded.wav"
```

### Test Robustness
```bash
curl -X POST http://localhost:5000/api/noise-test \
  -F "file=@encoded.wav" \
  -F "snr_db=20"
```

### Check API Status
```bash
curl http://localhost:5000/api/health
```

---

## 🔗 URLs
| Service | URL |
|---------|-----|
| Home | http://localhost:8000 |
| Encode | http://localhost:8000/encode.html |
| Decode | http://localhost:8000/decode.html |
| Noise Test | http://localhost:8000/noise.html |
| API | http://localhost:5000 |
| Health Check | http://localhost:5000/api/health |

---

## 📁 File Locations

| Purpose | Path |
|---------|------|
| API Server | `api_server.py` |
| Encoder | `core/encoder.py` |
| Decoder | `core/decoder.py` |
| Frontend | `frontend/` |
| Tests | `tests/` |
| Docs | `*.md` files |
| Config | `requirements.txt` |

---

## ⚙️ Configuration

### Change API Port
Edit last line of `api_server.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)  # Change 5000 → 5001
```

### Change Web Port
```bash
python -m http.server 9000 --directory frontend
```

### Enable Debug Mode
```python
# In api_server.py
app.run(debug=True, port=5000)
```

---

## 🧪 Quick Tests

### Test 1: API Alive?
```bash
curl http://localhost:5000/api/health
```

### Test 2: Can Encode?
```bash
curl -X POST http://localhost:5000/api/encode-download \
  -F "file=@test.wav" -F "message=TEST" -o out.wav && echo "✅ Encode OK"
```

### Test 3: Can Decode?
```bash
curl -X POST http://localhost:5000/api/decode \
  -F "file=@encoded.wav" | grep -q "message" && echo "✅ Decode OK"
```

---

## 📊 Key Limits

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max Message Length | ~12 chars | For 3-second audio |
| Sample Rate | 44.1-48 kHz | Standard rates |
| File Format | WAV, PCM, 16-bit | MP3/OGG not supported |
| Max File Size | 50 MB | Upload limit |
| Audio Quality | Imperceptible | SNR: 19-20 dB |
| Robustness | ±20 dB SNR | Can survive noise |
| Capacity | ~4 bits/sec | Depends on parameters |

---

## 🎯 Workflow Examples

### Scenario 1: Encode a Message
```
1. Open http://localhost:8000/encode.html
2. Click "Generate Test Audio"
3. Type: HELLO
4. Click "Encode & Download"
5. ✅ File downloaded: encoded_test_audio_3s.wav
```

### Scenario 2: Decode a Message
```
1. Open http://localhost:8000/decode.html
2. Upload: encoded_test_audio_3s.wav
3. Click "Decode"
4. ✅ Shows: HELLO (97.85% confidence)
```

### Scenario 3: Test Noise Robustness
```
1. Open http://localhost:8000/noise.html
2. Upload: encoded_test_audio_3s.wav
3. Set SNR: 20 dB
4. Click "Test"
5. ✅ Shows: Message recoverable despite noise
```

---

## 🐛 Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Connection refused | API not running | Run `python api_server.py` |
| Message too long | > 12 chars | Use shorter message or longer audio |
| No file provided | File not uploaded | Select file in UI |
| CORS error | Frontend can't reach API | Check both servers running |
| Module not found | Missing dependency | Run `pip install -r requirements.txt` |
| Port in use | Another app using port | Kill existing process or use different port |

---

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| README.md | Full project overview |
| QUICK_START.md | First-time setup |
| SETUP_GUIDE.md | Detailed installation |
| TESTING_GUIDE.md | How to test everything |
| SYSTEM_FLOW.md | Architecture & flow diagrams |
| SESSION_UPDATE.md | What's new in this session |

---

## ✨ Performance Tips

### Faster Encoding
- Reduce DWT level (2 instead of 3)
- Increase chip_rate (256 instead of 128)
- Use shorter audio

### Better Recovery
- Increase DWT level (4 instead of 3)
- Decrease chip_rate (64 instead of 128)
- Use longer audio

### More Robust to Noise
- Increase embedding strength
- Use lower frequencies
- Add redundancy

---

## ⏱️ Typical Durations

| Task | Time |
|------|------|
| Install dependencies | 2-3 min |
| Start servers | 5 sec |
| Generate 3s test audio | 0.1 sec |
| Encode 3s message | 0.5 sec |
| Decode 3s audio | 0.3 sec |
| Full workflow (encode + decode) | 2 sec |
| Run all tests | 1 sec |

---

**Everything working? You're ready to go! 🎉**

For help: See README.md or SETUP_GUIDE.md

Problem: Audio quality issues
Solution: Reduce embedding strength or use larger window


FILE I/O OPERATIONS
====================

# Get audio statistics before encoding
from core.audio_utils import get_signal_statistics

stats = get_signal_statistics(audio)
print(f"RMS: {stats['rms']}")
print(f"Peak: {stats['peak']}")

# Validate message before encoding
from core.audio_utils import validate_message

if validate_message("HELLO 123"):
    print("Valid message")
else:
    print("Invalid characters")

# Generate test audio
from core.audio_utils import generate_test_audio

test_audio = generate_test_audio(duration=10.0, sr=44100)
save_audio("test.wav", test_audio, 44100)


DATA FILES STRUCTURE
====================

Original Audio Files (60 seconds each):
  data/original/original_1.wav   - Simple 440 Hz tone
  data/original/original_2.wav   - C Major chord
  data/original/original_3.wav   - Complex spectrum

Encoded Audio Files (with hidden messages):
  data/encoded/encoded_1.wav     - Message: "HELLO WORLD"
  data/encoded/encoded_2.wav     - Message: "SECRET MESSAGE 123"
  data/encoded/encoded_3.wav     - Message: "AUDIO STEGANOGRAPHY TEST"

Noisy Versions (for robustness testing):
  data/encoded/noisy_1_light.wav      - 30 dB SNR (5% error)
  data/encoded/noisy_1_moderate.wav   - 20 dB SNR (10% error)
  data/encoded/noisy_1_heavy.wav      - 10 dB SNR (30% error)
  (same for files 2 and 3)


PERFORMANCE BENCHMARKS
======================

Encoding Time:
  1 second audio:  ~100 ms
  10 second audio: ~500 ms
  60 second audio: ~3 seconds

Decoding Time:
  1 second audio:  ~80 ms
  10 second audio: ~400 ms
  60 second audio: ~2.5 seconds

File Sizes:
  Original 60s @ 44.1kHz: ~5.3 MB
  Encoded (same): ~5.3 MB (no size change)
  With 3x redundancy: Still same size (embedded in phase)

Message Capacity:
  Depends on duration and parameters
  Typical: 30-50 bits per second
  60 second audio: ~1800-3000 bits
  With error correction: ~225-375 usable bits
  Character capacity: ~28-46 uppercase characters


COMMON WORKFLOWS
=================

# Workflow 1: Hide message and send
message = "MEETING AT 3 PM"
encoded, _ = encode_audio(audio, message, sr=44100)
save_audio("stego_message.wav", encoded, 44100)
# Send stego_message.wav to recipient

# Workflow 2: Receive and extract
received, sr = load_audio("stego_message.wav")
message, confidence, _ = decode_audio(received, sr=sr)
if confidence > 0.7:
    print(f"Message: {message}")

# Workflow 3: Test robustness
for snr in [40, 30, 20, 10]:
    noisy = add_gaussian_noise(encoded, snr)
    msg, conf, _ = decode_audio(noisy, sr)
    print(f"{snr} dB SNR: {msg} (confidence: {conf:.1%})")

# Workflow 4: Full analysis
report = generate_performance_report(
    original_message=message,
    recovered_message=decoded_msg,
    original_audio=audio,
    encoded_audio=encoded,
    confidence=confidence
)
print_report(report)


DEBUGGING TIPS
==============

# Check if audio loads correctly
audio, sr = load_audio("file.wav")
assert len(audio) > 0, "Audio file empty"
assert sr in [44100, 48000], "Unsupported sample rate"

# Verify encoding works
try:
    encoded, _ = encode_audio(audio, "TEST", sr=sr)
    print(f"Encoding OK: {len(encoded)} samples")
except Exception as e:
    print(f"Encoding failed: {e}")

# Check decoder output
msg, conf, meta = decode_audio(encoded, sr=sr)
print(f"Message: '{msg}'")
print(f"Confidence: {conf:.1%}")
print(f"Message length: {len(msg)}")
print(f"Confidence threshold: {meta.get('confidence_threshold', 'N/A')}")

# Compare original and encoded
import numpy as np
mse = np.mean((audio - encoded)**2)
print(f"Mean Square Error: {mse:.6f}")
print(f"Normalized: {mse / np.mean(audio**2) * 100:.3f}%")


TESTING WORKFLOW
=================

1. Run quick demo:
   python scripts/quick_demo.py

2. Generate test data:
   python scripts/generate_test_data.py

3. Run full tests:
   pytest tests/test_system.py -v

4. Test specific functionality:
   pytest tests/test_system.py::TestEncoder -v

5. Run with detailed output:
   pytest tests/test_system.py -v -s

6. Check coverage:
   pytest tests/test_system.py --cov=core


OPTIMIZATION TIPS
=================

For Maximum Robustness:
  - Use larger window_size (1024)
  - Use smaller hop_length (128)
  - Use lower sensitivity (0.3)
  - Repeat message encoding 2-3 times

For Maximum Speed:
  - Use smaller window_size (256)
  - Use larger hop_length (512)
  - Shorter audio files

For Maximum Imperceptibility:
  - Use smaller embedding_strength (0.3-0.5)
  - Use larger frequency range
  - Test with listeners

For Maximum Capacity:
  - Longer audio files
  - Larger window_size (more bins)
  - Smaller message (less redundancy needed)
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║              QUICK REFERENCE GUIDE - READY TO USE             ║
╚════════════════════════════════════════════════════════════════╝

Key Commands:
  python scripts/quick_demo.py        → Quick test
  python scripts/generate_test_data.py → Test files
  pytest tests/test_system.py -v      → Run tests
  frontend/index.html                 → Web UI

See QUICK_REFERENCE.md for complete examples!
""")
