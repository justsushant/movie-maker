"""Property-based tests for AudioSync."""

from __future__ import annotations
import pytest
import numpy as np
from hypothesis import given, strategies as st, assume, settings

from engine.audio.sync import AudioSync


# Strategies for generating audio analysis data
@st.composite
def sorted_timestamps(draw, min_value=0.0, max_value=10.0, min_size=0, max_size=50):
    """Generate sorted timestamp arrays."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    if size == 0:
        return np.array([])
    
    timestamps = draw(st.lists(
        st.floats(min_value=min_value, max_value=max_value, allow_nan=False, allow_infinity=False),
        min_size=size,
        max_size=size
    ))
    return np.array(sorted(timestamps))


@st.composite
def time_series_data(draw, min_size=0, max_size=50):
    """Generate time-series data (timestamps, values)."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    if size == 0:
        return np.array([]), np.array([])
    
    timestamps = draw(sorted_timestamps(min_size=size, max_size=size))
    values = draw(st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=size,
        max_size=size
    ))
    return timestamps, np.array(values)


@st.composite
def audio_sync_data(draw):
    """Generate complete AudioSync initialization data."""
    beats = draw(sorted_timestamps())
    onsets = draw(sorted_timestamps())
    energy_times, energy_values = draw(time_series_data())
    spectral_times, spectral_values = draw(time_series_data())
    
    return {
        'beats': beats,
        'onsets': onsets,
        'energy_times': energy_times,
        'energy_values': energy_values,
        'spectral_times': spectral_times,
        'spectral_values': spectral_values
    }


@settings(max_examples=100)
@given(audio_sync_data())
def test_property_audio_sync_stores_all_analysis_results(data):
    """
    Property 20: AudioSync Stores All Analysis Results
    
    For any AudioAnalyzer results, when AudioSync is initialized,
    all beats, onsets, energy data, and spectral data should be
    accessible through the AudioSync object.
    
    Validates: Requirements 9.2
    Tag: Feature: video-engine-phase-3, Property 20
    """
    audio_sync = AudioSync(**data)
    
    # Verify all data is stored
    assert np.array_equal(audio_sync.beats, data['beats']), "Beats should be stored"
    assert np.array_equal(audio_sync.onsets, data['onsets']), "Onsets should be stored"
    assert np.array_equal(audio_sync.energy_times, data['energy_times']), "Energy times should be stored"
    assert np.array_equal(audio_sync.energy_values, data['energy_values']), "Energy values should be stored"
    assert np.array_equal(audio_sync.spectral_times, data['spectral_times']), "Spectral times should be stored"
    assert np.array_equal(audio_sync.spectral_values, data['spectral_values']), "Spectral values should be stored"


@settings(max_examples=100)
@given(
    time_series_data(min_size=2, max_size=20),
    st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)
)
def test_property_audio_sync_interpolates_time_series_data(time_series, query_time):
    """
    Property 21: AudioSync Interpolates Time-Series Data
    
    For any time t between two analysis frames, AudioSync interpolation methods
    (get_energy_at_time, get_spectral_centroid_at_time) should return values
    between the two neighboring frame values.
    
    Validates: Requirements 9.3, 9.4
    Tag: Feature: video-engine-phase-3, Property 21
    """
    times, values = time_series
    
    # Skip if we don't have enough data
    assume(len(times) >= 2)
    
    # Create AudioSync with energy data
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=np.array([]),
        energy_times=times,
        energy_values=values,
        spectral_times=times,
        spectral_values=values
    )
    
    # Test energy interpolation
    energy = audio_sync.get_energy_at_time(query_time)
    
    if query_time < times[0]:
        # Before first frame - should return first value
        assert energy == values[0], "Should return first value before first frame"
    elif query_time > times[-1]:
        # After last frame - should return last value
        assert energy == values[-1], "Should return last value after last frame"
    else:
        # Between frames - should be between min and max values
        min_val = np.min(values)
        max_val = np.max(values)
        assert min_val <= energy <= max_val, \
            f"Interpolated value {energy} should be between {min_val} and {max_val}"
    
    # Test spectral centroid interpolation
    centroid = audio_sync.get_spectral_centroid_at_time(query_time)
    
    if query_time < times[0]:
        assert centroid == values[0], "Should return first value before first frame"
    elif query_time > times[-1]:
        assert centroid == values[-1], "Should return last value after last frame"
    else:
        min_val = np.min(values)
        max_val = np.max(values)
        assert min_val <= centroid <= max_val, \
            f"Interpolated value {centroid} should be between {min_val} and {max_val}"


@settings(max_examples=100)
@given(
    sorted_timestamps(min_size=1, max_size=20),
    st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)
)
def test_property_audio_sync_finds_nearest_beat(beats, query_time):
    """
    Property 22: AudioSync Finds Nearest Beat
    
    For any time t and beat array, get_nearest_beat should return
    the beat timestamp with minimum absolute distance to t.
    
    Validates: Requirements 9.5
    Tag: Feature: video-engine-phase-3, Property 22
    """
    assume(len(beats) > 0)
    
    audio_sync = AudioSync(
        beats=beats,
        onsets=np.array([]),
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    nearest_beat = audio_sync.get_nearest_beat(query_time)
    
    # Verify nearest beat is not None
    assert nearest_beat is not None, "Should return a beat"
    
    # Verify it's actually in the beats array
    assert nearest_beat in beats, "Returned beat should be in beats array"
    
    # Verify it's the closest beat
    distances = np.abs(beats - query_time)
    min_distance = np.min(distances)
    actual_distance = abs(nearest_beat - query_time)
    
    assert abs(actual_distance - min_distance) < 1e-6, \
        f"Returned beat should be closest (distance {actual_distance} vs min {min_distance})"


@settings(max_examples=100)
@given(
    sorted_timestamps(min_size=0, max_size=20),
    st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False)
)
def test_property_audio_sync_detects_onset_windows(onsets, query_time, duration):
    """
    Property 23: AudioSync Detects Onset Windows
    
    For any time t, duration d, and onset array, is_onset_active should
    return True if and only if at least one onset timestamp falls in
    the interval [t, t+d].
    
    Validates: Requirements 9.6
    Tag: Feature: video-engine-phase-3, Property 23
    """
    audio_sync = AudioSync(
        beats=np.array([]),
        onsets=onsets,
        energy_times=np.array([]),
        energy_values=np.array([]),
        spectral_times=np.array([]),
        spectral_values=np.array([])
    )
    
    is_active = audio_sync.is_onset_active(query_time, duration)
    
    # Manually check if any onset is in the window
    if len(onsets) == 0:
        expected = False
    else:
        expected = np.any((onsets >= query_time) & (onsets <= query_time + duration))
    
    assert is_active == expected, \
        f"is_onset_active returned {is_active} but expected {expected} " \
        f"for time {query_time}, duration {duration}, onsets {onsets}"
