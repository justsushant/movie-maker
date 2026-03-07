"""Generate synthetic test audio files for Phase 3 testing.

This script creates simple synthetic audio files with known characteristics
for testing audio analysis functionality.
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path

# Create audio directory if it doesn't exist
audio_dir = Path(__file__).parent
audio_dir.mkdir(parents=True, exist_ok=True)

def generate_beat_audio(filename: str, duration: float = 2.0, bpm: float = 120.0, sr: int = 22050):
    """Generate audio with clear beat pattern.
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        bpm: Beats per minute
        sr: Sample rate
    """
    t = np.linspace(0, duration, int(sr * duration))
    
    # Generate beats as short sine bursts
    beat_interval = 60.0 / bpm  # seconds per beat
    audio = np.zeros_like(t)
    
    beat_times = []
    current_time = 0.0
    while current_time < duration:
        beat_times.append(current_time)
        # Create a short burst (50ms)
        burst_duration = 0.05
        burst_mask = (t >= current_time) & (t < current_time + burst_duration)
        audio[burst_mask] = np.sin(2 * np.pi * 440 * (t[burst_mask] - current_time))
        current_time += beat_interval
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Convert to int16
    audio_int = (audio * 32767).astype(np.int16)
    
    wavfile.write(audio_dir / filename, sr, audio_int)
    print(f"Generated {filename} with {len(beat_times)} beats at {bpm} BPM")
    print(f"  Expected beat times: {[f'{t:.2f}' for t in beat_times[:5]]}...")
    return beat_times

def generate_onset_audio(filename: str, duration: float = 2.0, onset_interval: float = 0.5, sr: int = 22050):
    """Generate audio with sharp onsets (transients).
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        onset_interval: Time between onsets in seconds
        sr: Sample rate
    """
    t = np.linspace(0, duration, int(sr * duration))
    audio = np.zeros_like(t)
    
    onset_times = []
    current_time = 0.1  # Start slightly after beginning
    while current_time < duration:
        onset_times.append(current_time)
        # Create sharp transient (10ms)
        transient_duration = 0.01
        transient_mask = (t >= current_time) & (t < current_time + transient_duration)
        # Sharp attack with exponential decay
        transient_t = t[transient_mask] - current_time
        envelope = np.exp(-transient_t / 0.005)
        audio[transient_mask] = envelope * np.sin(2 * np.pi * 880 * transient_t)
        current_time += onset_interval
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Convert to int16
    audio_int = (audio * 32767).astype(np.int16)
    
    wavfile.write(audio_dir / filename, sr, audio_int)
    print(f"Generated {filename} with {len(onset_times)} onsets")
    print(f"  Expected onset times: {[f'{t:.2f}' for t in onset_times]}")
    return onset_times

def generate_varying_energy_audio(filename: str, duration: float = 2.0, sr: int = 22050):
    """Generate audio with varying energy levels.
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        sr: Sample rate
    """
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create amplitude envelope that varies over time
    # Low -> High -> Low pattern
    envelope = 0.2 + 0.6 * np.sin(2 * np.pi * 0.5 * t) ** 2
    
    # Generate tone with varying amplitude
    audio = envelope * np.sin(2 * np.pi * 440 * t)
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Convert to int16
    audio_int = (audio * 32767).astype(np.int16)
    
    wavfile.write(audio_dir / filename, sr, audio_int)
    print(f"Generated {filename} with varying energy")

def generate_silent_audio(filename: str, duration: float = 1.0, sr: int = 22050):
    """Generate silent audio for edge case testing.
    
    Args:
        filename: Output filename
        duration: Duration in seconds
        sr: Sample rate
    """
    audio = np.zeros(int(sr * duration), dtype=np.int16)
    wavfile.write(audio_dir / filename, sr, audio)
    print(f"Generated {filename} (silent)")

if __name__ == "__main__":
    print("Generating test audio files...")
    print()
    
    # Generate test files
    generate_beat_audio("test_beats_120bpm.wav", duration=2.0, bpm=120.0)
    generate_onset_audio("test_onsets.wav", duration=2.0, onset_interval=0.5)
    generate_varying_energy_audio("test_energy.wav", duration=2.0)
    generate_silent_audio("test_silent.wav", duration=1.0)
    
    print()
    print("Test audio files generated successfully!")
    print(f"Location: {audio_dir}")
