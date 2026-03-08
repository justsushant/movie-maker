"""Property-based tests for AudioAnalyzer."""

from __future__ import annotations
import pytest
import numpy as np
from pathlib import Path
import tempfile
from hypothesis import given, strategies as st, assume, settings
from scipy.io import wavfile

from engine.audio.analyzer import AudioAnalyzer


# Strategy for generating valid audio data
@st.composite
def audio_data(draw):
    """Generate synthetic audio data."""
    duration = draw(st.floats(min_value=0.1, max_value=5.0))
    sample_rate = draw(st.sampled_from([22050, 44100, 48000]))
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = draw(st.floats(min_value=100.0, max_value=1000.0))
    audio = np.sin(2 * np.pi * frequency * t)
    
    # Add some amplitude variation
    amplitude = draw(st.floats(min_value=0.1, max_value=1.0))
    audio = (audio * amplitude * 32767).astype(np.int16)
    
    return audio, sample_rate


@settings(max_examples=50, deadline=5000)
@given(audio_data())
def test_property_audio_loading_produces_valid_data(audio_data_tuple):
    """
    Property 1: Audio Loading Produces Valid Data
    
    For any valid audio file, when AudioAnalyzer loads the audio,
    the resulting sample rate should be positive and the audio samples
    should be a non-empty numpy array.
    
    Validates: Requirements 1.2, 1.3
    Tag: Feature: video-engine-phase-3, Property 1
    """
    audio, sample_rate = audio_data_tuple
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = Path(f.name)
        wavfile.write(temp_path, sample_rate, audio)
    
    try:
        # Load audio with AudioAnalyzer
        analyzer = AudioAnalyzer(temp_path)
        
        # Verify sample rate is positive
        assert analyzer.sr > 0, "Sample rate must be positive"
        
        # Verify audio samples are non-empty numpy array
        assert isinstance(analyzer.y, np.ndarray), "Audio samples must be numpy array"
        assert len(analyzer.y) > 0, "Audio samples must be non-empty"
        
        # Verify duration is positive
        assert analyzer.duration > 0, "Duration must be positive"
        
        # Verify duration matches expected value
        expected_duration = len(audio) / sample_rate
        assert abs(analyzer.duration - expected_duration) < 0.1, \
            "Duration should match audio length"
    
    finally:
        # Clean up temporary file
        temp_path.unlink()


@settings(max_examples=50, deadline=5000)
@given(audio_data())
def test_property_analysis_methods_return_timestamp_arrays(audio_data_tuple):
    """
    Property 2: Analysis Methods Return Timestamp Arrays
    
    For any valid audio file, when any analysis method (beats, onsets, energy,
    spectral_centroid) is called, the returned timestamps should be monotonically
    increasing arrays in seconds.
    
    Validates: Requirements 1.4, 1.5, 1.6, 1.7, 1.8
    Tag: Feature: video-engine-phase-3, Property 2
    """
    audio, sample_rate = audio_data_tuple
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = Path(f.name)
        wavfile.write(temp_path, sample_rate, audio)
    
    try:
        analyzer = AudioAnalyzer(temp_path)
        
        # Test beat detection
        beats = analyzer.analyze_beats()
        assert isinstance(beats, np.ndarray), "Beats must be numpy array"
        if len(beats) > 1:
            assert np.all(beats[1:] > beats[:-1]), "Beat timestamps must be monotonically increasing"
            assert np.all(beats >= 0), "Beat timestamps must be non-negative"
            assert np.all(beats <= analyzer.duration), "Beat timestamps must be within audio duration"
        
        # Test onset detection
        onsets = analyzer.analyze_onsets()
        assert isinstance(onsets, np.ndarray), "Onsets must be numpy array"
        if len(onsets) > 1:
            assert np.all(onsets[1:] > onsets[:-1]), "Onset timestamps must be monotonically increasing"
            assert np.all(onsets >= 0), "Onset timestamps must be non-negative"
            assert np.all(onsets <= analyzer.duration), "Onset timestamps must be within audio duration"
        
        # Test energy analysis
        energy_times, energy_values = analyzer.analyze_energy()
        assert isinstance(energy_times, np.ndarray), "Energy times must be numpy array"
        assert isinstance(energy_values, np.ndarray), "Energy values must be numpy array"
        assert len(energy_times) == len(energy_values), "Energy times and values must have same length"
        if len(energy_times) > 1:
            assert np.all(energy_times[1:] > energy_times[:-1]), "Energy timestamps must be monotonically increasing"
            assert np.all(energy_times >= 0), "Energy timestamps must be non-negative"
            assert np.all(energy_values >= 0), "Energy values must be non-negative"
        
        # Test spectral centroid analysis
        spectral_times, spectral_values = analyzer.analyze_spectral_centroid()
        assert isinstance(spectral_times, np.ndarray), "Spectral times must be numpy array"
        assert isinstance(spectral_values, np.ndarray), "Spectral values must be numpy array"
        assert len(spectral_times) == len(spectral_values), "Spectral times and values must have same length"
        if len(spectral_times) > 1:
            assert np.all(spectral_times[1:] > spectral_times[:-1]), "Spectral timestamps must be monotonically increasing"
            assert np.all(spectral_times >= 0), "Spectral timestamps must be non-negative"
            assert np.all(spectral_values >= 0), "Spectral centroid values must be non-negative"
    
    finally:
        temp_path.unlink()
