"""
Audio Steganography - Streamlit Web Application
Complete UI for encoding, decoding, and noise testing of hidden messages in audio.
"""

import streamlit as st
import numpy as np
import io
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Audio Steganography",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎵 Audio Steganography System")

st.markdown("""
## STFT-Based Audio Steganography

Hide secret alphanumeric messages inside audio files using frequency domain manipulation 
with phase modulation and redundancy error correction.

---

### 🎯 System Features

**Encoding:**
- STFT (Short-Time Fourier Transform) for frequency analysis
- Phase modulation (±π/4 for 0, ±π/2 for 1)
- 3x redundancy for robust recovery
- 32-bit message length header

**Decoding:**
- Correlation-based phase detection
- Majority voting (3-bit → 1-bit recovery)
- Automatic message length extraction
- Confidence scoring

**Robustness Testing:**
- Gaussian noise simulation
- White noise addition
- MP3-like compression artifacts
- Pitch and time scaling

---

### 📊 Key Advantages

✅ **Robust against noise** - 3x redundancy handles corrupted bits  
✅ **Imperceptible** - Phase changes don't affect audio quality significantly  
✅ **High capacity** - Can hide meaningful messages in seconds of audio  
✅ **Deterministic** - Same message always decodes the same way  
✅ **No encryption needed** - Uses signal processing only

---

### 🚀 Quick Start

Use the **sidebar navigation** to:

1. **🔒 Encoding** - Hide a message in WAV audio
2. **🔓 Decoding** - Extract message from encoded audio  
3. **🔊 Noise Testing** - Test robustness against noise

---

### ⚙️ Technical Specifications

**Algorithm:**
- **Method**: STFT + Phase Modulation + Redundancy
- **Transform**: scipy.signal.stft (512-sample windows, 50% overlap)
- **Embedding**: Phase-based (magnitude-preserving)
- **Error Correction**: Majority voting (3-repetition code)
- **Capacity**: ~20-50 bits per second (depending on audio)

**Audio Format:**
- **Type**: WAV (uncompressed PCM)
- **Channels**: Mono or Stereo
- **Sample Rate**: 44.1 kHz or 48 kHz
- **Bit Depth**: 16-bit

**Message Format:**
- **Character Set**: A-Z, 0-9, spaces
- **Max Length**: 1000 characters
- **Encoding**: ASCII + 32-bit length header

---

### 📖 Educational Context

This is a university DSP assignment demonstrating:
- Fourier analysis and STFT
- Signal processing for information hiding
- Digital signal modulation techniques
- Error correction codes (majority voting)
- Audio signal processing with NumPy/SciPy

""")

st.divider()

st.info("""
💡 **How it works:**
1. Your message is converted to binary with a header specifying message length
2. Each bit is repeated 3 times for redundancy
3. Bits are embedded in random frequency bins using phase shifts
4. The modified audio is reconstructed and sounds almost identical to the original
5. Only knowing the algorithm and the original audio allows extraction
""")

# Sidebar info
st.sidebar.markdown("""
---
### 📌 Navigation

Select a page from the dropdown menu to:

- **Encoding** - Embed messages
- **Decoding** - Extract messages
- **Noise Testing** - Verify robustness

### 📚 Resources

- **Audio Input**: Use WAV files only
- **Message**: Alphanumeric text
- **Duration**: Minimum 1 second recommended

### ✅ Tips

- Test with short messages first
- Use high-quality source audio
- Keep audio at moderate volume
- Save encoded files for later decoding
""")
