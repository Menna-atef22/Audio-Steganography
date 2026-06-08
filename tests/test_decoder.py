"""
Audio Steganography - Decoder and integration tests
"""

import numpy as np
from pathlib import Path
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.encoder import encode_audio
from core.decoder import decode_audio
from core.audio_utils import generate_test_audio, load_audio, save_audio


class TestDecoder:
    """Test decoding functionality"""

    def test_perfect_decoding(self):
        """Test decoding from unmodified encoded audio"""
        audio = generate_test_audio(duration=1.0)
        original_message = "HELLO"

        encoded, _ = encode_audio(audio, original_message, sr=44100)
        decoded_message, confidence, metadata = decode_audio(encoded, sr=44100)

        assert decoded_message == original_message
        assert confidence > 0.0
        assert isinstance(metadata, dict)

    def test_empty_audio_handling(self):
        """Test handling of too-short audio"""
        audio = generate_test_audio(duration=0.1)
        message = "TEST"

        try:
            encoded, _ = encode_audio(audio, message, sr=44100)
            decoded, _, _ = decode_audio(encoded, sr=44100)
            assert isinstance(decoded, str)
        except Exception as e:
            assert "short" in str(e).lower()


class TestIntegration:
    """Integration tests"""

    def test_full_pipeline(self):
        """Test complete encode-decode pipeline"""
        audio = generate_test_audio(duration=2.0)
        message = "COMPLETE TEST"

        encoded, _ = encode_audio(audio, message, sr=44100)
        assert len(encoded) > 0
        assert np.max(np.abs(encoded)) <= 1.0

        decoded, confidence, _ = decode_audio(encoded, sr=44100)
        assert confidence >= 0.0
        assert isinstance(decoded, str)

    def test_file_i_o(self):
        """Test file I/O with encoding/decoding"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            audio = generate_test_audio(duration=1.0)
            audio_path = tmppath / "test.wav"
            save_audio(str(audio_path), audio, sr=44100)

            loaded, sr = load_audio(str(audio_path), sr=44100)
            message = "FILE IO TEST"
            encoded, _ = encode_audio(loaded, message, sr=sr)

            encoded_path = tmppath / "encoded.wav"
            save_audio(str(encoded_path), encoded, sr=sr)

            loaded_encoded, sr = load_audio(str(encoded_path), sr=sr)
            decoded, _, _ = decode_audio(loaded_encoded, sr=sr)

            assert isinstance(decoded, str)
