"""
Audio Steganography - Metrics Module
Calculates performance metrics for steganography system.
"""

import numpy as np
from typing import Dict, Tuple


def calculate_bit_error_rate(original_bits: np.ndarray, decoded_bits: np.ndarray) -> float:
    """
    Calculate Bit Error Rate (BER).
    
    Args:
        original_bits: Original binary message
        decoded_bits: Decoded binary message
    
    Returns:
        BER as a percentage (0-100)
    """
    if len(original_bits) != len(decoded_bits):
        # Pad shorter array
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
    """
    Calculate message recovery rate (percentage of characters successfully recovered).
    
    Args:
        original_message: Original secret message
        recovered_message: Recovered message
    
    Returns:
        Recovery rate as percentage (0-100)
    """
    if len(original_message) == 0:
        return 100.0 if len(recovered_message) == 0 else 0.0
    
    if recovered_message == original_message:
        return 100.0
    
    # Calculate character-level match
    matches = 0
    for i, char in enumerate(original_message):
        if i < len(recovered_message) and recovered_message[i] == char:
            matches += 1
    
    return (matches / len(original_message)) * 100


def calculate_audio_quality_metrics(original_audio: np.ndarray, 
                                   encoded_audio: np.ndarray) -> Dict[str, float]:
    """
    Calculate audio quality degradation metrics.
    
    Args:
        original_audio: Original audio signal
        encoded_audio: Encoded audio signal
    
    Returns:
        Dictionary with quality metrics
    """
    # Ensure same length
    min_len = min(len(original_audio), len(encoded_audio))
    original = original_audio[:min_len]
    encoded = encoded_audio[:min_len]
    
    # Mean Squared Error (MSE)
    mse = np.mean((original - encoded) ** 2)
    
    # Peak Signal-to-Noise Ratio (PSNR)
    max_val = 1.0  # Audio normalized to [-1, 1]
    if mse > 0:
        psnr = 20 * np.log10(max_val / np.sqrt(mse))
    else:
        psnr = float('inf')
    
    # Signal-to-Noise Ratio (SNR)
    signal_power = np.mean(original ** 2)
    noise_power = mse
    
    if noise_power > 0 and signal_power > 0:
        snr = 10 * np.log10(signal_power / noise_power)
    else:
        snr = float('inf')
    
    # Normalized cross-correlation
    correlation = np.correlate(original, encoded, mode='same')[len(original)//2]
    correlation = correlation / (np.sqrt(np.sum(original**2)) * np.sqrt(np.sum(encoded**2)))
    
    # Spectral distortion
    from scipy import signal as sp_signal
    from scipy.fft import fft
    
    original_fft = np.abs(fft(original))
    encoded_fft = np.abs(fft(encoded))
    
    # Avoid division by zero
    original_fft = np.maximum(original_fft, 1e-10)
    encoded_fft = np.maximum(encoded_fft, 1e-10)
    
    spectral_distortion = np.mean((20 * np.log10(original_fft / encoded_fft)) ** 2) ** 0.5
    
    return {
        'mse': float(mse),
        'psnr': float(psnr),
        'snr': float(snr),
        'correlation': float(correlation),
        'spectral_distortion': float(spectral_distortion)
    }


def calculate_capacity(message_length: int, audio_length: int, sr: int = 44100) -> float:
    """
    Calculate steganography capacity (bits per second).
    
    Args:
        message_length: Length of message in characters
        audio_length: Length of audio in samples
        sr: Sample rate in Hz
    
    Returns:
        Capacity in bits per second
    """
    # Each character = 8 bits, plus 32-bit header
    total_bits = 32 + message_length * 8
    
    # With 3x redundancy
    total_bits_redundant = total_bits * 3
    
    duration = audio_length / sr
    
    if duration > 0:
        capacity_bps = total_bits_redundant / duration
    else:
        capacity_bps = 0
    
    return float(capacity_bps)


def estimate_capacity_limit(audio_length: int, sr: int = 44100) -> int:
    """
    Estimate maximum message length that can be embedded.
    
    Args:
        audio_length: Length of audio in samples
        sr: Sample rate in Hz
    
    Returns:
        Maximum message length in characters
    """
    # STFT parameters
    window_size = 512
    hop_length = 256
    
    # Number of STFT frames
    num_frames = (audio_length - window_size) // hop_length + 1
    
    # Bits per frame (conservative estimate)
    bits_per_frame = 2
    
    # Total bits available
    total_bits = num_frames * bits_per_frame
    
    # Account for redundancy and header
    # Header = 32 bits, each character = 8 bits, redundancy = 3x
    # total_bits = (32 + message_chars * 8) * 3
    # total_bits / 3 = 32 + message_chars * 8
    # message_chars = (total_bits / 3 - 32) / 8
    
    max_message_chars = int((total_bits / 3 - 32) / 8)
    
    return max(0, max_message_chars)


def generate_performance_report(original_message: str, 
                               recovered_message: str,
                               original_audio: np.ndarray,
                               encoded_audio: np.ndarray,
                               confidence: float) -> Dict:
    """
    Generate comprehensive performance report.
    
    Args:
        original_message: Original secret message
        recovered_message: Recovered message
        original_audio: Original audio
        encoded_audio: Encoded audio
        confidence: Decoder confidence score
    
    Returns:
        Dictionary with comprehensive metrics
    """
    # Message recovery
    recovery_rate = calculate_recovery_rate(original_message, recovered_message)
    
    # Audio quality
    quality_metrics = calculate_audio_quality_metrics(original_audio, encoded_audio)
    
    # Capacity
    capacity = calculate_capacity(len(original_message), len(original_audio))
    
    # Overall success
    success = recovered_message == original_message
    
    report = {
        'original_message': original_message,
        'recovered_message': recovered_message,
        'success': success,
        'recovery_rate': recovery_rate,
        'decoder_confidence': confidence,
        'audio_quality': quality_metrics,
        'capacity_bps': capacity,
        'mse': quality_metrics['mse'],
        'snr_db': quality_metrics['snr'],
        'psnr_db': quality_metrics['psnr']
    }
    
    return report


def print_report(report: Dict) -> str:
    """
    Format performance report as human-readable string.
    
    Args:
        report: Report dictionary
    
    Returns:
        Formatted report string
    """
    lines = [
        "=" * 60,
        "Audio Steganography Performance Report",
        "=" * 60,
        "",
        f"Original Message:  '{report['original_message']}'",
        f"Recovered Message: '{report['recovered_message']}'",
        f"Success:           {report['success']}",
        "",
        "Recovery Metrics:",
        f"  Recovery Rate:      {report['recovery_rate']:.2f}%",
        f"  Decoder Confidence: {report['decoder_confidence']:.4f}",
        "",
        "Audio Quality Metrics:",
        f"  MSE:                  {report['audio_quality']['mse']:.6f}",
        f"  SNR:                  {report['audio_quality']['snr']:.2f} dB",
        f"  PSNR:                 {report['audio_quality']['psnr']:.2f} dB",
        f"  Correlation:          {report['audio_quality']['correlation']:.4f}",
        f"  Spectral Distortion:  {report['audio_quality']['spectral_distortion']:.4f}",
        "",
        "Capacity:",
        f"  Bits per Second: {report['capacity_bps']:.2f} bps",
        "",
        "=" * 60
    ]
    
    return '\n'.join(lines)
