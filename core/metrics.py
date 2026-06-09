"""
Audio Steganography - Metrics Module
Calculates performance metrics for steganography system.
"""

import numpy as np
from typing import Dict, Tuple

def calculate_bit_error_rate(original_bits: np.ndarray, decoded_bits: np.ndarray) -> float:
    """Calculate Bit Error Rate (BER)."""
    if len(original_bits) != len(decoded_bits):
        min_len = min(len(original_bits), len(decoded_bits))
        original = original_bits[:min_len]
        decoded = decoded_bits[:min_len]
    else:
        original = original_bits
        decoded = decoded_bits
    
    errors = np.sum(original != decoded)
    ber = (errors / len(original)) * 100 if len(original) > 0 else 100
    return float(ber)

def calculate_recovery_rate(original_message: str, recovered_message: str) -> float:
    """Calculate character-level recovery rate between strings."""
    if len(original_message) == 0:
        return 100.0 if len(recovered_message) == 0 else 0.0
    if recovered_message == original_message:
        return 100.0
    
    matches = 0
    for i, char in enumerate(original_message):
        if i < len(recovered_message) and recovered_message[i] == char:
            matches += 1
    return (matches / len(original_message)) * 100

def calculate_audio_quality_metrics(original_audio: np.ndarray, encoded_audio: np.ndarray) -> Dict[str, float]:
    """Calculate audio quality degradation metrics (MSE, PSNR, SNR, Correlation)."""
    min_len = min(len(original_audio), len(encoded_audio))
    original = original_audio[:min_len]
    encoded = encoded_audio[:min_len]
    
    mse = np.mean((original - encoded) ** 2)
    max_val = 1.0
    psnr = 20 * np.log10(max_val / np.sqrt(mse)) if mse > 0 else float('inf')
    
    signal_power = np.mean(original ** 2)
    snr = 10 * np.log10(signal_power / mse) if mse > 0 and signal_power > 0 else float('inf')
    
    correlation = np.correlate(original, encoded, mode='same')[len(original)//2]
    correlation = correlation / (np.sqrt(np.sum(original**2)) * np.sqrt(np.sum(encoded**2)))
    
    from scipy.fft import fft
    
    # Use 1e-5 to clip near-zero values for stable Log-Spectral Distance calculation
    original_fft = np.maximum(np.abs(fft(original)), 1e-5)
    encoded_fft = np.maximum(np.abs(fft(encoded)), 1e-5)
    
    original_log = 20 * np.log10(original_fft)
    encoded_log = 20 * np.log10(encoded_fft)
    
    spectral_distortion = np.sqrt(np.mean((original_log - encoded_log) ** 2))
    
    return {
        'mse': float(mse),
        'psnr': float(psnr),
        'snr': float(snr),
        'correlation': float(correlation),
        'spectral_distortion': float(spectral_distortion)
    }

def calculate_capacity(message_length: int, audio_length: int, sr: int = 44100) -> float:
    """Calculate raw embedding capacity throughput (bits per second)."""
    total_bits = 32 + message_length * 8
    duration = audio_length / sr
    return float(total_bits / duration) if duration > 0 else 0.0

def estimate_capacity_limit(audio_length: int, sr: int = 44100) -> int:
    """Estimate max character limits based on Level-3 subband allocations."""
    # Level 3 DWT reduces the band length by approx 1/8th of original length
    target_band_len = audio_length // 8
    chip_rate = 128
    max_bits = target_band_len // chip_rate
    max_message_chars = (max_bits - 32) // 8
    return max(0, int(max_message_chars))

def generate_performance_report(original_audio: np.ndarray, encoded_audio: np.ndarray, 
                                original_message: str, recovered_message: str, 
                                confidence: float, sr: int = 44100) -> Dict:
    """Compile validation metric suites into a clean report dictionary."""
    quality = calculate_audio_quality_metrics(original_audio, encoded_audio)
    return {
        'original_message': original_message,
        'recovered_message': recovered_message,
        'success': original_message == recovered_message,
        'recovery_rate': calculate_recovery_rate(original_message, recovered_message),
        'decoder_confidence': confidence,
        'audio_quality': quality,
        'capacity_bps': calculate_capacity(len(original_message), len(original_audio), sr)
    }