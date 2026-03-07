"""Tests for frame renderer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.camera import Rect
from engine.image_loader import ImageLoader
from engine.planner import ResolvedClip, ResolvedTimeline
from engine.renderer import FrameRenderer
from engine.scene import MotionPreset


# ============================================================================
# Property-Based Tests
# ============================================================================

# Feature: video-engine-phase-1, Property 10: Frame Renderer Clip Selection
@settings(max_examples=100)
@given(
    num_clips=st.integers(min_value=1, max_value=5),
    clip_duration=st.floats(min_value=0.5, max_value=5.0),
    time_offset=st.floats(min_value=-1.0, max_value=1.0),
)
def test_property_frame_renderer_clip_selection(num_clips, clip_duration, time_offset):
    """
    Property 10: Frame Renderer Clip Selection
    
    For any resolved timeline and time value t, the frame renderer should
    identify the clip where start_time <= t < end_time, or return None if
    no such clip exists.
    
    Validates: Requirements 6.2
    """
    # Create mock clips with sequential timing
    clips = []
    for i in range(num_clips):
        start_time = i * clip_duration
        end_time = start_time + clip_duration
        
        # Create mock clip
        clip = Mock(spec=ResolvedClip)
        clip.source = Path(f"image{i}.jpg")
        clip.start_time = start_time
        clip.end_time = end_time
        clip.camera_path = lambda t: Rect(0, 0, 1920, 1080)
        
        clips.append(clip)
    
    # Create timeline
    timeline = ResolvedTimeline(
        clips=clips,
        resolution=(1920, 1080),
        fps=30,
        duration=num_clips * clip_duration
    )
    
    # Create renderer with mock image loader
    image_loader = Mock(spec=ImageLoader)
    renderer = FrameRenderer(timeline, image_loader)
    
    # Test various time values
    for i in range(num_clips):
        # Test at start of clip
        t_start = i * clip_duration
        active_clip = renderer._find_active_clip(t_start)
        assert active_clip is not None
        assert active_clip.start_time <= t_start < active_clip.end_time
        
        # Test in middle of clip
        t_mid = i * clip_duration + clip_duration / 2
        active_clip = renderer._find_active_clip(t_mid)
        assert active_clip is not None
        assert active_clip.start_time <= t_mid < active_clip.end_time
        
        # Test just before end of clip
        t_before_end = (i + 1) * clip_duration - 0.001
        active_clip = renderer._find_active_clip(t_before_end)
        assert active_clip is not None
        assert active_clip.start_time <= t_before_end < active_clip.end_time
    
    # Test at exact end time (should not find clip)
    t_end = num_clips * clip_duration
    active_clip = renderer._find_active_clip(t_end)
    assert active_clip is None
    
    # Test before first clip
    t_before = -0.5
    active_clip = renderer._find_active_clip(t_before)
    assert active_clip is None
    
    # Test after last clip
    t_after = num_clips * clip_duration + 1.0
    active_clip = renderer._find_active_clip(t_after)
    assert active_clip is None


# ============================================================================
# Unit Tests
# ============================================================================

@pytest.fixture
def mock_image_loader():
    """Create a mock image loader that returns test images."""
    loader = Mock(spec=ImageLoader)
    
    # Return a simple test image (100x100 RGB)
    test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
    loader.load.return_value = test_image
    
    return loader


@pytest.fixture
def simple_timeline():
    """Create a simple timeline with one clip."""
    clip = Mock(spec=ResolvedClip)
    clip.source = Path("test_image.jpg")
    clip.start_time = 0.0
    clip.end_time = 2.0
    clip.camera_path = lambda t: Rect(0, 0, 100, 100)
    
    return ResolvedTimeline(
        clips=[clip],
        resolution=(1920, 1080),
        fps=30,
        duration=2.0
    )


@pytest.fixture
def multi_clip_timeline():
    """Create a timeline with multiple clips."""
    clips = []
    
    for i in range(3):
        clip = Mock(spec=ResolvedClip)
        clip.source = Path(f"image{i}.jpg")
        clip.start_time = i * 2.0
        clip.end_time = (i + 1) * 2.0
        clip.camera_path = lambda t, i=i: Rect(i * 10, i * 10, 100, 100)
        clips.append(clip)
    
    return ResolvedTimeline(
        clips=clips,
        resolution=(1920, 1080),
        fps=30,
        duration=6.0
    )


def test_renderer_initialization(simple_timeline, mock_image_loader):
    """Test FrameRenderer initialization."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    assert renderer.timeline == simple_timeline
    assert renderer.image_loader == mock_image_loader
    assert renderer.output_width == 1920
    assert renderer.output_height == 1080


def test_render_frame_at_start(simple_timeline, mock_image_loader):
    """Test rendering frame at t=0."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(0.0)
    
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    mock_image_loader.load.assert_called_once()


def test_render_frame_in_middle(simple_timeline, mock_image_loader):
    """Test rendering frame in middle of clip."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(1.0)
    
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8


def test_render_frame_at_end(simple_timeline, mock_image_loader):
    """Test rendering frame at t=duration (should return black frame)."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(2.0)
    
    # Should return black frame (no clip active at exact end time)
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    assert np.all(frame == 0)  # Black frame


def test_render_frame_before_timeline(simple_timeline, mock_image_loader):
    """Test rendering frame before first clip."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(-0.5)
    
    # Should return black frame
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    assert np.all(frame == 0)


def test_render_frame_after_timeline(simple_timeline, mock_image_loader):
    """Test rendering frame after last clip."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(3.0)
    
    # Should return black frame
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    assert np.all(frame == 0)


def test_render_frame_between_clips(multi_clip_timeline, mock_image_loader):
    """Test rendering frame at exact boundary between clips."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    # At t=2.0, first clip ends and second clip starts
    # Should render second clip (start_time <= 2.0 < end_time)
    frame = renderer.render_frame(2.0)
    
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8


def test_find_active_clip_first_clip(multi_clip_timeline, mock_image_loader):
    """Test finding active clip in first clip."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    clip = renderer._find_active_clip(0.5)
    
    assert clip is not None
    assert clip.start_time == 0.0
    assert clip.end_time == 2.0


def test_find_active_clip_second_clip(multi_clip_timeline, mock_image_loader):
    """Test finding active clip in second clip."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    clip = renderer._find_active_clip(3.0)
    
    assert clip is not None
    assert clip.start_time == 2.0
    assert clip.end_time == 4.0


def test_find_active_clip_third_clip(multi_clip_timeline, mock_image_loader):
    """Test finding active clip in third clip."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    clip = renderer._find_active_clip(5.0)
    
    assert clip is not None
    assert clip.start_time == 4.0
    assert clip.end_time == 6.0


def test_find_active_clip_none_before(multi_clip_timeline, mock_image_loader):
    """Test finding active clip before timeline."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    clip = renderer._find_active_clip(-1.0)
    
    assert clip is None


def test_find_active_clip_none_after(multi_clip_timeline, mock_image_loader):
    """Test finding active clip after timeline."""
    renderer = FrameRenderer(multi_clip_timeline, mock_image_loader)
    
    clip = renderer._find_active_clip(7.0)
    
    assert clip is None


def test_render_frame_uses_image_loader_cache(simple_timeline, mock_image_loader):
    """Test that renderer uses image loader (which should cache)."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    # Render multiple frames
    renderer.render_frame(0.0)
    renderer.render_frame(0.5)
    renderer.render_frame(1.0)
    
    # Image loader should be called for each frame
    # (caching is handled by ImageLoader itself)
    assert mock_image_loader.load.call_count == 3


def test_render_frame_with_different_resolutions():
    """Test rendering with different output resolutions."""
    resolutions = [(1280, 720), (1920, 1080), (3840, 2160)]
    
    for width, height in resolutions:
        clip = Mock(spec=ResolvedClip)
        clip.source = Path("test.jpg")
        clip.start_time = 0.0
        clip.end_time = 1.0
        clip.camera_path = lambda t: Rect(0, 0, 100, 100)
        
        timeline = ResolvedTimeline(
            clips=[clip],
            resolution=(width, height),
            fps=30,
            duration=1.0
        )
        
        loader = Mock(spec=ImageLoader)
        loader.load.return_value = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        renderer = FrameRenderer(timeline, loader)
        frame = renderer.render_frame(0.5)
        
        assert frame.shape == (height, width, 3)


def test_render_empty_timeline():
    """Test rendering with empty timeline."""
    timeline = ResolvedTimeline(
        clips=[],
        resolution=(1920, 1080),
        fps=30,
        duration=0.0
    )
    
    loader = Mock(spec=ImageLoader)
    renderer = FrameRenderer(timeline, loader)
    
    # Should return black frame
    frame = renderer.render_frame(0.0)
    
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    assert np.all(frame == 0)


def test_render_frame_output_dtype(simple_timeline, mock_image_loader):
    """Test that rendered frame has correct dtype."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(0.5)
    
    assert frame.dtype == np.uint8


def test_render_frame_output_dimensions(simple_timeline, mock_image_loader):
    """Test that rendered frame has correct dimensions."""
    renderer = FrameRenderer(simple_timeline, mock_image_loader)
    
    frame = renderer.render_frame(0.5)
    
    # Should match timeline resolution (height, width, channels)
    assert frame.shape == (1080, 1920, 3)
