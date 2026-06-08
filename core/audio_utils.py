"""
Audio Steganography - Core Utilities
Handles audio file I/O, preprocessing, and format conversions
"""

import numpy as np
import soundfile as sf
from typing import Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


def load_audio(filepath: str, sr: int = 44100) -> Tuple[np.ndarray, int]:
    """
    Load audio file and resample if necessary.
    
    Args:
        filepath: Path to audio file
        sr: Target sample rate (default 44100 Hz)
    
    Returns:
        audio: Audio signal as numpy array (mono)
        sample_rate: Sample rate of audio
    
    Raises:
        FileNotFoundError: If audio file not found
        ValueError: If audio file is invalid
    """
    try:
        audio, original_sr = sf.read(filepath)
        
        # Convert stereo to mono if needed
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        
        # Resample if necessary
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
    """
    Save audio signal to file.
    
    Args:
        filepath: Output file path
        audio: Audio signal as numpy array
        sr: Sample rate (default 44100 Hz)
    
    Raises:
        ValueError: If audio data is invalid
    """
    try:
        # Ensure audio is in valid range
        audio = np.clip(audio, -1.0, 1.0)
        sf.write(filepath, audio, sr, subtype='PCM_16')
    except Exception as e:
        raise ValueError(f"Error saving audio file: {str(e)}")


def normalize_audio(audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
    """
    Normalize audio to target level to prevent clipping.
    
    Args:
        audio: Audio signal
        target_level: Target maximum amplitude (default 0.9)
    
    Returns:
        Normalized audio signal
    """
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * target_level
    return audio


def get_audio_duration(audio: np.ndarray, sr: int) -> float:
    """
    Get audio duration in seconds.
    
    Args:
        audio: Audio signal
        sr: Sample rate
    
    Returns:
        Duration in seconds
    """
    return len(audio) / sr


def pad_audio(audio: np.ndarray, target_length: int, mode: str = 'zero') -> np.ndarray:
    """
    Pad audio to target length.
    
    Args:
        audio: Audio signal
        target_length: Target length in samples
        mode: 'zero' (zero-padding) or 'repeat' (repeat signal)
    
    Returns:
        Padded audio signal
    """
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


def generate_sine_wave(frequency: float, duration: float, sr: int = 44100, 
                       amplitude: float = 0.5) -> np.ndarray:
    """
    Generate a sine wave signal (useful for testing).
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sr: Sample rate (default 44100 Hz)
        amplitude: Amplitude (default 0.5)
    
    Returns:
        Sine wave signal
    """
    t = np.arange(0, duration, 1/sr)
    return amplitude * np.sin(2 * np.pi * frequency * t)


def generate_test_audio(duration: float = 1.0, sr: int = 44100) -> np.ndarray:
    """
    Generate a simple test audio signal (combination of sine waves).
    
    Args:
        duration: Duration in seconds (default 1.0)
        sr: Sample rate (default 44100 Hz)
    
    Returns:
        Test audio signal (mono)
    """
    # Combination of frequencies to simulate natural audio
    audio = generate_sine_wave(440, duration, sr, 0.3)      # A4
    audio += generate_sine_wave(880, duration, sr, 0.2)     # A5
    audio += generate_sine_wave(220, duration, sr, 0.15)    # A3
    
    # Add slight modulation
    t = np.arange(0, duration, 1/sr)
    modulation = 0.5 * np.sin(2 * np.pi * 2 * t)
    audio = audio * (1 + 0.3 * modulation)
    
    return normalize_audio(audio, 0.8)


def get_audio_hash(audio: np.ndarray, max_val: int = 2**31 - 1) -> int:
    """
    Generate deterministic hash of audio signal for seeding PRNG.
    
    Args:
        audio: Audio signal
        max_val: Maximum hash value
    
    Returns:
        Integer hash value
    """
    # Use FFT-based hash for speed
    from scipy.fftpack import fft
    fft_result = np.abs(fft(audio[:min(len(audio), 44100)]))
    hash_val = int(np.sum(fft_result * np.arange(len(fft_result)))) % max_val
    return max(1, hash_val)  # Ensure non-zero


def get_signal_statistics(audio: np.ndarray) -> dict:
    """
    Calculate audio signal statistics.
    
    Args:
        audio: Audio signal
    
    Returns:
        Dictionary with statistics (rms, peak, mean, std)
    """
    return {
        'rms': float(np.sqrt(np.mean(audio**2))),
        'peak': float(np.max(np.abs(audio))),
        'mean': float(np.mean(audio)),
        'std': float(np.std(audio)),
        'min': float(np.min(audio)),
        'max': float(np.max(audio))
    }


def calculate_snr(original: np.ndarray, corrupted: np.ndarray) -> float:
    """
    Calculate Signal-to-Noise Ratio (SNR) in dB.
    
    Args:
        original: Original signal
        corrupted: Signal with noise
    
    Returns:
        SNR in dB
    """
    noise = original - corrupted
    signal_power = np.mean(original**2)
    noise_power = np.mean(noise**2)
    
    if noise_power == 0:
        return float('inf')
    
    snr_db = 10 * np.log10(signal_power / noise_power)
    return float(snr_db)


def validate_message(message: str) -> bool:
    """
    Validate message (must be alphanumeric).
    
    Args:
        message: Message string
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(message, str):
        return False
    if len(message) == 0 or len(message) > 1000:
        return False
    # Allow alphanumeric and spaces only
    return all(c.isalnum() or c == ' ' for c in message)
