"""
Audio Steganography - DWT + Spread Spectrum Decoder
Extracts messages using Wavelet decomposition and cross-correlation.
"""

import numpy as np
import pywt
from typing import Tuple
from core.audio_utils import normalize_audio

class SteganoDecoder:
    """DWT and Spread Spectrum based audio steganography decoder."""
    
    def __init__(self, sr: int = 44100, wavelet: str = 'db4', level: int = 3):
        self.sr = sr
        self.wavelet = wavelet
        self.level = level
        self.chip_rate = 128
        self.seed = 42
        self.alpha_estimate = 0.02  # Must match encoder alpha for accurate confidence
    
    def _generate_pn_sequence(self, num_bits: int) -> np.ndarray:
        rng = np.random.RandomState(self.seed)
        return rng.choice([-1, 1], size=(num_bits, self.chip_rate))
    
    def _binary_to_message(self, extracted_bits: np.ndarray) -> Tuple[str, bool]:
        """Convert extracted bipolar arrays back into structured text strings."""
        binary_array = np.array([1 if b > 0 else 0 for b in extracted_bits], dtype=np.uint8)
        
        if len(binary_array) < 32:
            return "", False
            
        header_bits = binary_array[:32]
        length = 0
        for i in range(4):
            byte_bits = header_bits[i*8:(i+1)*8]
            byte_val = int(''.join([str(b) for b in byte_bits]), 2)
            length = (length << 8) | byte_val
            
        if length <= 0 or length > 2000 or len(binary_array) < 32 + length * 8:
            return "", False
            
        message_bits = binary_array[32:32 + length * 8]
        
        try:
            message_chars = []
            for i in range(length):
                char_bits = message_bits[i*8:(i+1)*8]
                char_val = int(''.join([str(b) for b in char_bits]), 2)
                if 32 <= char_val <= 126:
                    message_chars.append(chr(char_val))
                else:
                    return "", False
            return ''.join(message_chars), True
        except:
            return "", False

    def decode(self, audio: np.ndarray, sensitivity: float = 0.5) -> Tuple[str, float, dict]:
        """Extract hidden message using DWT decomposition and cross-correlation."""
        audio = normalize_audio(audio, 0.9)
        
        # 1. Perform Wavelet Decomposition
        coeffs = pywt.wavedec(audio, self.wavelet, level=self.level)
        target_band = coeffs[0]  # cA3: must match encoder band
        
        # 2. Extract Header (First 32 bits)
        header_pn = self._generate_pn_sequence(32)
        extracted_header = []
        
        for i in range(32):
            segment = target_band[i*self.chip_rate : (i+1)*self.chip_rate]
            if len(segment) < self.chip_rate:
                segment = np.pad(segment, (0, self.chip_rate - len(segment)))
            correlation = np.dot(segment, header_pn[i])
            extracted_header.append(1 if correlation > 0 else -1)
            
        header_bits = [1 if b > 0 else 0 for b in extracted_header]
        msg_length = 0
        for i in range(4):
            byte_val = int(''.join([str(b) for b in header_bits[i*8:(i+1)*8]]), 2)
            msg_length = (msg_length << 8) | byte_val
            
        if msg_length <= 0 or msg_length > 2000:
             return "", 0.0, {'error': 'Invalid header detected'}
             
        total_bits = 32 + (msg_length * 8)
        if total_bits * self.chip_rate > len(target_band):
            return "", 0.0, {'error': 'Extracted length overflows coefficient band'}

        # 3. Extract Full Message Sequence via despreading
        full_pn = self._generate_pn_sequence(total_bits)
        extracted_bits = []
        correlations = []
        
        for i in range(total_bits):
            segment = target_band[i*self.chip_rate : (i+1)*self.chip_rate]
            if len(segment) < self.chip_rate:
                segment = np.pad(segment, (0, self.chip_rate - len(segment)))
            correlation = np.dot(segment, full_pn[i])
            extracted_bits.append(1 if correlation > 0 else -1)
            correlations.append(abs(correlation))
            
        # 4. Convert and compute exact mathematical confidence metric
        message, success = self._binary_to_message(extracted_bits)
        
        avg_corr = np.mean(correlations) if len(correlations) > 0 else 0
        expected_corr = self.chip_rate * self.alpha_estimate
        
        if success:
            normalized_confidence = avg_corr / expected_corr
            confidence = np.clip(normalized_confidence, 0.0, 0.99)
        else:
            confidence = 0.0
        
        metadata = {
            'bits_extracted': total_bits,
            'wavelet': self.wavelet,
            'success': success,
            'sample_rate': self.sr
        }
        
        return message, float(confidence), metadata

def decode_audio(audio: np.ndarray, sr: int = 44100, sensitivity: float = 0.5) -> Tuple[str, float, dict]:
    decoder = SteganoDecoder(sr=sr)
    return decoder.decode(audio, sensitivity)