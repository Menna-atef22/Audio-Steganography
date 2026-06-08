"""
Audio Steganography - Encoder and utility tests
"""

import numpy as np
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.encoder import SteganoEncoder, encode_audio
from core.decoder import decode_audio
from core.audio_utils import (
    generate_test_audio, normalize_audio, validate_message
)
from core.noise_test import add_gaussian_noise, add_white_noise
from core.metrics import calculate_recovery_rate, generate_performance_report


class TestAudioUtils:
    """Test audio utilities"""

    def test_generate_test_audio(self):
        """Test test audio generation"""
        audio = generate_test_audio(duration=1.0, sr=44100)
        assert len(audio) == 44100
        assert np.max(np.abs(audio)) <= 1.0

    def test_normalize_audio(self):
        """Test audio normalization"""
        audio = np.random.randn(1000) * 2.0  # Unnormalized
        normalized = normalize_audio(audio, 0.9)
        assert np.max(np.abs(normalized)) <= 0.9

    def test_validate_message(self):
        """Test message validation"""
        assert validate_message("HELLO")
        assert validate_message("HELLO WORLD 123")
        assert validate_message("A")
        assert not validate_message("")
        assert not validate_message("Hello@World")  # Special char


class TestEncoder:
    """Test encoding functionality"""

    def test_basic_encoding(self):
        """Test basic message encoding"""
        audio = generate_test_audio(duration=1.0)
        message = "HELLO"

        encoder = SteganoEncoder(sr=44100)
        encoded, metadata = encoder.encode(audio, message)

        assert len(encoded) <= len(audio) * 1.1  # Slight expansion allowed
        assert metadata["message_length"] == 5
        assert metadata["binary_length"] == 40  # 5 chars * 8 bits + 32 bit header

    def test_encoding_output_quality(self):
        """Test that encoded audio quality is high"""
        audio = generate_test_audio(duration=1.0)
        message = "TEST"

        encoded, _ = encode_audio(audio, message, sr=44100)

        assert np.max(np.abs(encoded)) <= 1.0
        assert np.min(encoded) >= -1.0

    def test_encoding_different_messages(self):
        """Test encoding of different messages"""
        audio = generate_test_audio(duration=1.0)

        messages = ["A", "TEST", "HELLO WORLD", "ABC123"]

        for msg in messages:
            encoded, metadata = encode_audio(audio, msg)
            assert metadata["message_length"] == len(msg)
            assert len(encoded) > 0


class TestNoise:
    """Test noise robustness"""

    def test_gaussian_noise(self):
        """Test Gaussian noise addition"""
        audio = generate_test_audio(duration=1.0)
        snr_db = 20

        noisy = add_gaussian_noise(audio, snr_db)

        assert len(noisy) == len(audio)
        assert np.max(np.abs(noisy)) <= 1.0

    def test_white_noise(self):
        """Test white noise addition"""
        audio = generate_test_audio(duration=1.0)
        snr_db = 20

        noisy = add_white_noise(audio, snr_db)

        assert len(noisy) == len(audio)
        assert np.max(np.abs(noisy)) <= 1.0

    def test_robustness_at_high_snr(self):
        """Test robustness at high SNR (clean audio)"""
        audio = generate_test_audio(duration=1.0)
        message = "TEST"

        encoded, _ = encode_audio(audio, message)
        noisy = add_gaussian_noise(encoded, snr_db=30)
        decoded_message, confidence, _ = decode_audio(noisy, sr=44100)

        assert decoded_message == message
        assert confidence >= 0.0

    def test_robustness_at_low_snr(self):
        """Test robustness degrades at low SNR"""
        audio = generate_test_audio(duration=1.0)
        message = "TEST"

        encoded, _ = encode_audio(audio, message)
        noisy_high_snr = add_gaussian_noise(encoded, snr_db=30)
        noisy_low_snr = add_gaussian_noise(encoded, snr_db=10)

        decoded_high, confidence_high, _ = decode_audio(noisy_high_snr, sr=44100)
        decoded_low, confidence_low, _ = decode_audio(noisy_low_snr, sr=44100)

        assert len(noisy_high_snr) == len(encoded)
        assert len(noisy_low_snr) == len(encoded)
        assert decoded_high == message
        assert isinstance(decoded_low, str)
        assert confidence_high >= confidence_low


class TestMetrics:
    """Test performance metrics"""

    def test_recovery_rate(self):
        """Test recovery rate calculation"""
        original = "HELLO"

        assert calculate_recovery_rate(original, original) == 100.0
        partial = "HEL"
        rate = calculate_recovery_rate(original, partial)
        assert 0 < rate < 100
        assert calculate_recovery_rate(original, "") == 0.0

    def test_performance_report(self):
        """Test performance report generation"""
        audio = generate_test_audio(duration=1.0)
        message = "TEST"

        encoded, _ = encode_audio(audio, message)
        decoded = message
        confidence = 0.95

        report = generate_performance_report(
            message, decoded, audio, encoded, confidence
        )

        assert "success" in report
        assert "recovery_rate" in report
        assert "audio_quality" in report
