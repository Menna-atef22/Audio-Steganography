# 🔄 Complete System Flow Diagram

## Frontend-Backend Communication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER BROWSER (Port 8000)                     │
│                                                                 │
│  ┌──────────────────┬──────────────────┬──────────────────┐   │
│  │  encode.html     │  decode.html     │   noise.html     │   │
│  │  (Encoding UI)   │  (Decoding UI)   │  (Noise Test)    │   │
│  └────────┬─────────┴────────┬─────────┴────────┬─────────┘   │
│           │                  │                  │              │
│           └──────────────────┴──────────────────┘              │
│                    Shared: script.js                            │
│                    Shared: style.css                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓ FETCH API ↑
          ┌──────────────────────────────────────┐
          │   http://localhost:8000/[page]       │
          └──────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                  FLASK REST API (Port 5000)                     │
│                      api_server.py                              │
│                                                                 │
│  Route: /api/encode-download (POST)                            │
│  ├─ Input: file (WAV) + message (string)                       │
│  ├─ Process: Load → Encode with DWT → Return binary            │
│  └─ Output: Encoded WAV file (download)                        │
│                                                                 │
│  Route: /api/decode (POST)                                     │
│  ├─ Input: file (encoded WAV)                                  │
│  ├─ Process: Load → Phase extraction → Message recovery        │
│  └─ Output: JSON {message, confidence, metadata}               │
│                                                                 │
│  Route: /api/generate-test-audio (GET)                         │
│  ├─ Input: duration (seconds), sample_rate                     │
│  ├─ Process: Generate sine wave test audio                     │
│  └─ Output: WAV file (download)                                │
│                                                                 │
│  Route: /api/noise-test (POST)                                 │
│  ├─ Input: file (encoded WAV) + SNR (dB)                       │
│  ├─ Process: Add noise → Decode → Measure recovery             │
│  └─ Output: JSON {message, confidence, snr_db}                 │
│                                                                 │
│  Route: /api/health (GET)                                      │
│  └─ Output: {status: 'ok', service: 'Audio Steganography'}     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          ↓ Python imports ↑
          
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│              PYTHON CORE MODULES (core/)                        │
│                                                                 │
│  encoder.py                                                     │
│  ├─ Class: SteganoEncoder                                       │
│  ├─ Method: encode(audio, message) → (encoded_audio, metadata)  │
│  ├─ Algorithm:                                                  │
│  │  1. Validate message (alphanumeric only)                     │
│  │  2. Message → Binary (ASCII + length header)                 │
│  │  3. Apply 3x redundancy (each bit repeated 3x)               │
│  │  4. DWT Transform (db4 wavelet, level 3)                     │
│  │  5. Spread spectrum modulation (chip_rate=128)               │
│  │  6. Embed into mid-frequency DWT coefficients                │
│  │  7. Inverse DWT → Encoded audio                              │
│  └─ Return: Encoded audio, metadata dict                        │
│                                                                 │
│  decoder.py                                                     │
│  ├─ Class: SteganoDecoder                                       │
│  ├─ Method: decode(audio) → (message, confidence, metadata)     │
│  ├─ Algorithm:                                                  │
│  │  1. DWT Transform of audio                                   │
│  │  2. Extract phases at embedded positions                     │
│  │  3. Compare to expected bit values                           │
│  │  4. Majority voting for error correction                     │
│  │  5. Parse length header + extract message                    │
│  │  6. Calculate confidence score                               │
│  └─ Return: Message, confidence %, metadata                     │
│                                                                 │
│  audio_utils.py                                                 │
│  ├─ load_audio(path) → (audio_array, sample_rate)              │
│  ├─ save_audio(path, audio, sr) → saves WAV file               │
│  ├─ normalize_audio(audio) → normalized [-1, 1]                │
│  ├─ validate_message(msg) → True/False                          │
│  └─ generate_test_audio(duration, sr) → sine wave              │
│                                                                 │
│  noise_test.py                                                  │
│  ├─ add_gaussian_noise(audio, snr_db) → noisy_audio            │
│  └─ Simulates real-world noise at specified SNR                │
│                                                                 │
│  metrics.py                                                     │
│  ├─ calculate_snr(original, encoded) → dB value                │
│  ├─ calculate_correlation(audio1, audio2) → similarity         │
│  └─ Performance measurement utilities                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          ↓ Reads/Writes ↑
          
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                   FILE SYSTEM                                   │
│                                                                 │
│  audio/                                                         │
│  ├─ original/  (generated at runtime)                           │
│  │  └─ test_original.wav                                        │
│  └─ encoded/   (generated at runtime)                           │
│     └─ test_encoded.wav                                         │
│                                                                 │
│  uploads/      (temporary files during API operations)          │
│  ├─ [filename].wav (uploaded by user)                           │
│  └─ (deleted after processing)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Request-Response Cycle Example

### Encoding Workflow:
```
USER ACTION: Upload audio.wav, type "HELLO", click "Encode"
        ↓
BROWSER (encode.html):
├─ Validates inputs (file selected, message entered)
├─ Creates FormData with file + message
├─ Sends: POST http://localhost:5000/api/encode-download
└─ Waits for response
        ↓
FLASK API (api_server.py):
├─ Receives multipart FormData
├─ Extracts: file object, message="HELLO"
├─ Saves file temporarily to uploads/audio.wav
├─ Calls encoder: encoder.encode(audio_array, "HELLO")
└─ Encoder Process:
        ├─ Convert "HELLO" → ASCII → Binary
        ├─ Add 32-bit length header
        ├─ Apply 3x redundancy
        ├─ DWT Transform (db4, level 3)
        ├─ Spread spectrum (chip_rate=128)
        ├─ Embed in mid-frequency coefficients
        └─ Return encoded_audio_array
├─ Save encoded audio to BytesIO buffer
├─ Delete temporary file
└─ Return: WAV file as bytes (with download headers)
        ↓
BROWSER (encode.html):
├─ Receives blob (encoded WAV file)
├─ Creates download link
├─ Triggers automatic download as "encoded_audio.wav"
├─ Displays success message with confidence metrics
└─ Shows "Encoding Complete!" panel
        ↓
USER: File "encoded_audio.wav" now on computer ✅
```

### Decoding Workflow:
```
USER ACTION: Upload encoded_audio.wav, click "Decode"
        ↓
BROWSER (decode.html):
├─ Validates input (file selected)
├─ Creates FormData with file
├─ Sends: POST http://localhost:5000/api/decode
└─ Waits for response
        ↓
FLASK API (api_server.py):
├─ Receives multipart FormData
├─ Extracts: file object
├─ Saves file temporarily to uploads/audio.wav
├─ Calls decoder: decoder.decode(audio_array)
└─ Decoder Process:
        ├─ DWT Transform (same db4, level 3)
        ├─ Extract phase angles at embedded positions
        ├─ Compare to expected bit patterns
        ├─ Apply majority voting for error correction
        ├─ Parse length header
        ├─ Extract message characters
        ├─ Calculate confidence score (0.0-1.0)
        └─ Return: message="HELLO", confidence=0.9785
├─ Delete temporary file
└─ Return: JSON {success: true, message: "HELLO", confidence: 0.9785}
        ↓
BROWSER (decode.html):
├─ Receives JSON response
├─ Parses message and confidence
├─ Displays: "HELLO" with "97.85% Confidence"
├─ Shows metadata (wavelet, level, message length, time)
└─ Enables copy/download buttons
        ↓
USER: Message "HELLO" extracted and displayed ✅
```

### Noise Test Workflow:
```
USER ACTION: Upload encoded_audio.wav, select SNR=20dB, click "Test"
        ↓
BROWSER (noise.html):
├─ Creates FormData with file + snr_db=20
├─ Sends: POST http://localhost:5000/api/noise-test
└─ Waits for response
        ↓
FLASK API (api_server.py):
├─ Receives: file + snr_db
├─ Saves file temporarily
├─ Calls noise_test: add_gaussian_noise(audio, snr_db=20)
│   └─ Gaussian noise added at 20dB SNR
├─ Calls decoder on noisy audio
│   └─ Attempts to extract message from noisy signal
├─ Returns: {message: "HELLO", confidence: 0.95, snr_db: 20}
└─ Deletes temporary file
        ↓
BROWSER (noise.html):
├─ Displays: Message recovered despite 20dB noise
├─ Shows confidence: 95% (slightly lower than clean audio)
└─ Confirms robustness of encoding
        ↓
USER: Message still recoverable - encoding is robust ✅
```

## Data Flow Diagram

```
┌─────────────────────────┐
│  User Audio File        │
│  (WAV, 16-bit, 44.1kHz) │
└────────────┬────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Preprocessing (core/audio_utils.py)
├─ Load audio with soundfile
├─ Normalize to [-1.0, 1.0]
├─ Handle mono/stereo
└─ Validate sample rate
             │
             ↓
         ┌──────────────────────────────┐
         │  Message Preprocessing       │
         ├─ Uppercase ASCII validation  │
         ├─ Alphanumeric only          │
         ├─ Max ~12 chars (for 3s audio)
         └─ Convert to binary
             │
             ↓
┌────────────────────────────────────┐
│  Encoding (core/encoder.py)         │
├─ 1. Add 32-bit length header       │
├─ 2. Apply 3x redundancy            │
├─ 3. DWT Transform (db4, level 3)  │
├─ 4. Spread spectrum modulation     │
├─ 5. Embed in mid-freq coefficients │
├─ 6. Inverse DWT                    │
└─ 7. Normalize output
             │
             ↓
┌────────────────────────────────────┐
│  Encoded Audio Output               │
├─ Imperceptible to human ear        │
├─ SNR: ~19-20 dB                    │
├─ Correlation with original: 99.97% │
└─ Ready for transmission/storage
             │
             ↓
        [Optional: Add Noise]
             │
             ↓
┌────────────────────────────────────┐
│  Decoding (core/decoder.py)         │
├─ 1. DWT Transform                  │
├─ 2. Extract phases at positions    │
├─ 3. Compare to expected bits       │
├─ 4. Majority voting (3-bit→1-bit)  │
├─ 5. Parse length header            │
├─ 6. Extract message characters     │
└─ 7. Calculate confidence
             │
             ↓
┌────────────────────────┐
│  Extracted Message     │
├─ Original text        │
├─ Confidence score     │
└─ Success indicator
             │
             ↓
┌────────────────────────┐
│  User receives message │
│  with metadata         │
└────────────────────────┘
```

## Environment Setup

```
System
  ├─ Python 3.8+
  ├─ pip (package manager)
  └─ 100MB disk space
       │
       ↓
  requirements.txt
       ├─ scipy (signal processing)
       ├─ numpy (math operations)
       ├─ soundfile (WAV I/O)
       ├─ librosa (audio library)
       ├─ pydub (audio manipulation)
       ├─ matplotlib (visualization)
       ├─ pytest (testing)
       ├─ flask (web framework)
       ├─ flask-cors (CORS support)
       └─ pywt (wavelet transforms)
```

---

**Visual Summary**: The system is a complete web-based audio steganography platform with:
- Static frontend (HTML/CSS/JS) serving at port 8000
- REST API backend (Flask) at port 5000
- Core Python algorithms for encoding/decoding
- Full file upload/download support
- Real-time feedback and progress tracking
