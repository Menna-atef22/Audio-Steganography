"""
Audio Steganography - DWT + Spread Spectrum Encoder
Embeds secret messages using Discrete Wavelet Transform and Direct Sequence Spread Spectrum.
"""

import numpy as np
import pywt
from typing import Tuple
from core.audio_utils import normalize_audio, validate_message

class SteganoEncoder:
    """DWT and Spread Spectrum based audio steganography encoder."""
    
    def __init__(self, sr: int = 44100, wavelet: str = 'db4', level: int = 3):
        self.sr = sr
        self.wavelet = wavelet
        self.level = level
        self.alpha = 0.02  # Embedding strength (balanced: PSNR > 30 dB + robust decoding)
        self.chip_rate = 128  # Spreading factor (optimized for high robustness and long message capacity)
        self.seed = 42  # Secret key for deterministic PN sequence generation
    
    def _message_to_binary(self, message: str) -> np.ndarray:
        """Convert message string to binary array with a 32-bit size header."""
        message = message.upper()
        ascii_codes = np.array([ord(c) for c in message], dtype=np.uint8)
        
        length = len(message)
        header = np.array([
            (length >> 24) & 0xFF,
            (length >> 16) & 0xFF,
            (length >> 8) & 0xFF,
            length & 0xFF
        ], dtype=np.uint8)
        
        full_data = np.concatenate([header, ascii_codes])
        binary_str = ''.join([format(byte, '08b') for byte in full_data])
        # Map binary 0/1 to bipolar spread spectrum tokens -1 and 1
        binary_array = np.array([1 if b == '1' else -1 for b in binary_str], dtype=np.int8)
        
        return binary_array
    
    def _generate_pn_sequence(self, num_bits: int) -> np.ndarray:
        """Generate Pseudo-Noise sequences for despreading."""
        rng = np.random.RandomState(self.seed)
        return rng.choice([-1, 1], size=(num_bits, self.chip_rate))
    
    def encode(self, audio: np.ndarray, message: str) -> Tuple[np.ndarray, dict]:
        """Embed message into audio using DWT and Spread Spectrum."""
        
        # 0. Validate message before starting
        if not validate_message(message):
            raise ValueError("Invalid message: Must be alphanumeric and max 2000 characters.")
            
        audio = normalize_audio(audio, 0.9)
        binary_message = self._message_to_binary(message)
        num_bits = len(binary_message)
        
        # 1. Generate Spread Spectrum noise signal
        pn_sequences = self._generate_pn_sequence(num_bits)
        spread_signal = (binary_message[:, None] * pn_sequences).flatten()
        
        # 2. Perform Discrete Wavelet Decomposition
        coeffs = pywt.wavedec(audio, self.wavelet, level=self.level)
        target_band = coeffs[0]  # cA3: low-freq approximation (0–5.5 kHz), survives LPF at 6–8 kHz
        
        if len(spread_signal) > len(target_band):
            max_chars = (len(target_band) // self.chip_rate - 32) // 8
            raise ValueError(f"Message too long! Max characters allowed with this chip rate: {max_chars}")
        
        # 3. Additive Spread Spectrum embedding into mid-frequency coefficients
        modified_band = target_band.copy()
        modified_band[:len(spread_signal)] += self.alpha * spread_signal
        coeffs[0] = modified_band
        
        # 4. Reconstruct Audio via IDWT
        encoded_audio = pywt.waverec(coeffs, self.wavelet)
        
        # Adjust boundary alterations from filter banks to original sample length
        if len(encoded_audio) > len(audio):
            encoded_audio = encoded_audio[:len(audio)]
        elif len(encoded_audio) < len(audio):
            encoded_audio = np.pad(encoded_audio, (0, len(audio) - len(encoded_audio)))
            
        encoded_audio = normalize_audio(encoded_audio, 0.9)
        
        metadata = {
            'message_length': len(message),
            'binary_length': num_bits,
            'chip_rate': self.chip_rate,
            'wavelet': self.wavelet,
            'sample_rate': self.sr
        }
        
        return encoded_audio, metadata

def encode_audio(audio: np.ndarray, message: str, sr: int = 44100) -> Tuple[np.ndarray, dict]:
    encoder = SteganoEncoder(sr=sr)
    return encoder.encode(audio, message)