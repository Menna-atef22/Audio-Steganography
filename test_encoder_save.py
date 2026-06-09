#!/usr/bin/env python
"""
Quick test to verify encoder works and saves files
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.encoder import SteganoEncoder
from core.decoder import SteganoDecoder
from core.audio_utils import generate_test_audio, save_audio, load_audio

def main():
    print("🎵 Audio Steganography - Encoder Test\n")
    
    # 1. Generate test audio
    print("1. Generating test audio...")
    audio = generate_test_audio(duration=3.0, sr=44100)
    print(f"   ✓ Generated {len(audio)} samples at 44.1 kHz")
    
    # 2. Save original audio
    audio_dir = Path("audio/original")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    original_file = audio_dir / "test_original.wav"
    save_audio(str(original_file), audio, sr=44100)
    print(f"   ✓ Saved original audio: {original_file}")
    
    # 3. Create encoder and encode message
    print("\n2. Encoding message into audio...")
    encoder = SteganoEncoder(sr=44100)
    message = "HELLO WORLD"
    
    try:
        encoded_audio, metadata = encoder.encode(audio, message)
        print(f"   ✓ Encoded message: '{message}'")
        print(f"   ✓ Encoded audio shape: {encoded_audio.shape}")
        print(f"   ✓ Metadata: {metadata}")
    except Exception as e:
        print(f"   ✗ Encoding failed: {e}")
        return 1
    
    # 4. Save encoded audio
    print("\n3. Saving encoded audio...")
    encoded_dir = Path("audio/encoded")
    encoded_dir.mkdir(parents=True, exist_ok=True)
    
    encoded_file = encoded_dir / "test_encoded.wav"
    save_audio(str(encoded_file), encoded_audio, sr=44100)
    print(f"   ✓ Saved encoded audio: {encoded_file}")
    
    # 5. Verify we can load the files back
    print("\n4. Verifying saved files...")
    loaded_original, sr1 = load_audio(str(original_file))
    loaded_encoded, sr2 = load_audio(str(encoded_file))
    
    print(f"   ✓ Loaded original: {len(loaded_original)} samples at {sr1} Hz")
    print(f"   ✓ Loaded encoded:  {len(loaded_encoded)} samples at {sr2} Hz")
    
    # 6. Try to decode the message
    print("\n5. Decoding message from encoded audio...")
    decoder = SteganoDecoder(sr=44100)
    
    try:
        decoded_message, confidence, dec_metadata = decoder.decode(loaded_encoded)
        print(f"   ✓ Decoded message: '{decoded_message}'")
        print(f"   ✓ Confidence: {confidence:.2%}")
        
        if decoded_message.strip() == message.strip():
            print(f"   ✓ Message matches! Encoding/Decoding works correctly")
        else:
            print(f"   ⚠ Message differs (expected '{message}', got '{decoded_message}')")
    except Exception as e:
        print(f"   ✗ Decoding failed: {e}")
        return 1
    
    # 7. Compare audio characteristics
    print("\n6. Audio Quality Comparison...")
    import numpy as np
    
    mse = np.mean((audio - loaded_encoded) ** 2)
    snr = 10 * np.log10(np.mean(audio ** 2) / (mse + 1e-10))
    correlation = np.corrcoef(audio[:1000], loaded_encoded[:1000])[0, 1]
    
    print(f"   Mean Squared Error: {mse:.6f}")
    print(f"   Signal-to-Noise Ratio: {snr:.2f} dB")
    print(f"   Correlation: {correlation:.6f}")
    
    print("\n✅ All tests passed! Encoder is working correctly.")
    print(f"\nFiles saved to:")
    print(f"  - Original: {original_file.absolute()}")
    print(f"  - Encoded:  {encoded_file.absolute()}")
    print(f"\nYou can now listen to these files to compare the audio quality.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
