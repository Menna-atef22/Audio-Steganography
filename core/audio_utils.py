"""
Audio Steganography - Core Utilities
Handles audio file I/O, preprocessing, and format conversions
"""

import numpy as np
import soundfile as sf
import hashlib
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


def load_audio(filepath: str, sr: int = 44100) -> Tuple[np.ndarray, int]:
    """Load audio file and resample if necessary."""
    try:
        audio, original_sr = sf.read(filepath)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        if original_sr != sr:
            from scipy import signal
            num_samples = int(len(audio) * sr / original_sr)
            audio = signal.resample(audio, num_samples)
        return audio, sr
    except FileNotFoundError:
        raise FileNotFoundError(f"Audio file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error loading audio file: {str(e)}")


def save_audio(filepath: str, audio: np.ndarray, sr: int = 44100) -> None:
    """Save audio signal to file safely without clipping."""
    try:
        audio = np.clip(audio, -1.0, 1.0)
        sf.write(filepath, audio, sr, subtype='PCM_16')
    except Exception as e:
        raise ValueError(f"Error saving audio file: {str(e)}")


def normalize_audio(audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
    """Normalize audio to target level to prevent clipping."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * target_level
    return audio


def get_audio_duration(audio: np.ndarray, sr: int) -> float:
    """Get audio duration in seconds."""
    return len(audio) / sr


def pad_audio(audio: np.ndarray, target_length: int, mode: str = 'zero') -> np.ndarray:
    """Pad audio to target length."""
    if len(audio) >= target_length:
        return audio[:target_length]
    if mode == 'zero':
        return np.pad(audio, (0, target_length - len(audio)), mode='constant')
    elif mode == 'repeat':
        num_repeats = (target_length // len(audio)) + 1
        padded = np.tile(audio, num_repeats)
        return padded[:target_length]
    else:
        raise ValueError(f"Unknown padding mode: {mode}")


def generate_sine_wave(frequency: float, duration: float, sr: int = 44100, amplitude: float = 0.5) -> np.ndarray:
    """Generate a pure sine wave signal (useful for integration tests)."""
    t = np.arange(0, duration, 1/sr)
    return amplitude * np.sin(2 * np.pi * frequency * t)


def generate_test_audio(duration: float = 1.0, sr: int = 44100) -> np.ndarray:
    """Generate a comprehensive test audio signal mimicking natural audio components."""
    audio = generate_sine_wave(440, duration, sr, 0.3)
    audio += generate_sine_wave(880, duration, sr, 0.2)
    audio += generate_sine_wave(220, duration, sr, 0.15)
    t = np.arange(0, duration, 1/sr)
    modulation = 0.5 * np.sin(2 * np.pi * 2 * t)
    audio = audio * (1 + 0.3 * modulation)
    return normalize_audio(audio, 0.8)


def get_audio_hash(audio: np.ndarray) -> str:
    """Generate a deterministic MD5 hash of the raw audio signal values."""
    return hashlib.md5(audio.tobytes()).hexdigest()


def validate_message(message: str) -> bool:
    """Validate that the message is not empty and conforms to text rules."""
    if not message:
        return False
    return all(c.isalnum() or c.isspace() for c in message)