"""Unit tests for ScenePlanner audio integration (Phase 3)."""

from __future__ import annotations
import pytest
from pathlib import Path

from engine.scene import Scene, ImageClip, MotionPreset
from engine.planner import ScenePlanner
from engine.image_loader import ImageLoader


# Test fixtures path
FIXTURES_DIR = Path(__file__).parent / "fixtures"
AUDIO_FIXTURES_DIR = FIXTURES_DIR / "audio"
IMAGE_FIXTURES_DIR = FIXTURES_DIR / "images"


def test_planner_scene_with_audio():
    """Test that ScenePlanner analyzes audio when scene.audio is provided."""
    # Create scene with audio
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync was created
    assert timeline.audio_sync is not None
    
    # Check that audio_sync has data
    assert len(timeline.audio_sync.beats) > 0
    assert len(timeline.audio_sync.energy_times) > 0
    assert len(timeline.audio_sync.energy_values) > 0


def test_planner_scene_without_audio():
    """Test that ScenePlanner skips audio analysis when scene.audio is None."""
    # Create scene without audio
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ]
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync is None
    assert timeline.audio_sync is None


def test_planner_scene_with_missing_audio_file():
    """Test that ScenePlanner handles missing audio files gracefully."""
    # Create scene with non-existent audio file
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        audio="nonexistent_audio.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    # Should not crash, should log error and continue
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync is None (graceful degradation)
    assert timeline.audio_sync is None
    
    # Check that timeline was still created successfully
    assert len(timeline.clips) == 1
    assert timeline.duration > 0


def test_planner_scene_with_corrupted_audio_file():
    """Test that ScenePlanner handles corrupted audio files gracefully."""
    # Create a corrupted audio file
    corrupted_path = AUDIO_FIXTURES_DIR / "corrupted_test.wav"
    corrupted_path.write_bytes(b"not a valid audio file")
    
    try:
        # Create scene with corrupted audio
        scene = Scene(
            clips=[
                ImageClip(
                    source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ],
            audio=corrupted_path
        )
        
        planner = ScenePlanner()
        image_loader = ImageLoader()
        
        # Should not crash, should log error and continue
        timeline = planner.plan(scene, image_loader)
        
        # Check that audio_sync is None (graceful degradation)
        assert timeline.audio_sync is None
        
        # Check that timeline was still created successfully
        assert len(timeline.clips) == 1
        assert timeline.duration > 0
        
    finally:
        # Clean up
        if corrupted_path.exists():
            corrupted_path.unlink()


def test_planner_audio_analysis_caching():
    """Test that audio analysis results are stored in timeline."""
    # Create scene with audio
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        audio=AUDIO_FIXTURES_DIR / "test_beats_120bpm.wav"
    )
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    timeline = planner.plan(scene, image_loader)
    
    # Check that audio_sync is accessible from timeline
    assert timeline.audio_sync is not None
    
    # Check that we can query audio features
    energy = timeline.audio_sync.get_energy_at_time(1.0)
    assert isinstance(energy, float)
    assert energy >= 0.0
    
    nearest_beat = timeline.audio_sync.get_nearest_beat(1.0)
    assert nearest_beat is not None
    assert isinstance(nearest_beat, float)


def test_planner_backward_compatibility():
    """Test that ScenePlanner works with scenes that don't have audio attribute."""
    # Create scene without audio attribute (backward compatibility)
    scene = Scene(
        clips=[
            ImageClip(
                source=IMAGE_FIXTURES_DIR / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ]
    )
    
    # Remove audio attribute if it exists (simulate old Scene)
    if hasattr(scene, 'audio'):
        delattr(scene, 'audio')
    
    planner = ScenePlanner()
    image_loader = ImageLoader()
    
    # Should not crash
    timeline = planner.plan(scene, image_loader)
    
    # Check that timeline was created successfully
    assert len(timeline.clips) == 1
    assert timeline.duration > 0
    
    # audio_sync should be None
    assert timeline.audio_sync is None
