"""Unit tests for AudioSync (Phase 3)."""

from __future__ import annotations
import pytest
import numpy as np


def test_audio_sync_initialization():
    """Test AudioSync initialization stores all data correctly."""
    from engine.audio.sync import AudioSync
    
    beats = np.array([0.5, 1.0, 1.5, 2.0])
    onsets = np.array([0.1, 0.6, 1.1, 1.6])
    energy_times = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    energy_values = np.array([0.2, 0.5, 0.8, 0.6, 0.3])
    spectral_times = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    spectral_values = np.array([1500, 1800, 2000, 1700, 1600])
    
    audio_sync = AudioSync(
        beats=beats,
        onsets=onsets,
        energy_times=energy_times,
        energy_values=energy_values,
        spectral_times=spectral_times,
        spectral_values=spectral_values
    )
    
    # Check all data is stored
    assert np.array_equal(audio_sync.beats, beats)
    assert np.array_equal(audio_sync.onsets, onsets)
    assert np.array_equal(audio_sync.energy_times, energy_times)
    assert np.array_equal(audio_sync.energy_values, energy_values)
    assert np.array_equal(audio_sync.spectral_times, spectral_times)
    assert np.array_equal(audio_sync.spectral_values, spectral_values)


def test_audio_sync_energy_interpolation():
    """Test get_energy_at_time interpolation with known values."""
    from engine.audio.sync import AudioSync
    
    energy_times = np.array([0.0, 1.0, 2.0])
    energy_values = np.array([0.0, 1.0, 0.0])
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=energy_times,
        energy_values=energy_values,
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Test exact points
    assert audio_sync.get_energy_at_time(0.0) == pytest.approx(0.0)
    assert audio_sync.get_energy_at_time(1.0) == pytest.approx(1.0)
    assert audio_sync.get_energy_at_time(2.0) == pytest.approx(0.0)
    
    # Test interpolation
    assert audio_sync.get_energy_at_time(0.5) == pytest.approx(0.5)
    assert audio_sync.get_energy_at_time(1.5) == pytest.approx(0.5)
    
    # Test before first frame (should return first value)
    assert audio_sync.get_energy_at_time(-1.0) == pytest.approx(0.0)
    
    # Test after last frame (should return last value)
    assert audio_sync.get_energy_at_time(3.0) == pytest.approx(0.0)


def test_audio_sync_energy_empty_data():
    """Test get_energy_at_time with empty data returns 0.0."""
    from engine.audio.sync import AudioSync
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    assert audio_sync.get_energy_at_time(1.0) == 0.0


def test_audio_sync_spectral_centroid_interpolation():
    """Test get_spectral_centroid_at_time interpolation with known values."""
    from engine.audio.sync import AudioSync
    
    spectral_times = np.array([0.0, 1.0, 2.0])
    spectral_values = np.array([1000.0, 2000.0, 1000.0])
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=spectral_times,
        spectral_values=spectral_values
    )
    
    # Test exact points
    assert audio_sync.get_spectral_centroid_at_time(0.0) == pytest.approx(1000.0)
    assert audio_sync.get_spectral_centroid_at_time(1.0) == pytest.approx(2000.0)
    assert audio_sync.get_spectral_centroid_at_time(2.0) == pytest.approx(1000.0)
    
    # Test interpolation
    assert audio_sync.get_spectral_centroid_at_time(0.5) == pytest.approx(1500.0)
    assert audio_sync.get_spectral_centroid_at_time(1.5) == pytest.approx(1500.0)
    
    # Test edge cases
    assert audio_sync.get_spectral_centroid_at_time(-1.0) == pytest.approx(1000.0)
    assert audio_sync.get_spectral_centroid_at_time(3.0) == pytest.approx(1000.0)


def test_audio_sync_spectral_centroid_empty_data():
    """Test get_spectral_centroid_at_time with empty data returns 0.0."""
    from engine.audio.sync import AudioSync
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    assert audio_sync.get_spectral_centroid_at_time(1.0) == 0.0


def test_audio_sync_get_nearest_beat():
    """Test get_nearest_beat with known beat array."""
    from engine.audio.sync import AudioSync
    
    beats = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    
    audio_sync = AudioSync(
        beats=beats,
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Test exact matches
    assert audio_sync.get_nearest_beat(0.5) == pytest.approx(0.5)
    assert audio_sync.get_nearest_beat(1.0) == pytest.approx(1.0)
    
    # Test between beats (should snap to nearest)
    assert audio_sync.get_nearest_beat(0.7) == pytest.approx(0.5)
    assert audio_sync.get_nearest_beat(0.8) == pytest.approx(1.0)
    assert audio_sync.get_nearest_beat(1.2) == pytest.approx(1.0)
    assert audio_sync.get_nearest_beat(1.3) == pytest.approx(1.5)
    
    # Test before first beat
    assert audio_sync.get_nearest_beat(0.0) == pytest.approx(0.5)
    
    # Test after last beat
    assert audio_sync.get_nearest_beat(3.0) == pytest.approx(2.5)


def test_audio_sync_get_nearest_beat_empty():
    """Test get_nearest_beat with no beats returns None."""
    from engine.audio.sync import AudioSync
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    assert audio_sync.get_nearest_beat(1.0) is None


def test_audio_sync_is_onset_active():
    """Test is_onset_active with known onset array."""
    from engine.audio.sync import AudioSync
    
    onsets = np.array([0.5, 1.0, 1.5, 2.0])
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=onsets,
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Test with onset in window
    assert audio_sync.is_onset_active(0.4, 0.2) is True  # onset at 0.5 is in [0.4, 0.6]
    assert audio_sync.is_onset_active(0.5, 0.1) is True  # onset at 0.5 is in [0.5, 0.6]
    assert audio_sync.is_onset_active(0.9, 0.2) is True  # onset at 1.0 is in [0.9, 1.1]
    
    # Test with no onset in window
    assert audio_sync.is_onset_active(0.0, 0.3) is False  # no onset in [0.0, 0.3]
    assert audio_sync.is_onset_active(0.6, 0.3) is False  # no onset in [0.6, 0.9]
    assert audio_sync.is_onset_active(2.5, 0.3) is False  # no onset in [2.5, 2.8]
    
    # Test edge case: onset exactly at end of window
    assert audio_sync.is_onset_active(0.3, 0.2) is True  # onset at 0.5 is at [0.3, 0.5]


def test_audio_sync_is_onset_active_empty():
    """Test is_onset_active with no onsets returns False."""
    from engine.audio.sync import AudioSync
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    assert audio_sync.is_onset_active(1.0, 0.5) is False


def test_audio_sync_get_closest_onset():
    """Test get_closest_onset with known onset array."""
    from engine.audio.sync import AudioSync
    
    onsets = np.array([0.5, 1.0, 1.5, 2.0])
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=onsets,
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Test within max_distance
    assert audio_sync.get_closest_onset(0.45, 0.1) == pytest.approx(0.5)
    assert audio_sync.get_closest_onset(0.55, 0.1) == pytest.approx(0.5)
    assert audio_sync.get_closest_onset(0.95, 0.1) == pytest.approx(1.0)
    
    # Test beyond max_distance
    assert audio_sync.get_closest_onset(0.3, 0.1) is None
    assert audio_sync.get_closest_onset(0.7, 0.1) is None
    
    # Test exact match
    assert audio_sync.get_closest_onset(1.0, 0.0) == pytest.approx(1.0)
    
    # Test with larger max_distance
    assert audio_sync.get_closest_onset(0.3, 0.3) == pytest.approx(0.5)


def test_audio_sync_get_closest_onset_empty():
    """Test get_closest_onset with no onsets returns None."""
    from engine.audio.sync import AudioSync
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    assert audio_sync.get_closest_onset(1.0, 0.5) is None


def test_audio_sync_interpolation_between_frames():
    """Test that interpolation returns values between neighboring frames."""
    from engine.audio.sync import AudioSync
    
    energy_times = np.array([0.0, 1.0, 2.0, 3.0])
    energy_values = np.array([0.2, 0.8, 0.4, 0.6])
    
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=energy_times,
        energy_values=energy_values,
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    # Test interpolation between frames
    # Between 0.0 (0.2) and 1.0 (0.8)
    val_0_5 = audio_sync.get_energy_at_time(0.5)
    assert 0.2 < val_0_5 < 0.8
    assert val_0_5 == pytest.approx(0.5)  # Linear interpolation
    
    # Between 1.0 (0.8) and 2.0 (0.4)
    val_1_5 = audio_sync.get_energy_at_time(1.5)
    assert 0.4 < val_1_5 < 0.8
    assert val_1_5 == pytest.approx(0.6)  # Linear interpolation
    
    # Between 2.0 (0.4) and 3.0 (0.6)
    val_2_5 = audio_sync.get_energy_at_time(2.5)
    assert 0.4 < val_2_5 < 0.6
    assert val_2_5 == pytest.approx(0.5)  # Linear interpolation
