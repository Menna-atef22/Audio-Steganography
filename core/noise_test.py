"""
Audio Steganography - Noise Testing Module
Simulates noise and distortions to test steganography robustness.
"""

import numpy as np
from typing import Tuple, Dict
from scipy import signal


def add_gaussian_noise(audio: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Add Gaussian white noise to audio signal at specified SNR.
    
    Args:
        audio: Audio signal
        snr_db: Signal-to-Noise Ratio in dB
    
    Returns:
        Noisy audio signal
    """
    # Calculate signal power
    signal_power = np.mean(audio ** 2)
    
    # Calculate noise power from SNR
    # SNR = 10 * log10(signal_power / noise_power)
    noise_power = signal_power / (10 ** (snr_db / 10))
    
    # Generate Gaussian noise
    noise = np.random.normal(0, np.sqrt(noise_power), len(audio))
    
    # Add noise to signal
    noisy_audio = audio + noise
    
    # Clip to prevent overflow
    noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
    
    return noisy_audio


def add_white_noise(audio: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Add white noise to audio signal at specified SNR.
    
    Args:
        audio: Audio signal
        snr_db: Signal-to-Noise Ratio in dB
    
    Returns:
        Noisy audio signal
    """
    # For white noise, use similar approach as Gaussian
    signal_power = np.mean(audio ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    
    # Generate white noise (uniform distribution)
    noise = np.random.uniform(-1, 1, len(audio)) * np.sqrt(noise_power)
    
    # Add noise to signal
    noisy_audio = audio + noise
    
    # Clip to prevent overflow
    noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
    
    return noisy_audio


def add_mp3_like_compression(audio: np.ndarray, quality: int = 5) -> np.ndarray:
    """
    Simulate lossy compression-like distortion.
    
    Args:
        audio: Audio signal
        quality: Quality level (1-10, lower = more distortion)
    
    Returns:
        Compressed audio signal
    """
    # Apply high-pass filter to simulate compression artifacts
    # This is a crude simulation of MP3-like compression
    
    # Calculate order based on quality
    order = max(2, 10 - quality)
    
    # Design high-pass filter
    sos = signal.butter(order, 100, 'hp', fs=44100, output='sos')
    
    # Apply filter
    compressed = signal.sosfilt(sos, audio)
    
    # Add some harmonic distortion
    distortion_factor = (10 - quality) / 10
    compressed = compressed + distortion_factor * 0.1 * np.sin(2 * np.pi * compressed)
    
    # Clip
    compressed = np.clip(compressed, -1.0, 1.0)
    
    return compressed


def add_time_scaling(audio: np.ndarray, factor: float) -> np.ndarray:
    """
    Apply time-scale stretching (pitch preservation).
    
    Args:
        audio: Audio signal
        factor: Time scaling factor (0.95-1.05)
    
    Returns:
        Time-scaled audio signal
    """
    if factor <= 0:
        return audio
    
    # Simple linear interpolation for time scaling
    original_length = len(audio)
    new_length = int(original_length / factor)
    
    # Create interpolation indices
    original_indices = np.arange(original_length)
    new_indices = np.linspace(0, original_length - 1, new_length)
    
    # Interpolate
    scaled_audio = np.interp(new_indices, original_indices, audio)
    
    # Pad or trim to original length
    if len(scaled_audio) < original_length:
        scaled_audio = np.pad(scaled_audio, (0, original_length - len(scaled_audio)))
    else:
        scaled_audio = scaled_audio[:original_length]
    
    return scaled_audio


def add_pitch_shift(audio: np.ndarray, semitones: float) -> np.ndarray:
    """
    Apply pitch shifting.
    
    Args:
        audio: Audio signal
        semitones: Number of semitones to shift (-12 to +12)
    
    Returns:
        Pitch-shifted audio signal
    """
    # Calculate frequency ratio from semitones
    ratio = 2 ** (semitones / 12)
    
    # Apply time-scaling
    scaled = add_time_scaling(audio, 1.0 / ratio)
    
    return scaled


def add_low_pass_filter(audio: np.ndarray, cutoff_hz: float = 8000, 
                        sr: int = 44100) -> np.ndarray:
    """
    Apply low-pass filtering.
    
    Args:
        audio: Audio signal
        cutoff_hz: Cutoff frequency in Hz
        sr: Sample rate
    
    Returns:
        Filtered audio signal
    """
    # Design Butterworth low-pass filter
    order = 6
    nyquist = sr / 2
    
    if cutoff_hz >= nyquist:
        return audio
    
    normalized_cutoff = cutoff_hz / nyquist
    sos = signal.butter(order, normalized_cutoff, 'low', output='sos')
    
    # Apply filter
    filtered = signal.sosfilt(sos, audio)
    
    return filtered


def test_robustness(original_audio: np.ndarray, encoded_audio: np.ndarray,
                   decoder_func, snr_db: float = 20, 
                   noise_type: str = 'gaussian') -> Dict:
    """
    Test steganography robustness against noise.
    
    Args:
        original_audio: Original audio signal
        encoded_audio: Encoded audio with message
        decoder_func: Decoding function to call
        snr_db: Signal-to-Noise Ratio in dB
        noise_type: Type of noise ('gaussian', 'white', 'compression', 'lpf')
    
    Returns:
        Dictionary with test results
    """
    # Apply noise/distortion
    if noise_type == 'gaussian':
        corrupted = add_gaussian_noise(encoded_audio, snr_db)
    elif noise_type == 'white':
        corrupted = add_white_noise(encoded_audio, snr_db)
    elif noise_type == 'compression':
        quality = max(1, 10 - int(snr_db / 4))
        corrupted = add_mp3_like_compression(encoded_audio, quality)
    elif noise_type == 'lpf':
        cutoff = 4000 + (snr_db - 10) * 400  # Higher SNR = higher cutoff
        corrupted = add_low_pass_filter(encoded_audio, cutoff)
    else:
        corrupted = encoded_audio
    
    # Try to decode
    try:
        message, confidence, metadata = decoder_func(corrupted)
    except:
        message = ""
        confidence = 0.0
        metadata = {}
    
    # Calculate SNR of corrupted signal
    noise = corrupted - encoded_audio
    signal_power = np.mean(encoded_audio ** 2)
    noise_power = np.mean(noise ** 2)
    
    if noise_power > 0:
        measured_snr = 10 * np.log10(signal_power / noise_power)
    else:
        measured_snr = float('inf')
    
    # Calculate BER (Bit Error Rate) - simplified estimate
    # This would require knowing the original message
    ber = 1.0 - confidence if message == "" else 0.0
    
    results = {
        'noise_type': noise_type,
        'snr_db': snr_db,
        'measured_snr': measured_snr,
        'recovered_message': message,
        'success': len(message) > 0,
        'confidence': confidence,
        'ber': ber
    }
    
    return results


def test_multiple_scenarios(original_audio: np.ndarray, encoded_audio: np.ndarray,
                           decoder_func) -> Dict[str, list]:
    """
    Test steganography against multiple noise scenarios.
    
    Args:
        original_audio: Original audio signal
        encoded_audio: Encoded audio with message
        decoder_func: Decoding function to call
    
    Returns:
        Dictionary with results for each scenario
    """
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
            # No noise test
            try:
                message, confidence, metadata = decoder_func(encoded_audio)
            except:
                message = ""
                confidence = 0.0
            
            all_results[scenario_name] = {
                'noise_type': 'none',
                'snr_db': float('inf'),
                'recovered_message': message,
                'success': len(message) > 0,
                'confidence': confidence
            }
        else:
            result = test_robustness(original_audio, encoded_audio, 
                                    decoder_func, snr_db, noise_type)
            all_results[scenario_name] = result
    
    return all_results
