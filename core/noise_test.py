"""
Audio Steganography - Noise Testing Module
Simulates noise and distortions to validate steganography robustness.
"""

import numpy as np
from typing import Dict
from scipy import signal

def add_gaussian_noise(audio: np.ndarray, snr_db: float) -> np.ndarray:
    """Add Gaussian white noise to audio signal at specified SNR."""
    signal_power = np.mean(audio ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(audio))
    return np.clip(audio + noise, -1.0, 1.0)

def add_white_noise(audio: np.ndarray, snr_db: float) -> np.ndarray:
    """Add uniform white noise to audio signal at specified SNR."""
    signal_power = np.mean(audio ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.uniform(-1, 1, len(audio)) * np.sqrt(noise_power)
    return np.clip(audio + noise, -1.0, 1.0)

def add_mp3_like_compression(audio: np.ndarray, quality: int = 5) -> np.ndarray:
    """Simulate lossy compression-like high-frequency degradation artifacts."""
    order = max(2, 10 - quality)
    sos = signal.butter(order, 100, 'hp', fs=44100, output='sos')
    compressed = signal.sosfilt(sos, audio)
    distortion_factor = (10 - quality) / 10
    compressed += distortion_factor * 0.02 * np.sin(2 * np.pi * compressed)
    return np.clip(compressed, -1.0, 1.0)

def add_low_pass_filter(audio: np.ndarray, cutoff_hz: float = 8000, sr: int = 44100) -> np.ndarray:
    """Apply high-order low-pass filtering to signal."""
    order = 6
    nyquist = sr / 2
    if cutoff_hz >= nyquist:
        return audio
    normalized_cutoff = cutoff_hz / nyquist
    sos = signal.butter(order, normalized_cutoff, 'low', output='sos')
    return signal.sosfilt(sos, audio)

def test_robustness(original_audio: np.ndarray, encoded_audio: np.ndarray, decoder_func, 
                    snr_db: float = 20, noise_type: str = 'gaussian') -> Dict:
    """Test steganography robustness against specific noise channel types."""
    if noise_type == 'gaussian':
        corrupted = add_gaussian_noise(encoded_audio, snr_db)
    elif noise_type == 'white':
        corrupted = add_white_noise(encoded_audio, snr_db)
    elif noise_type == 'compression':
        quality = max(1, 10 - int(snr_db / 4))
        corrupted = add_mp3_like_compression(encoded_audio, quality)
    elif noise_type == 'lpf':
        corrupted = add_low_pass_filter(encoded_audio, cutoff_hz=6000)
    else:
        corrupted = encoded_audio
        
    try:
        msg, confidence, _ = decoder_func(corrupted)
    except:
        msg, confidence = "", 0.0
        
    return {
        'noise_type': noise_type,
        'snr_db': snr_db,
        'recovered_message': msg,
        'success': len(msg) > 0,
        'confidence': confidence
    }

def run_suite(original_audio: np.ndarray, encoded_audio: np.ndarray, decoder_func) -> Dict:
    """Test steganography against multiple default noise scenarios."""
    scenarios = [
        ('Clean', 'gaussian', float('inf')),
        ('Light Noise', 'gaussian', 30),
        ('Moderate Noise', 'gaussian', 20),
        ('Heavy Noise', 'gaussian', 10),
        ('White Noise', 'white', 20),
        ('Compression', 'compression', 20),
        ('Low-Pass Filter', 'lpf', 20),
    ]
    
    all_results = {}
    for scenario_name, noise_type, snr_db in scenarios:
        if snr_db == float('inf'):
            try:
                message, confidence, _ = decoder_func(encoded_audio)
            except:
                message, confidence = "", 0.0
            all_results[scenario_name] = {
                'noise_type': 'none',
                'snr_db': float('inf'),
                'recovered_message': message,
                'success': len(message) > 0,
                'confidence': confidence
            }
        else:
            all_results[scenario_name] = test_robustness(original_audio, encoded_audio, decoder_func, snr_db, noise_type)
            
    return all_results