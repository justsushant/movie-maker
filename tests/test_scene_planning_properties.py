"""Property-based tests for scene planning with audio."""

from __future__ import annotations
import pytest
import numpy as np
from pathlib import Path
import tempfile
from hypothesis import given, strategies as st, assume, settings
from scipy.io import wavfile

from engine.scene import Scene, ImageClip, Transition, TransitionType, BeatSync
from engine.planner import ScenePlanner
from engine.image_loader import ImageLoader


# Strategy for generating test images
@st.composite
def image_path_strategy(draw):
    """Get path to a test image."""
    # Use existing test image
    image_path = Path("tests/fixtures/images/landscape_1920x1080.png")
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path


# Strategy for generating test audio
@st.composite
def audio_file_strategy(draw):
    """Generate a temporary audio file."""
    duration = draw(st.floats(min_value=1.0, max_value=3.0))
    sample_rate = 22050
    
    # Generate sine wave with beats
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 120  # 120 BPM
    audio = np.sin(2 * np.pi * 2 * t)  # 2 Hz = 120 BPM
    audio = (audio * 0.5 * 32767).astype(np.int16)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_path = Path(temp_file.name)
    wavfile.write(temp_path, sample_rate, audio)
    temp_file.close()
    
    return temp_path


@settings(max_examples=20, deadline=10000)
@given(image_path_strategy(), audio_file_strategy())
def test_property_scene_with_audio_triggers_analysis(image_path, audio_path):
    """
    Property 24: Scene with Audio Triggers Analysis
    
    For any scene with a valid audio path, ScenePlanner should create
    an AudioSync object and store it in the ResolvedTimeline.
    
    Validates: Requirements 10.2, 10.3
    Tag: Feature: video-engine-phase-3, Property 24
    """
    try:
        # Create scene with audio
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            audio=audio_path,
            clips=[
                ImageClip(source=image_path, duration=2.0)
            ]
        )
        
        # Plan scene
        planner = ScenePlanner()
        image_loader = ImageLoader()
        timeline = planner.plan(scene, image_loader)
        
        # Verify audio analysis was triggered
        assert timeline.audio_sync is not None, \
            "AudioSync should be created when scene has audio"
        
        # Verify AudioSync has data
        assert hasattr(timeline.audio_sync, 'beats'), "AudioSync should have beats"
        assert hasattr(timeline.audio_sync, 'onsets'), "AudioSync should have onsets"
        assert hasattr(timeline.audio_sync, 'energy_times'), "AudioSync should have energy_times"
        assert hasattr(timeline.audio_sync, 'energy_values'), "AudioSync should have energy_values"
    
    finally:
        # Clean up temporary audio file
        audio_path.unlink()


@settings(max_examples=20, deadline=5000)
@given(image_path_strategy())
def test_property_scene_without_audio_skips_analysis(image_path):
    """
    Property 25: Scene without Audio Skips Analysis
    
    For any scene with audio=None, ScenePlanner should create a
    ResolvedTimeline with audio_sync=None.
    
    Validates: Requirements 10.5
    Tag: Feature: video-engine-phase-3, Property 25
    """
    # Create scene without audio
    scene = Scene(
        resolution=(640, 480),
        fps=30,
        audio=None,  # No audio
        clips=[
            ImageClip(source=image_path, duration=2.0)
        ]
    )
    
    # Plan scene
    planner = ScenePlanner()
    image_loader = ImageLoader()
    timeline = planner.plan(scene, image_loader)
    
    # Verify audio analysis was skipped
    assert timeline.audio_sync is None, \
        "AudioSync should be None when scene has no audio"
