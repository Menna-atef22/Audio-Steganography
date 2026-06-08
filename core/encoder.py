"""
Audio Steganography - STFT-Based Encoder
Embeds secret messages in audio using frequency domain manipulation with phase modulation.
Uses redundancy (3x repetition) for robust recovery.
"""

import numpy as np
from scipy import signal
from typing import Tuple, List
from core.audio_utils import normalize_audio, get_audio_hash


class SteganoEncoder:
    """STFT-based audio steganography encoder with phase modulation."""
    
    def __init__(self, sr: int = 44100, window_size: int = 512, hop_length: int = 256):
        """
        Initialize encoder.
        
        Args:
            sr: Sample rate (Hz)
            window_size: STFT window size
            hop_length: Hop length for STFT
        """
        self.sr = sr
        self.window_size = window_size
        self.hop_length = hop_length
        self.redundancy = 3  # Repeat each bit 3 times
        self.phase_shift_0 = np.pi / 4      # ±π/4 for bit 0
        self.phase_shift_1 = np.pi / 2      # ±π/2 for bit 1
    
    def _message_to_binary(self, message: str) -> np.ndarray:
        """
        Convert message to binary stream with header.
        
        Args:
            message: Secret message (alphanumeric + spaces)
        
        Returns:
            Binary array of bits
        """
        # Convert message to uppercase and encode as ASCII
        message = message.upper()
        ascii_codes = np.array([ord(c) for c in message], dtype=np.uint8)
        
        # Create 32-bit length header (big-endian)
        length = len(message)
        header = np.array([
            (length >> 24) & 0xFF,
            (length >> 16) & 0xFF,
            (length >> 8) & 0xFF,
            length & 0xFF
        ], dtype=np.uint8)
        
        # Concatenate header and message
        full_data = np.concatenate([header, ascii_codes])
        
        # Convert to binary (MSB first)
        binary_str = ''.join([format(byte, '08b') for byte in full_data])
        binary_array = np.array([int(b) for b in binary_str], dtype=np.uint8)
        
        return binary_array
    
    def _get_embedding_positions(self, num_frames: int, num_bits: int) -> np.ndarray:
        """
        Generate pseudo-random frequency bin positions for embedding.
        
        Args:
            num_frames: Number of STFT frames
            num_bits: Number of bits to embed (with redundancy)
        
        Returns:
            Array of shape (num_bits, num_frames) with bin indices
        """
        # Create deterministic seed based on total energy
        # This seed will be consistent across encoder and decoder
        seed = int(np.random.RandomState(42).uniform(0, 2**31 - 1))
        rng = np.random.RandomState(seed)
        
        # Generate bin positions (avoid DC and Nyquist components)
        num_bins = self.window_size // 2 - 1
        min_bin = 2  # Skip DC and very low frequencies
        max_bin = min(num_bins - 2, int(self.sr / 2 / 100))  # Up to ~100 Hz
        
        positions = np.zeros((num_bits, num_frames), dtype=np.int32)
        for i in range(num_bits):
            positions[i, :] = rng.randint(min_bin, max_bin, num_frames)
        
        return positions
    
    def _embed_bit(self, stft_frame: np.ndarray, bin_idx: int, bit: int) -> np.ndarray:
        """
        Embed a single bit using phase modulation.
        
        Args:
            stft_frame: STFT frame (frequency domain)
            bin_idx: Frequency bin index
            bit: Bit value (0 or 1)
        
        Returns:
            Modified STFT frame
        """
        stft_frame = stft_frame.copy()
        
        # Get magnitude and phase
        magnitude = np.abs(stft_frame[bin_idx])
        phase = np.angle(stft_frame[bin_idx])
        
        # Apply phase shift based on bit value
        if bit == 0:
            # Add ±π/4 randomly
            phase_shift = self.phase_shift_0 * np.random.choice([-1, 1])
        else:
            # Add ±π/2 randomly
            phase_shift = self.phase_shift_1 * np.random.choice([-1, 1])
        
        # Modify phase (keep magnitude unchanged)
        new_phase = phase + phase_shift
        stft_frame[bin_idx] = magnitude * np.exp(1j * new_phase)
        
        return stft_frame
    
    def encode(self, audio: np.ndarray, message: str) -> Tuple[np.ndarray, dict]:
        """
        Embed message in audio signal.
        
        Args:
            audio: Audio signal (numpy array)
            message: Secret message (alphanumeric + spaces, max 1000 chars)
        
        Returns:
            Tuple of (encoded_audio, metadata)
        """
        # Validate and normalize input
        audio = normalize_audio(audio, 0.9)
        binary_message = self._message_to_binary(message)
        
        # Add redundancy: repeat each bit 3 times
        redundant_bits = np.repeat(binary_message, self.redundancy)
        
        # Apply STFT
        f, t, Sxx = signal.stft(
            audio,
            fs=self.sr,
            window='hann',
            nperseg=self.window_size,
            noverlap=self.window_size - self.hop_length
        )
        
        num_frames = Sxx.shape[1]
        num_bits = len(redundant_bits)
        
        # Get embedding positions
        embedding_positions = self._get_embedding_positions(num_frames, num_bits)
        
        # Embed bits
        bits_per_frame = num_bits // num_frames
        
        for frame_idx in range(num_frames):
            start_bit = frame_idx * bits_per_frame
            end_bit = min(start_bit + bits_per_frame, num_bits)
            
            for bit_offset, bit_idx in enumerate(range(start_bit, end_bit)):
                if bit_idx < num_bits:
                    bin_idx = embedding_positions[bit_idx, frame_idx]
                    bit_value = redundant_bits[bit_idx]
                    
                    # Embed bit in this frame
                    Sxx[:, frame_idx] = self._embed_bit(Sxx[:, frame_idx], bin_idx, bit_value)
        
        # Reconstruct audio using inverse STFT
        _, encoded_audio = signal.istft(
            Sxx,
            fs=self.sr,
            window='hann',
            nperseg=self.window_size,
            noverlap=self.window_size - self.hop_length
        )
        
        # Ensure output length matches input
        if len(encoded_audio) > len(audio):
            encoded_audio = encoded_audio[:len(audio)]
        elif len(encoded_audio) < len(audio):
            encoded_audio = np.pad(encoded_audio, (0, len(audio) - len(encoded_audio)))
        
        # Final normalization
        encoded_audio = normalize_audio(encoded_audio, 0.9)
        
        # Metadata
        metadata = {
            'message_length': len(message),
            'binary_length': len(binary_message),
            'redundant_length': len(redundant_bits),
            'num_frames': num_frames,
            'window_size': self.window_size,
            'hop_length': self.hop_length,
            'sample_rate': self.sr
        }
        
        return encoded_audio, metadata


def encode_audio(audio: np.ndarray, message: str, sr: int = 44100) -> Tuple[np.ndarray, dict]:
    """
    Convenience function to encode audio with default parameters.
    
    Args:
        audio: Audio signal
        message: Secret message
        sr: Sample rate
    
    Returns:
        Tuple of (encoded_audio, metadata)
    """
    encoder = SteganoEncoder(sr=sr)
    return encoder.encode(audio, message)
