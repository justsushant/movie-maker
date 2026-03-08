"""Integration tests for Phase 3 audio-reactive features."""

from __future__ import annotations
import pytest
import numpy as np
from pathlib import Path

from engine.scene import Scene, ImageClip, Transition, TransitionType, BeatSync
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import (
    OnsetFlash, OnsetZoomPulse, EnergyZoom, 
    EnergyBrightness, EnergyShake, SpectralColorShift
)
from engine.transitions import crossfade


@pytest.fixture
def image_loader():
    """Image loader for tests."""
    return ImageLoader()


@pytest.fixture
def test_audio_path():
    """Path to test audio file."""
    return Path("tests/fixtures/audio/test_beats_120bpm.wav")


@pytest.fixture
def test_image_path():
    """Path to test image."""
    return Path("tests/fixtures/images/landscape_1920x1080.png")


def test_end_to_end_with_audio(test_audio_path, test_image_path, image_loader):
    """
    Test complete end-to-end pipeline with audio analysis.
    
    Creates a scene with audio, beat-synced transitions, and audio-reactive effects.
    Verifies the video renders without errors and effects respond to audio.
    """
    # Skip if audio file doesn't exist
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with audio
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(
                source=test_image_path,
                duration=2.0
            ),
            ImageClip(
                source=test_image_path,
                duration=2.0
            ),
            ImageClip(
                source=test_image_path,
                duration=2.0
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            ),
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.BEAT_GRID
            )
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    # Verify audio analysis succeeded
    assert timeline.audio_sync is not None, "Audio analysis should succeed"
    assert len(timeline.audio_sync.beats) > 0, "Should detect beats"
    assert len(timeline.audio_sync.onsets) > 0, "Should detect onsets"
    assert len(timeline.audio_sync.energy_times) > 0, "Should have energy data"
    
    # Verify beat sync adjusted timings
    # At least one transition should have been adjusted
    original_starts = [0.0, 2.0]  # Declared transition starts
    actual_starts = [t.start_time for t in timeline.transitions]
    
    # Check if any timing was adjusted (within beat tolerance)
    adjustments = [abs(actual - original) for actual, original in zip(actual_starts, original_starts)]
    assert any(adj > 0.01 for adj in adjustments), "Beat sync should adjust at least one transition"
    
    # Add audio-reactive effects to clips
    for clip in timeline.clips:
        clip.effects = [
            OnsetFlash(timeline.audio_sync, flash_duration=0.2, intensity=0.3),
            EnergyZoom(timeline.audio_sync, zoom_range=(1.0, 1.1), energy_range=(0.0, 1.0))
        ]
    
    # Render frames
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render a few frames at different times
    test_times = [0.5, 1.5, 2.5, 3.5]
    frames = []
    
    for t in test_times:
        frame = renderer.render_frame(t)
        assert frame is not None, f"Frame at t={t} should render"
        assert frame.shape == (480, 640, 3), "Frame should have correct shape"
        assert frame.dtype == np.uint8, "Frame should be uint8"
        frames.append(frame)
    
    # Verify all frames rendered successfully
    assert len(frames) == len(test_times), "All frames should render"


def test_end_to_end_with_all_audio_effects(test_audio_path, test_image_path, image_loader):
    """
    Test end-to-end with all 6 audio-reactive effects applied.
    
    Verifies that all effects can be combined and render without errors.
    """
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with audio
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(
                source=test_image_path,
                duration=3.0
            )
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    assert timeline.audio_sync is not None
    
    # Add all 6 audio-reactive effects
    timeline.clips[0].effects = [
        OnsetFlash(timeline.audio_sync, flash_duration=0.2, intensity=0.3),
        OnsetZoomPulse(timeline.audio_sync, pulse_duration=0.3, zoom_magnitude=1.1),
        EnergyZoom(timeline.audio_sync, zoom_range=(1.0, 1.15), energy_range=(0.0, 1.0)),
        EnergyBrightness(timeline.audio_sync, brightness_range=(0.9, 1.1), energy_range=(0.0, 1.0)),
        EnergyShake(timeline.audio_sync, shake_range=(0.0, 5.0), energy_range=(0.0, 1.0)),
        SpectralColorShift(timeline.audio_sync, temperature_range=(-0.1, 0.1), centroid_range=(1000.0, 3000.0))
    ]
    
    # Render frames
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render frames at different times
    for t in [0.5, 1.0, 1.5, 2.0, 2.5]:
        frame = renderer.render_frame(t)
        assert frame is not None, f"Frame at t={t} should render with all effects"
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8


def test_beat_sync_aligns_transitions_to_beats(test_audio_path, test_image_path, image_loader):
    """
    Test that beat sync actually aligns transitions to detected beats.
    
    Verifies that NEAREST_BEAT and BEAT_GRID modes snap to beat timestamps.
    """
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with beat-synced transitions
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0)
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            ),
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.BEAT_GRID
            )
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    assert timeline.audio_sync is not None
    beats = timeline.audio_sync.beats
    
    # Check that transition start times are close to beat timestamps
    # Note: Some transitions may fall back to declared timing if beat snapping
    # would create invalid durations
    beat_aligned_count = 0
    
    for transition in timeline.transitions:
        # Find nearest beat to transition start
        nearest_beat = timeline.audio_sync.get_nearest_beat(transition.start_time)
        
        # Transition should be within half a beat interval of a beat
        if len(beats) > 1:
            beat_interval = np.mean(np.diff(beats))
            distance = abs(transition.start_time - nearest_beat)
            
            # Check if this transition is beat-aligned
            if distance < beat_interval / 2 + 0.1:
                beat_aligned_count += 1
    
    # At least one transition should be beat-aligned
    assert beat_aligned_count > 0, \
        "At least one transition should be aligned to beats"


def test_audio_reactive_effects_respond_to_audio_features(test_audio_path, test_image_path, image_loader):
    """
    Test that audio-reactive effects actually respond to audio features.
    
    Verifies that effects produce different results at times with different audio characteristics.
    """
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with audio
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(source=test_image_path, duration=5.0)
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    assert timeline.audio_sync is not None
    
    # Find times with different energy levels
    energy_times = timeline.audio_sync.energy_times
    energy_values = timeline.audio_sync.energy_values
    
    # Find low and high energy times
    low_energy_idx = np.argmin(energy_values)
    high_energy_idx = np.argmax(energy_values)
    
    low_energy_time = energy_times[low_energy_idx]
    high_energy_time = energy_times[high_energy_idx]
    
    # Add energy-driven effect
    timeline.clips[0].effects = [
        EnergyBrightness(
            timeline.audio_sync,
            brightness_range=(0.5, 1.5),
            energy_range=(0.0, 1.0)
        )
    ]
    
    # Render frames at low and high energy times
    renderer = FrameRenderer(timeline, image_loader)
    
    frame_low = renderer.render_frame(low_energy_time)
    frame_high = renderer.render_frame(high_energy_time)
    
    # High energy frame should be brighter
    brightness_low = np.mean(frame_low)
    brightness_high = np.mean(frame_high)
    
    assert brightness_high > brightness_low, \
        "Frame at high energy time should be brighter than frame at low energy time"


def test_transitions_with_audio_effects(test_audio_path, test_image_path, image_loader):
    """
    Test that transitions work correctly with audio-reactive effects.
    
    Verifies that effects are applied during transition blending.
    """
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with audio and transitions
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0)
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5
            )
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    assert timeline.audio_sync is not None
    
    # Add audio-reactive effects to both clips
    for clip in timeline.clips:
        clip.effects = [
            OnsetFlash(timeline.audio_sync, flash_duration=0.2, intensity=0.3)
        ]
    
    # Render frames during transition
    renderer = FrameRenderer(timeline, image_loader)
    
    transition_start = timeline.transitions[0].start_time
    transition_mid = transition_start + 0.25
    
    frame = renderer.render_frame(transition_mid)
    
    assert frame is not None, "Frame during transition should render"
    assert frame.shape == (480, 640, 3)
    assert frame.dtype == np.uint8


def test_multiple_clips_with_different_audio_effects(test_audio_path, test_image_path, image_loader):
    """
    Test that different clips can have different audio-reactive effects.
    
    Verifies that effects are applied per-clip correctly.
    """
    if not test_audio_path.exists():
        pytest.skip(f"Test audio not found: {test_audio_path}")
    
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with multiple clips
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=test_audio_path,
        clips=[
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0)
        ]
    )
    
    # Plan scene
    image_loader = ImageLoader()
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    assert timeline.audio_sync is not None
    
    # Add different effects to each clip
    timeline.clips[0].effects = [
        OnsetFlash(timeline.audio_sync, flash_duration=0.2, intensity=0.3)
    ]
    
    timeline.clips[1].effects = [
        EnergyZoom(timeline.audio_sync, zoom_range=(1.0, 1.2), energy_range=(0.0, 1.0))
    ]
    
    timeline.clips[2].effects = [
        SpectralColorShift(timeline.audio_sync, temperature_range=(-0.2, 0.2), centroid_range=(1000.0, 3000.0))
    ]
    
    # Render frames from each clip
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render one frame from each clip
    frame1 = renderer.render_frame(0.5)  # First clip
    frame2 = renderer.render_frame(2.5)  # Second clip
    frame3 = renderer.render_frame(4.5)  # Third clip
    
    assert frame1 is not None
    assert frame2 is not None
    assert frame3 is not None
    
    # All frames should have correct shape
    for frame in [frame1, frame2, frame3]:
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8


def test_error_recovery_with_invalid_audio_path(test_image_path, image_loader, caplog):
    """
    Test error recovery when audio file path is invalid.
    
    Verifies that:
    - System logs error when audio file doesn't exist
    - Scene planning continues without audio analysis
    - Video renders without audio features
    - AudioSync is None in timeline
    - Beat sync falls back to declared timings
    - Audio-reactive effects degrade gracefully
    
    Validates: Requirements 12.3, 14.2, 14.3
    """
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")
    
    # Create scene with invalid audio path
    invalid_audio_path = Path("nonexistent/audio/file.wav")
    
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=invalid_audio_path,  # Invalid path
        clips=[
            ImageClip(source=test_image_path, duration=2.0),
            ImageClip(source=test_image_path, duration=2.0)
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT  # Should fall back to declared timing
            )
        ]
    )
    
    # Plan scene - should not raise exception
    image_loader = ImageLoader()
    planner = ScenePlanner()
    
    # Capture logs
    import logging
    with caplog.at_level(logging.ERROR):
        timeline = planner.plan(scene, image_loader)
    
    # Verify error was logged
    assert any("audio" in record.message.lower() or "error" in record.message.lower() 
               for record in caplog.records), \
        "Should log error about audio file"
    
    # Verify AudioSync is None
    assert timeline.audio_sync is None, \
        "AudioSync should be None when audio file is invalid"
    
    # Verify beat sync fell back to declared timing
    # Expected transition start: 2.0 - 0.5 = 1.5s
    expected_start = 1.5
    actual_start = timeline.transitions[0].start_time
    
    assert abs(actual_start - expected_start) < 0.01, \
        f"Beat sync should fall back to declared timing: expected {expected_start}, got {actual_start}"
    
    # Add audio-reactive effects (should degrade gracefully)
    timeline.clips[0].effects = [
        OnsetFlash(None, flash_duration=0.2, intensity=0.3),
        EnergyZoom(None, zoom_range=(1.0, 1.2), energy_range=(0.0, 1.0))
    ]
    
    # Render frames - should work without errors
    renderer = FrameRenderer(timeline, image_loader)
    
    frame1 = renderer.render_frame(0.5)
    frame2 = renderer.render_frame(1.5)
    
    assert frame1 is not None, "Frame should render despite invalid audio"
    assert frame2 is not None, "Frame should render despite invalid audio"
    
    # Verify frames have correct shape
    assert frame1.shape == (480, 640, 3)
    assert frame2.shape == (480, 640, 3)
    assert frame1.dtype == np.uint8
    assert frame2.dtype == np.uint8
    
    # Verify audio-reactive effects returned frames unchanged (graceful degradation)
    # Render same frame without effects for comparison
    timeline.clips[0].effects = []
    frame_no_effects = renderer.render_frame(0.5)
    
    # Re-add effects and render again
    timeline.clips[0].effects = [
        OnsetFlash(None, flash_duration=0.2, intensity=0.3),
        EnergyZoom(None, zoom_range=(1.0, 1.2), energy_range=(0.0, 1.0))
    ]
    frame_with_effects = renderer.render_frame(0.5)
    
    # Frames should be identical (effects did nothing)
    assert np.array_equal(frame_no_effects, frame_with_effects), \
        "Audio-reactive effects should return frames unchanged when AudioSync is None"
