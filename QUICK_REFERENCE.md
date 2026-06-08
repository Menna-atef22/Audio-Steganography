"""
QUICK REFERENCE GUIDE - Audio Steganography System
====================================================
"""

COMMAND REFERENCE
=================

# Run Quick Demo (10 seconds)
python scripts/quick_demo.py

# Generate Test Data (creates 12 WAV files)
python scripts/generate_test_data.py

# Run Full Test Suite
pytest tests/test_system.py -v

# Run Specific Test
pytest tests/test_system.py::TestEncoder::test_basic_encoding -v

# Start Streamlit Web App
python -m streamlit run app.py

# Start Streamlit in specific browser
streamlit run app.py --logger.level=debug


PYTHON API EXAMPLES
====================

# === BASIC ENCODING ===
from core.encoder import encode_audio
from core.audio_utils import load_audio, save_audio

# Load audio file
audio, sr = load_audio("myaudio.wav")

# Hide message
message = "HELLO WORLD"
encoded, metadata = encode_audio(audio, message, sr=sr)

# Save encoded audio
save_audio("encoded.wav", encoded, sr)


# === BASIC DECODING ===
from core.decoder import decode_audio

# Load encoded audio
encoded, sr = load_audio("encoded.wav")

# Extract message
message, confidence, metadata = decode_audio(encoded, sr=sr)
print(f"Message: {message}")
print(f"Confidence: {confidence:.1%}")


# === NOISE TESTING ===
from core.noise_test import add_gaussian_noise

# Add noise at 20 dB SNR
noisy = add_gaussian_noise(encoded, snr_db=20)

# Try to decode from noisy audio
message, confidence, _ = decode_audio(noisy, sr=sr)
print(f"Decoded from noise: {message}")


# === PERFORMANCE ANALYSIS ===
from core.metrics import generate_performance_report, print_report

report = generate_performance_report(
    original_message="HELLO WORLD",
    recovered_message="HELLO WORLD",
    original_audio=audio,
    encoded_audio=encoded,
    confidence=0.98
)

print_report(report)


# === ADVANCED: CUSTOM ENCODER/DECODER ===
from core.encoder import SteganoEncoder
from core.decoder import SteganoDecoder

# Create custom encoder
encoder = SteganoEncoder(
    sr=44100,
    window_size=512,  # Larger window = more robustness
    hop_length=256    # 50% overlap
)

# Encode with custom parameters
encoded, metadata = encoder.encode(audio, "SECRET MESSAGE")

# Create decoder with same parameters
decoder = SteganoDecoder(sr=44100, window_size=512, hop_length=256)

# Decode with sensitivity tuning
message, confidence, metadata = decoder.decode(
    encoded,
    sensitivity=0.5  # 0.0 = very lenient, 1.0 = very strict
)


PARAMETER TUNING
=================

Window Size:
  256  → Faster, lower latency, less frequency resolution
  512  → Balanced (default)
  1024 → Better frequency resolution, more robust to noise

Hop Length (samples):
  64   → 4x overlap, slower but more robust
  128  → 2x overlap, balanced
  256  → 1x (50% overlap), default
  512  → Faster, less robust

Sensitivity (0.0 - 1.0):
  0.3  → Very lenient, recovers more but less accurate
  0.5  → Balanced (default)
  0.7  → Strict, only recovers if very confident
  1.0  → Extremely strict, rarely recovers

Embedding Strength (0.0 - 1.0):
  0.5  → Light, very imperceptible
  0.7  → Balanced
  1.0  → Maximum, most robust but more audible


TROUBLESHOOTING
=================

Problem: "File is not a valid WAV file"
Solution: Ensure file is PCM WAV (16-bit, 44.1/48 kHz)

Problem: Low confidence scores (<50%)
Solution: Lower sensitivity value, or check SNR of audio

Problem: Empty decoded message
Solution: Check window_size and hop_length match encoding

Problem: ImportError for streamlit
Solution: pip install streamlit>=1.28.0

Problem: Slow encoding/decoding
Solution: Use smaller window_size (256) or fewer samples

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
  streamlit run app.py                → Web app

See QUICK_REFERENCE.md for complete examples!
""")
