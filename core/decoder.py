"""
Audio Steganography - STFT-Based Decoder
Extracts secret messages from encoded audio using phase detection and majority voting.
"""

import numpy as np
from scipy import signal
from typing import Tuple
from core.audio_utils import normalize_audio


class SteganoDecoder:
    """STFT-based audio steganography decoder with majority voting."""
    
    def __init__(self, sr: int = 44100, window_size: int = 512, hop_length: int = 256):
        """
        Initialize decoder.
        
        Args:
            sr: Sample rate (Hz)
            window_size: STFT window size
            hop_length: Hop length for STFT
        """
        self.sr = sr
        self.window_size = window_size
        self.hop_length = hop_length
        self.redundancy = 3  # Expect each bit repeated 3 times
        self.phase_shift_0 = np.pi / 4      # ±π/4 for bit 0
        self.phase_shift_1 = np.pi / 2      # ±π/2 for bit 1
        self.threshold = 0.5  # Threshold for phase detection
    
    def _get_embedding_positions(self, num_frames: int, num_bits: int) -> np.ndarray:
        """
        Generate same pseudo-random frequency bin positions as encoder.
        
        Args:
            num_frames: Number of STFT frames
            num_bits: Total number of bits (with redundancy)
        
        Returns:
            Array of shape (num_bits, num_frames) with bin indices
        """
        # Use same seed as encoder for reproducibility
        seed = int(np.random.RandomState(42).uniform(0, 2**31 - 1))
        rng = np.random.RandomState(seed)
        
        # Same configuration as encoder
        num_bins = self.window_size // 2 - 1
        min_bin = 2
        max_bin = min(num_bins - 2, int(self.sr / 2 / 100))
        
        positions = np.zeros((num_bits, num_frames), dtype=np.int32)
        for i in range(num_bits):
            positions[i, :] = rng.randint(min_bin, max_bin, num_frames)
        
        return positions
    
    def _extract_bit(self, stft_frame: np.ndarray, bin_idx: int) -> float:
        """
        Extract bit from phase of frequency component.
        
        Args:
            stft_frame: STFT frame (frequency domain)
            bin_idx: Frequency bin index
        
        Returns:
            Probability of bit being 1 (0.0 to 1.0)
        """
        # Get phase
        phase = np.angle(stft_frame[bin_idx])
        
        # Measure phase difference from expected values
        diff_0 = min(abs(phase - self.phase_shift_0), abs(phase + self.phase_shift_0))
        diff_1 = min(abs(phase - self.phase_shift_1), abs(phase + self.phase_shift_1))
        
        # Likelihood of bit 1 based on phase difference
        if diff_0 + diff_1 == 0:
            return 0.5
        
        likelihood_1 = 1.0 - (diff_1 / (diff_0 + diff_1))
        return likelihood_1
    
    def _majority_vote(self, redundant_bits: np.ndarray) -> np.ndarray:
        """
        Recover original bits using majority voting on redundant copies.
        
        Args:
            redundant_bits: Array of redundant bits (each bit repeated 3 times)
        
        Returns:
            Recovered binary array
        """
        # Convert to binary decisions first
        binary_redundant = (redundant_bits > self.threshold).astype(np.uint8)
        
        # Apply majority voting
        num_original_bits = len(binary_redundant) // self.redundancy
        recovered_bits = np.zeros(num_original_bits, dtype=np.uint8)
        
        for i in range(num_original_bits):
            redundant_group = binary_redundant[i * self.redundancy:(i + 1) * self.redundancy]
            # Majority vote: bit is 1 if sum > 1.5, i.e., at least 2 out of 3 are 1
            recovered_bits[i] = 1 if np.sum(redundant_group) > 1 else 0
        
        return recovered_bits
    
    def _binary_to_message(self, binary_array: np.ndarray) -> Tuple[str, bool]:
        """
        Convert binary array back to message string.
        
        Args:
            binary_array: Binary array
        
        Returns:
            Tuple of (message, success_flag)
        """
        # First 32 bits are the length header
        if len(binary_array) < 32:
            return "", False
        
        header_bits = binary_array[:32]
        
        # Convert header to length (big-endian)
        length = 0
        for i in range(4):
            byte_bits = header_bits[i*8:(i+1)*8]
            byte_val = int(''.join([str(b) for b in byte_bits]), 2)
            length = (length << 8) | byte_val
        
        # Validate length
        if length <= 0 or length > 1000 or len(binary_array) < 32 + length * 8:
            return "", False
        
        # Extract message bytes
        message_bits = binary_array[32:32 + length * 8]
        
        try:
            message_chars = []
            for i in range(length):
                char_bits = message_bits[i*8:(i+1)*8]
                char_val = int(''.join([str(b) for b in char_bits]), 2)
                
                # Validate ASCII character
                if 32 <= char_val <= 126:  # Printable ASCII
                    message_chars.append(chr(char_val))
                else:
                    return "", False
            
            message = ''.join(message_chars)
            return message, True
        
        except:
            return "", False
    
    def decode(self, audio: np.ndarray, sensitivity: float = 0.5) -> Tuple[str, float, dict]:
        """
        Extract message from encoded audio.
        
        Args:
            audio: Encoded audio signal
            sensitivity: Detection sensitivity (0.0 to 1.0), higher = stricter
        
        Returns:
            Tuple of (message, confidence, metadata)
        """
        # Normalize input
        audio = normalize_audio(audio, 0.9)
        
        # Apply STFT with same parameters as encoder
        f, t, Sxx = signal.stft(
            audio,
            fs=self.sr,
            window='hann',
            nperseg=self.window_size,
            noverlap=self.window_size - self.hop_length
        )
        
        num_frames = Sxx.shape[1]
        
        # Estimate number of bits based on frame count
        # Use conservative estimate to avoid over-extraction
        bits_per_frame = 2
        num_redundant_bits = min(num_frames * bits_per_frame, 4000)  # Max 4000 bits = 500 bytes
        
        # Get embedding positions
        embedding_positions = self._get_embedding_positions(num_frames, num_redundant_bits)
        
        # Extract bits from STFT
        extracted_bits = []
        bits_extracted = 0
        
        for frame_idx in range(num_frames):
            for bit_idx in range(bits_per_frame):
                if bits_extracted >= num_redundant_bits:
                    break
                
                actual_bit_idx = frame_idx * bits_per_frame + bit_idx
                if actual_bit_idx < num_redundant_bits:
                    bin_idx = embedding_positions[actual_bit_idx, frame_idx]
                    likelihood = self._extract_bit(Sxx[:, frame_idx], bin_idx)
                    
                    # Apply sensitivity threshold
                    adjusted_likelihood = (likelihood - 0.5) * (1.0 + sensitivity) + 0.5
                    adjusted_likelihood = np.clip(adjusted_likelihood, 0.0, 1.0)
                    
                    extracted_bits.append(adjusted_likelihood)
                    bits_extracted += 1
            
            if bits_extracted >= num_redundant_bits:
                break
        
        # Apply majority voting
        extracted_bits = np.array(extracted_bits)
        recovered_bits = self._majority_vote(extracted_bits)
        
        # Convert to message
        message, success = self._binary_to_message(recovered_bits)
        
        # Calculate confidence
        if success:
            # Confidence based on how well bits matched their expected phase patterns
            binary_extracted = (extracted_bits > 0.5).astype(np.uint8)
            agreement_rate = np.mean(binary_extracted[:len(recovered_bits)*self.redundancy] == np.repeat(recovered_bits, self.redundancy))
            confidence = min(0.99, 0.7 + agreement_rate * 0.3)
        else:
            confidence = 0.0
        
        # Metadata
        metadata = {
            'num_frames': num_frames,
            'bits_extracted': len(extracted_bits),
            'success': success,
            'window_size': self.window_size,
            'hop_length': self.hop_length,
            'sample_rate': self.sr
        }
        
        return message, confidence, metadata


def decode_audio(audio: np.ndarray, sr: int = 44100, 
                 sensitivity: float = 0.5) -> Tuple[str, float, dict]:
    """
    Convenience function to decode audio with default parameters.
    
    Args:
        audio: Encoded audio signal
        sr: Sample rate
        sensitivity: Detection sensitivity
    
    Returns:
        Tuple of (message, confidence, metadata)
    """
    decoder = SteganoDecoder(sr=sr)
    return decoder.decode(audio, sensitivity)
