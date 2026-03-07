"""Unit tests for AudioAnalyzer (Phase 3)."""

from __future__ import annotations
import pytest
import numpy as np
from pathlib import Path

# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "audio"


def test_audio_analyzer_import_error():
    """Test that AudioAnalyzer raises ImportError when librosa not available."""
    # This test would need to mock the import, skip for now since librosa is installed
    pytest.skip("Requires mocking librosa import")


def test_audio_analyzer_file_not_found():
    """Test that AudioAnalyzer raises FileNotFoundError for missing files."""
    from engine.audio.analyzer import AudioAnalyzer
    
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        AudioAnalyzer("nonexistent_file.wav")


def test_audio_analyzer_loads_audio():
    """Test that AudioAnalyzer successfully loads audio files."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_silent.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    # Check that audio was loaded
    assert analyzer.y is not None
    assert len(analyzer.y) > 0
    assert analyzer.sr > 0
    assert analyzer.duration > 0
    
    # For 1 second silent audio at 22050 Hz
    assert analyzer.duration == pytest.approx(1.0, abs=0.01)


def test_audio_analyzer_beat_detection():
    """Test beat detection with synthetic beat audio."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_beats_120bpm.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    beats = analyzer.analyze_beats()
    
    # Check that beats were detected
    assert len(beats) > 0
    assert isinstance(beats, np.ndarray)
    
    # Beats should be in ascending order
    assert np.all(beats[:-1] <= beats[1:])
    
    # Beats should be within audio duration
    assert np.all(beats >= 0)
    assert np.all(beats <= analyzer.duration)
    
    # For 120 BPM (0.5s interval), expect beats near 0.0, 0.5, 1.0, 1.5
    # Librosa may not detect all beats perfectly, but should find some
    assert len(beats) >= 2  # At least 2 beats detected


def test_audio_analyzer_beat_caching():
    """Test that beat analysis results are cached."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_beats_120bpm.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    beats1 = analyzer.analyze_beats()
    beats2 = analyzer.analyze_beats()
    
    # Should return the same array object (cached)
    assert beats1 is beats2


def test_audio_analyzer_onset_detection():
    """Test onset detection with synthetic onset audio."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_onsets.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    onsets = analyzer.analyze_onsets()
    
    # Check that onsets were detected
    assert len(onsets) > 0
    assert isinstance(onsets, np.ndarray)
    
    # Onsets should be in ascending order
    assert np.all(onsets[:-1] <= onsets[1:])
    
    # Onsets should be within audio duration
    assert np.all(onsets >= 0)
    assert np.all(onsets <= analyzer.duration)
    
    # Expected onsets at 0.1, 0.6, 1.1, 1.6
    # Librosa should detect at least some of these
    assert len(onsets) >= 2


def test_audio_analyzer_onset_caching():
    """Test that onset analysis results are cached."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_onsets.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    onsets1 = analyzer.analyze_onsets()
    onsets2 = analyzer.analyze_onsets()
    
    # Should return the same array object (cached)
    assert onsets1 is onsets2


def test_audio_analyzer_energy_analysis():
    """Test energy envelope analysis."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_energy.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    times, energy = analyzer.analyze_energy()
    
    # Check return format
    assert isinstance(times, np.ndarray)
    assert isinstance(energy, np.ndarray)
    assert len(times) == len(energy)
    assert len(times) > 0
    
    # Times should be in ascending order
    assert np.all(times[:-1] <= times[1:])
    
    # Times should span the audio duration
    assert times[0] >= 0
    assert times[-1] <= analyzer.duration
    
    # Energy values should be non-negative
    assert np.all(energy >= 0)
    
    # For varying energy audio, should have some variation
    assert np.std(energy) > 0


def test_audio_analyzer_energy_caching():
    """Test that energy analysis results are cached."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_energy.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    result1 = analyzer.analyze_energy()
    result2 = analyzer.analyze_energy()
    
    # Should return the same tuple (cached)
    assert result1 is result2


def test_audio_analyzer_spectral_centroid():
    """Test spectral centroid analysis."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_energy.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    times, centroid = analyzer.analyze_spectral_centroid()
    
    # Check return format
    assert isinstance(times, np.ndarray)
    assert isinstance(centroid, np.ndarray)
    assert len(times) == len(centroid)
    assert len(times) > 0
    
    # Times should be in ascending order
    assert np.all(times[:-1] <= times[1:])
    
    # Times should span the audio duration
    assert times[0] >= 0
    assert times[-1] <= analyzer.duration
    
    # Centroid values should be positive (Hz)
    assert np.all(centroid > 0)


def test_audio_analyzer_spectral_centroid_caching():
    """Test that spectral centroid analysis results are cached."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_energy.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    result1 = analyzer.analyze_spectral_centroid()
    result2 = analyzer.analyze_spectral_centroid()
    
    # Should return the same tuple (cached)
    assert result1 is result2


def test_audio_analyzer_analyze_all():
    """Test analyze_all convenience method."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_beats_120bpm.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    results = analyzer.analyze_all()
    
    # Check that all keys are present
    assert 'beats' in results
    assert 'onsets' in results
    assert 'energy' in results
    assert 'spectral_centroid' in results
    
    # Check types
    assert isinstance(results['beats'], np.ndarray)
    assert isinstance(results['onsets'], np.ndarray)
    assert isinstance(results['energy'], tuple)
    assert isinstance(results['spectral_centroid'], tuple)
    
    # Check that results match individual method calls
    assert np.array_equal(results['beats'], analyzer.analyze_beats())
    assert np.array_equal(results['onsets'], analyzer.analyze_onsets())
    
    energy_times, energy_values = analyzer.analyze_energy()
    result_energy_times, result_energy_values = results['energy']
    assert np.array_equal(result_energy_times, energy_times)
    assert np.array_equal(result_energy_values, energy_values)


def test_audio_analyzer_silent_audio():
    """Test analysis on silent audio (edge case)."""
    from engine.audio.analyzer import AudioAnalyzer
    
    audio_path = FIXTURES_DIR / "test_silent.wav"
    analyzer = AudioAnalyzer(audio_path)
    
    # Should not crash on silent audio
    beats = analyzer.analyze_beats()
    onsets = analyzer.analyze_onsets()
    times, energy = analyzer.analyze_energy()
    times_sc, centroid = analyzer.analyze_spectral_centroid()
    
    # May have no beats/onsets detected
    assert isinstance(beats, np.ndarray)
    assert isinstance(onsets, np.ndarray)
    
    # Energy should be very low
    assert np.all(energy < 0.1)
    
    # Should still have time series data
    assert len(times) > 0
    assert len(times_sc) > 0


def test_audio_analyzer_multiple_formats():
    """Test loading different audio formats."""
    # This test would require test files in different formats
    # For now, we only have WAV files
    pytest.skip("Requires test files in multiple formats (MP3, OGG, etc.)")


def test_audio_analyzer_corrupted_file():
    """Test handling of corrupted audio files."""
    from engine.audio.analyzer import AudioAnalyzer
    
    # Create a fake corrupted file
    corrupted_path = FIXTURES_DIR / "corrupted.wav"
    corrupted_path.write_bytes(b"not a valid audio file")
    
    try:
        with pytest.raises(ValueError, match="Failed to load audio file"):
            AudioAnalyzer(corrupted_path)
    finally:
        # Clean up
        if corrupted_path.exists():
            corrupted_path.unlink()
