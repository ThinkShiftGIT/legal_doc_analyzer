import os
from pathlib import Path
from reportlab.pdfgen import canvas
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip
import numpy as np
import wave
import struct
import tempfile

# Create test directory
TEST_DIR = Path(__file__).parent / "test_data"
TEST_DIR.mkdir(exist_ok=True)

def create_test_pdf(pdf_path: Path = None):
    """Create a test PDF file with sample legal text"""
    if pdf_path is None:
        pdf_path = TEST_DIR / "test.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "LEGAL DOCUMENT - TEST SAMPLE")
    c.drawString(100, 700, "This agreement is made between Party A and Party B.")
    c.drawString(100, 650, "1. Both parties agree to the following terms:")
    c.drawString(120, 630, "a) Maintain confidentiality")
    c.drawString(120, 610, "b) Provide timely updates")
    c.save()

def create_test_audio(audio_path: Path = None):
    """Create a test WAV audio file that simulates speech patterns"""
    if audio_path is None:
        audio_path = TEST_DIR / "test.wav"
    
    # Audio parameters
    sample_rate = 16000  # Common for speech
    duration = 2  # seconds
    
    # Create WAV file
    wav_file = wave.open(str(audio_path), 'w')
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    
    # Generate speech-like signal
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Fundamental frequency (typical for human voice)
    f0 = 150
    
    # Generate a more complex waveform that mimics speech
    signal = np.zeros_like(t)
    
    # Add fundamental frequency and harmonics
    for harmonic in range(1, 5):
        frequency = f0 * harmonic
        amplitude = 1.0 / harmonic
        signal += amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Add amplitude modulation to simulate syllables
    syllable_rate = 4  # syllables per second
    envelope = 0.5 * (1 + np.sin(2 * np.pi * syllable_rate * t))
    signal *= envelope
    
    # Normalize and convert to 16-bit integer
    signal = signal / np.max(np.abs(signal))
    signal = (signal * 32767).astype(np.int16)
    
    # Write to file
    wav_file.writeframes(signal.tobytes())
    wav_file.close()

def create_test_video(video_path: Path = None):
    """Create a test MP4 video file with audio"""
    if video_path is None:
        video_path = TEST_DIR / "test.mp4"
    
    # Create a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple video clip with text
        duration = 2
        size = (640, 480)
        color_clip = ColorClip(size=size, color=(0, 0, 255), duration=duration)
        
        # Create test audio
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
        create_test_audio(Path(temp_audio_path))
        audio_clip = AudioFileClip(temp_audio_path)
        
        # Combine video and audio
        video_clip = color_clip.set_audio(audio_clip)
        video_clip.write_videofile(
            str(video_path),
            fps=24,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # Clean up
        video_clip.close()
        audio_clip.close()
        color_clip.close()

if __name__ == "__main__":
    create_test_pdf()
    create_test_audio()
    create_test_video()