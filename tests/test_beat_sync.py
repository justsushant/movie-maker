"""Unit tests for beat synchronization (Phase 3)."""

from __future__ import annotations
import pytest
import numpy as np
from pathlib import Path

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType, BeatSync
from engine.planner import ScenePlanner
from engine.image_loader import ImageLoader
from engine.audio.sync import AudioSync


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / "fixtures"
AUDIO_FIXTURES_DIR = FIXTURES_DIR / "audio"
IMAGE_FIXTURES_DIR = FIXTURES_DIR / "images"


def test_beat_sync_none_preserves_timing():
    """Test that BeatSync.NONE preserves declared timings."""
    # Create scene with transitions using NONE sync
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NONE
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that transition timing is preserved
    assert len(timeline.transitions) == 1
    tr = timeline.transitions[0]
    
    # Transition should start at 2.0 (end of first clip)
    # But with overlap, it starts at clip2 start time
    # Clip 1: 0.0 - 2.0
    # Transition: 1.5 - 2.0 (0.5s duration, overlaps last 0.5s of clip1)
    # Clip 2: 1.5 - 3.5
    assert tr.start_time == pytest.approx(1.5)
    assert tr.end_time == pytest.approx(2.0)
    assert tr.end_time - tr.start_time == pytest.approx(0.5)


def test_beat_sync_nearest_beat_snaps_start():
    """Test that BeatSync.NEAREST_BEAT snaps transition start to nearest beat."""
    # Create scene with transition using NEAREST_BEAT sync
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync has beats
    assert timeline.audio_sync is not None
    assert len(timeline.audio_sync.beats) > 0
    
    # Check that transition was adjusted
    assert len(timeline.transitions) == 1
    tr = timeline.transitions[0]
    
    # Original transition would start at 1.5
    # Should be snapped to nearest beat
    # Find what the nearest beat to 1.5 would be
    nearest_beat = timeline.audio_sync.get_nearest_beat(1.5)
    
    # Transition should start at nearest beat
    assert tr.start_time == pytest.approx(nearest_beat, abs=0.01)
    
    # Duration should be preserved
    assert tr.end_time - tr.start_time == pytest.approx(0.5, abs=0.01)


def test_beat_sync_beat_grid_snaps_both_boundaries():
    """Test that BeatSync.BEAT_GRID snaps both start and end to beats."""
    # Create scene with transition using BEAT_GRID sync
    # Use longer duration to ensure different beats for start/end
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=3.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=3.0,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=1.0,  # Longer duration to span multiple beats
                sync=BeatSync.BEAT_GRID
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync has beats
    assert timeline.audio_sync is not None
    assert len(timeline.audio_sync.beats) > 0
    
    # Check that transition was adjusted
    assert len(timeline.transitions) == 1
    tr = timeline.transitions[0]
    
    # Original transition would be 2.0 - 3.0
    # Both boundaries should be snapped to nearest beats
    nearest_start_beat = timeline.audio_sync.get_nearest_beat(2.0)
    nearest_end_beat = timeline.audio_sync.get_nearest_beat(3.0)
    
    # If the beats would create non-positive duration, fallback to declared timing
    if nearest_end_beat <= nearest_start_beat:
        # Fallback case - should use declared timing
        assert tr.start_time == pytest.approx(2.0, abs=0.01)
        assert tr.end_time == pytest.approx(3.0, abs=0.01)
    else:
        # Normal case - should snap to beats
        assert tr.start_time == pytest.approx(nearest_start_beat, abs=0.01)
        assert tr.end_time == pytest.approx(nearest_end_beat, abs=0.01)
        
        # Duration should be positive
        assert tr.end_time > tr.start_time


def test_beat_sync_without_audio_uses_declared_timing():
    """Test that beat sync without audio falls back to declared timing."""
    # Create scene with beat sync but no audio
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT  # Sync mode specified but no audio
            )
        ]
        # No audio attribute
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync is None
    assert timeline.audio_sync is None
    
    # Check that transition uses declared timing (no beat sync applied)
    assert len(timeline.transitions) == 1
    tr = timeline.transitions[0]
    
    # Should use original timing
    assert tr.start_time == pytest.approx(1.5)
    assert tr.end_time == pytest.approx(2.0)


def test_beat_sync_preserves_positive_durations():
    """Test that beat snapping doesn't create negative clip durations."""
    # Create a mock AudioSync with beats that would cause issues
    beats = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    audio_sync = AudioSync(
        beats=beats,
        onsets=np.array([]),
        energy_times=np.array([0.0, 1.0]),
        energy_values=np.array([0.5, 0.5]),
        spectral_times=np.array([0.0, 1.0]),
        spectral_values=np.array([1500, 1500])
    )
    
    # Create scene with very short clips
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=0.6,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=0.6,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.3,
                sync=BeatSync.NEAREST_BEAT
            )
        ]
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    # Manually inject audio_sync for testing
    # We'll test the _apply_beat_sync method directly
    from engine.planner import ResolvedClip, TransitionRegion
    from engine.transitions import get_transition_function
    
    # Create initial timeline
    resolved_clips = [
        ResolvedClip(
            source=Path(IMAGE_FIXTURES_DIR / "landscape_1920x1080.png"),
            start_time=0.0,
            end_time=0.6,
            camera_path=lambda t: None,
            effects=[]
        ),
        ResolvedClip(
            source=Path(IMAGE_FIXTURES_DIR / "landscape_1920x1080.png"),
            start_time=0.3,
            end_time=0.9,
            camera_path=lambda t: None,
            effects=[]
        )
    ]
    
    transition_regions = [
        TransitionRegion(
            start_time=0.3,
            end_time=0.6,
            clip_a_index=0,
            clip_b_index=1,
            transition_function=get_transition_function(TransitionType.CROSSFADE),
            easing_function=lambda x: x
        )
    ]
    
    # Apply beat sync
    adjusted_clips, adjusted_transitions = planner._apply_beat_sync(
        scene, resolved_clips, transition_regions, audio_sync
    )
    
    # Check that all clips have positive durations
    for clip in adjusted_clips:
        assert clip.end_time > clip.start_time, f"Clip has non-positive duration: {clip.start_time} - {clip.end_time}"
    
    # Check that all transitions have positive durations
    for tr in adjusted_transitions:
        assert tr.end_time > tr.start_time, f"Transition has non-positive duration: {tr.start_time} - {tr.end_time}"


def test_beat_sync_multiple_transitions():
    """Test beat sync with multiple transitions."""
    # Create scene with multiple transitions
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
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
                sync=BeatSync.NONE
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that we have 2 transitions
    assert len(timeline.transitions) == 2
    
    # First transition should be beat-synced
    tr1 = timeline.transitions[0]
    nearest_beat = timeline.audio_sync.get_nearest_beat(1.5)
    assert tr1.start_time == pytest.approx(nearest_beat, abs=0.01)
    
    # Second transition should use declared timing (NONE mode)
    # But its timing is relative to the adjusted first transition
    tr2 = timeline.transitions[1]
    assert tr2.end_time > tr2.start_time


def test_beat_sync_with_missing_audio_file():
    """Test that beat sync handles missing audio files gracefully."""
    # Create scene with beat sync but missing audio file
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            ),
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        transitions=[
            Transition(
                type=TransitionType.CROSSFADE,
                duration=0.5,
                sync=BeatSync.NEAREST_BEAT
            )
        ],
        audio="nonexistent_audio.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    # Should not crash
    timeline = planner.plan(scene, image_loader)
    
    # audio_sync should be None (graceful degradation)
    assert timeline.audio_sync is None
    
    # Transition should use declared timing
    assert len(timeline.transitions) == 1
    tr = timeline.transitions[0]
    assert tr.start_time == pytest.approx(1.5)
    assert tr.end_time == pytest.approx(2.0)
