#!/usr/bin/env python
"""
Flask API backend for Audio Steganography
Handles file uploads, encoding, decoding, and downloads
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import io

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.encoder import SteganoEncoder
from core.decoder import SteganoDecoder
from core.audio_utils import load_audio, save_audio, generate_test_audio
from core.noise_test import add_gaussian_noise

app = Flask(__name__)
CORS(app)

# Create upload folder
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Create encoded audio output folder
ENCODED_FOLDER = Path("encoded-audio")
ENCODED_FOLDER.mkdir(exist_ok=True)

@app.route('/api/encode', methods=['POST'])
def encode_message():
    """Encode a message into uploaded audio file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        message = request.form.get('message', '')
        wavelet = request.form.get('wavelet', 'db4')
        level = int(request.form.get('level', 3))
        alpha = float(request.form.get('alpha', 0.03))
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = UPLOAD_FOLDER / file.filename
        file.save(temp_path)
        
        # Load audio
        audio, sr = load_audio(str(temp_path))
        
        # Encode message
        encoder = SteganoEncoder(sr=sr, wavelet=wavelet, level=level)
        encoder.alpha = alpha
        encoded_audio, metadata = encoder.encode(audio, message)
        
        # Save encoded audio to designated output folder
        output_filename = f"encoded_{file.filename}"
        output_path = ENCODED_FOLDER / output_filename
        save_audio(str(output_path), encoded_audio, sr)
        
        # Save encoded audio to bytes
        output = io.BytesIO()
        save_audio_to_bytes(output, encoded_audio, sr)
        output.seek(0)
        
        # Clean up temp file
        temp_path.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Successfully encoded "{message}" into audio',
            'metadata': metadata
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/encode-download', methods=['POST'])
def encode_and_download():
    """Encode message and return file for download"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        message = request.form.get('message', '')
        wavelet = request.form.get('wavelet', 'db4')
        level = int(request.form.get('level', 3))
        alpha = float(request.form.get('alpha', 0.03))
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = UPLOAD_FOLDER / file.filename
        file.save(temp_path)
        
        # Load audio
        audio, sr = load_audio(str(temp_path))
        
        # Encode message
        encoder = SteganoEncoder(sr=sr, wavelet=wavelet, level=level)
        encoder.alpha = alpha
        encoded_audio, metadata = encoder.encode(audio, message)
        
        # Save encoded audio to designated output folder
        output_filename = f"encoded_{file.filename}"
        output_path = ENCODED_FOLDER / output_filename
        save_audio(str(output_path), encoded_audio, sr)
        
        # Create output bytes
        output = io.BytesIO()
        save_audio_to_bytes(output, encoded_audio, sr)
        output.seek(0)
        
        # Clean up temp file
        temp_path.unlink()
        
        # Return file for download
        return send_file(
            output,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'encoded_{file.filename}'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/decode', methods=['POST'])
def decode_message():
    """Decode message from uploaded audio file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        wavelet = request.form.get('wavelet', 'db4')
        level = int(request.form.get('level', 3))
        sensitivity = float(request.form.get('sensitivity', 0.5))
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = UPLOAD_FOLDER / file.filename
        file.save(temp_path)
        
        # Load audio
        audio, sr = load_audio(str(temp_path))
        
        # Decode message
        decoder = SteganoDecoder(sr=sr, wavelet=wavelet, level=level)
        message, confidence, metadata = decoder.decode(audio, sensitivity=sensitivity)
        
        # Clean up temp file
        temp_path.unlink()
        
        return jsonify({
            'success': True,
            'message': message,
            'confidence': float(confidence),
            'metadata': metadata
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/generate-test-audio', methods=['GET'])
def generate_test():
    """Generate test audio and return for download"""
    try:
        duration = float(request.args.get('duration', 3.0))
        sr = int(request.args.get('sr', 44100))
        
        audio = generate_test_audio(duration=duration, sr=sr)
        
        # Create output bytes
        output = io.BytesIO()
        save_audio_to_bytes(output, audio, sr)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'test_audio_{duration}s.wav'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/noise-test', methods=['POST'])
def noise_test():
    """Add noise to audio and attempt decoding"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        snr_db = float(request.form.get('snr_db', 20))
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = UPLOAD_FOLDER / file.filename
        file.save(temp_path)
        
        # Load audio
        audio, sr = load_audio(str(temp_path))
        
        # Add noise
        noisy_audio = add_gaussian_noise(audio, snr_db=snr_db)
        
        # Try to decode from noisy audio
        decoder = SteganoDecoder(sr=sr)
        message, confidence, metadata = decoder.decode(noisy_audio)
        
        # Clean up temp file
        temp_path.unlink()
        
        return jsonify({
            'success': True,
            'message': message,
            'confidence': float(confidence),
            'snr_db': snr_db,
            'metadata': metadata
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Audio Steganography API'}), 200


def save_audio_to_bytes(bytes_io, audio: np.ndarray, sr: int) -> None:
    """Save audio to BytesIO object"""
    import soundfile as sf
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(bytes_io, audio, sr, format='WAV', subtype='PCM_16')


if __name__ == '__main__':
    print("Starting Audio Steganography API Server...")
    print("API running at http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/encode - Encode message into audio")
    print("  POST /api/encode-download - Encode and download")
    print("  POST /api/decode - Decode message from audio")
    print("  GET  /api/generate-test-audio - Generate test audio")
    print("  POST /api/noise-test - Add noise and test decoding")
    print("  GET  /api/health - Health check")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
