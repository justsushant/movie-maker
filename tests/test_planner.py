"""Tests for ScenePlanner and timeline resolution."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PIL import Image

from engine.image_loader import ImageLoader
from engine.planner import ResolvedClip, ResolvedTimeline, ScenePlanner
from engine.scene import ImageClip, MotionPreset, Scene


# ============================================================================
# Property-Based Tests
# ============================================================================


# Feature: video-engine-phase-1, Property 4: Timeline Clip Timing Consistency
@given(
    # Generate number of clips (1-10)
    num_clips=st.integers(min_value=1, max_value=10),
    # Generate clip durations
    durations=st.lists(
        st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=10
    ),
)
@settings(max_examples=100, deadline=None)
def test_property_timeline_clip_timing_consistency(num_clips: int, durations: list[float]):
    """
    Property 4: Timeline Clip Timing Consistency
    
    For any scene with multiple clips, when planning the timeline:
    - Each clip's start_time should equal the sum of all previous clip durations
    - Each clip's end_time should equal start_time + duration
    - Clips should be non-overlapping and sequential
    
    Validates: Requirements 5.1, 5.2
    """
    # Ensure we have the right number of durations
    durations = durations[:num_clips]
    if len(durations) < num_clips:
        durations.extend([1.0] * (num_clips - len(durations)))
    
    # Create temporary directory for test images
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test images and clips
        clips = []
        for i, duration in enumerate(durations):
            image_path = tmp_path / f"image_{i}.png"
            Image.new('RGB', (1920, 1080), color='red').save(image_path)
            clips.append(ImageClip(str(image_path), duration, MotionPreset.STATIC))
        
        # Create scene
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify timing consistency
        expected_start = 0.0
        for i, (clip, duration) in enumerate(zip(timeline.clips, durations)):
            # Check start_time equals sum of previous durations
            assert abs(clip.start_time - expected_start) < 1e-9, (
                f"Clip {i} start_time incorrect: expected={expected_start:.6f}, "
                f"got={clip.start_time:.6f}"
            )
            
            # Check end_time equals start_time + duration
            expected_end = expected_start + duration
            assert abs(clip.end_time - expected_end) < 1e-9, (
                f"Clip {i} end_time incorrect: expected={expected_end:.6f}, "
                f"got={clip.end_time:.6f}"
            )
            
            # Verify non-overlapping: next clip should start where this one ends
            if i < len(timeline.clips) - 1:
                next_clip = timeline.clips[i + 1]
                assert abs(next_clip.start_time - clip.end_time) < 1e-9, (
                    f"Clips {i} and {i+1} overlap or have gap: "
                    f"clip {i} ends at {clip.end_time:.6f}, "
                    f"clip {i+1} starts at {next_clip.start_time:.6f}"
                )
            
            expected_start += duration


# Feature: video-engine-phase-1, Property 13: Scene Planning Completeness
@given(
    # Generate number of clips (1-10)
    num_clips=st.integers(min_value=1, max_value=10),
    # Generate motion presets
    motion_presets=st.lists(
        st.sampled_from(list(MotionPreset)),
        min_size=1,
        max_size=10
    ),
)
@settings(max_examples=100, deadline=None)
def test_property_scene_planning_completeness(num_clips: int, motion_presets: list[MotionPreset]):
    """
    Property 13: Scene Planning Completeness
    
    For any valid scene with N clips, planning should produce a resolved timeline
    with exactly N resolved clips, each having a valid camera_path function.
    
    Validates: Requirements 5.6
    """
    # Ensure we have the right number of motion presets
    motion_presets = motion_presets[:num_clips]
    if len(motion_presets) < num_clips:
        motion_presets.extend([MotionPreset.STATIC] * (num_clips - len(motion_presets)))
    
    # Create temporary directory for test images
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test images and clips
        clips = []
        for i, motion in enumerate(motion_presets):
            image_path = tmp_path / f"image_{i}.png"
            Image.new('RGB', (1920, 1080), color='blue').save(image_path)
            clips.append(ImageClip(str(image_path), 2.0, motion))
        
        # Create scene
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify completeness: exactly N resolved clips
        assert len(timeline.clips) == num_clips, (
            f"Expected {num_clips} resolved clips, got {len(timeline.clips)}"
        )
        
        # Verify each clip has a valid camera_path function
        for i, clip in enumerate(timeline.clips):
            assert clip.camera_path is not None, f"Clip {i} has no camera_path"
            assert callable(clip.camera_path), f"Clip {i} camera_path is not callable"
            
            # Test that camera_path can be called and returns a Rect
            try:
                viewport = clip.camera_path(clip.start_time)
                assert hasattr(viewport, 'x'), f"Clip {i} camera_path doesn't return Rect"
                assert hasattr(viewport, 'y'), f"Clip {i} camera_path doesn't return Rect"
                assert hasattr(viewport, 'width'), f"Clip {i} camera_path doesn't return Rect"
                assert hasattr(viewport, 'height'), f"Clip {i} camera_path doesn't return Rect"
            except Exception as e:
                pytest.fail(f"Clip {i} camera_path raised exception: {e}")


# ============================================================================
# Unit Tests
# ============================================================================


class TestScenePlannerBasics:
    """Test basic ScenePlanner functionality."""
    
    def test_plan_empty_scene(self, tmp_path: Path):
        """Test planning an empty scene produces empty timeline."""
        scene = Scene(clips=[])
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        assert isinstance(timeline, ResolvedTimeline)
        assert len(timeline.clips) == 0
        assert timeline.duration == 0.0
        assert timeline.resolution == (1920, 1080)
        assert timeline.fps == 30
    
    def test_plan_single_clip_scene(self, tmp_path: Path):
        """Test planning a scene with a single clip."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create scene with one clip
        clip = ImageClip(str(image_path), duration=5.0, motion=MotionPreset.STATIC)
        scene = Scene(clips=[clip])
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify timeline
        assert len(timeline.clips) == 1
        assert timeline.duration == 5.0
        
        # Verify resolved clip
        resolved = timeline.clips[0]
        assert resolved.start_time == 0.0
        assert resolved.end_time == 5.0
        assert resolved.source == Path(image_path)
        assert resolved.camera_path is not None
    
    def test_plan_multi_clip_scene(self, tmp_path: Path):
        """Test planning a scene with multiple clips."""
        # Create test images
        image1_path = tmp_path / "image1.png"
        image2_path = tmp_path / "image2.png"
        image3_path = tmp_path / "image3.png"
        Image.new('RGB', (1920, 1080), color='red').save(image1_path)
        Image.new('RGB', (1920, 1080), color='green').save(image2_path)
        Image.new('RGB', (1920, 1080), color='blue').save(image3_path)
        
        # Create scene with three clips
        clips = [
            ImageClip(str(image1_path), duration=2.0, motion=MotionPreset.STATIC),
            ImageClip(str(image2_path), duration=3.0, motion=MotionPreset.ZOOM_IN),
            ImageClip(str(image3_path), duration=1.5, motion=MotionPreset.PAN_LEFT),
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify timeline
        assert len(timeline.clips) == 3
        assert timeline.duration == 6.5  # 2.0 + 3.0 + 1.5
        
        # Verify clip timings
        assert timeline.clips[0].start_time == 0.0
        assert timeline.clips[0].end_time == 2.0
        
        assert timeline.clips[1].start_time == 2.0
        assert timeline.clips[1].end_time == 5.0
        
        assert timeline.clips[2].start_time == 5.0
        assert timeline.clips[2].end_time == 6.5


class TestScenePlannerTimings:
    """Test timeline timing calculations."""
    
    def test_sequential_clip_timings(self, tmp_path: Path):
        """Test that clips are planned sequentially without gaps or overlaps."""
        # Create test images
        images = []
        for i in range(5):
            image_path = tmp_path / f"image{i}.png"
            Image.new('RGB', (1920, 1080), color='red').save(image_path)
            images.append(image_path)
        
        # Create clips with varying durations
        durations = [1.0, 2.5, 0.5, 3.0, 1.5]
        clips = [
            ImageClip(str(img), dur, MotionPreset.STATIC)
            for img, dur in zip(images, durations)
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify sequential timings
        expected_start = 0.0
        for i, (clip, duration) in enumerate(zip(timeline.clips, durations)):
            assert clip.start_time == expected_start
            assert clip.end_time == expected_start + duration
            expected_start += duration
        
        # Verify total duration
        assert timeline.duration == sum(durations)
    
    def test_timeline_duration_calculation(self, tmp_path: Path):
        """Test that timeline duration equals sum of clip durations."""
        # Create test images
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create clips with specific durations
        durations = [1.5, 2.0, 3.5, 1.0]
        clips = [
            ImageClip(str(image_path), dur, MotionPreset.STATIC)
            for dur in durations
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify duration
        expected_duration = sum(durations)
        assert timeline.duration == expected_duration
        assert timeline.clips[-1].end_time == expected_duration


class TestScenePlannerMotionPresets:
    """Test planning with different motion presets."""
    
    def test_plan_with_mixed_motion_presets(self, tmp_path: Path):
        """Test planning scene with mixed motion presets."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create clips with different motion presets
        clips = [
            ImageClip(str(image_path), 2.0, MotionPreset.STATIC),
            ImageClip(str(image_path), 2.0, MotionPreset.KEN_BURNS_ZOOM_IN),
            ImageClip(str(image_path), 2.0, MotionPreset.PAN_LEFT),
            ImageClip(str(image_path), 2.0, MotionPreset.ZOOM_OUT),
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify all clips have camera paths
        assert len(timeline.clips) == 4
        for clip in timeline.clips:
            assert clip.camera_path is not None
            # Test camera path can be called
            viewport = clip.camera_path(clip.start_time)
            assert viewport is not None
    
    def test_camera_path_uses_absolute_time(self, tmp_path: Path):
        """Test that camera paths use absolute timeline time."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create clips
        clips = [
            ImageClip(str(image_path), 3.0, MotionPreset.ZOOM_IN),
            ImageClip(str(image_path), 3.0, MotionPreset.ZOOM_IN),
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # First clip: starts at t=0, ends at t=3
        clip1 = timeline.clips[0]
        viewport_start1 = clip1.camera_path(0.0)
        viewport_mid1 = clip1.camera_path(1.5)
        viewport_end1 = clip1.camera_path(3.0)
        
        # Second clip: starts at t=3, ends at t=6
        clip2 = timeline.clips[1]
        viewport_start2 = clip2.camera_path(3.0)
        viewport_mid2 = clip2.camera_path(4.5)
        viewport_end2 = clip2.camera_path(6.0)
        
        # Both clips should have similar zoom patterns (ZOOM_IN)
        # Start viewports should be similar (full image)
        assert abs(viewport_start1.width - viewport_start2.width) < 10.0
        
        # End viewports should be similar (50% of image)
        assert abs(viewport_end1.width - viewport_end2.width) < 10.0


class TestScenePlannerResolutionAndFPS:
    """Test that planner preserves scene resolution and FPS."""
    
    def test_planner_preserves_resolution(self, tmp_path: Path):
        """Test that planner preserves scene resolution in timeline."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create scene with custom resolution
        clip = ImageClip(str(image_path), 5.0, MotionPreset.STATIC)
        scene = Scene(clips=[clip], resolution=(3840, 2160), fps=60)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify resolution and fps preserved
        assert timeline.resolution == (3840, 2160)
        assert timeline.fps == 60
    
    def test_planner_uses_default_resolution(self, tmp_path: Path):
        """Test that planner uses default resolution when not specified."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create scene with defaults
        clip = ImageClip(str(image_path), 5.0, MotionPreset.STATIC)
        scene = Scene(clips=[clip])
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify default resolution and fps
        assert timeline.resolution == (1920, 1080)
        assert timeline.fps == 30


class TestScenePlannerImageLoading:
    """Test that planner correctly loads images to get dimensions."""
    
    def test_planner_loads_images_for_dimensions(self, tmp_path: Path):
        """Test that planner loads images to determine dimensions."""
        # Create test images with different sizes
        image1_path = tmp_path / "image1.png"
        image2_path = tmp_path / "image2.png"
        Image.new('RGB', (1920, 1080), color='red').save(image1_path)
        Image.new('RGB', (3840, 2160), color='blue').save(image2_path)
        
        # Create clips
        clips = [
            ImageClip(str(image1_path), 2.0, MotionPreset.STATIC),
            ImageClip(str(image2_path), 2.0, MotionPreset.STATIC),
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify camera paths work (implying dimensions were loaded correctly)
        for clip in timeline.clips:
            viewport = clip.camera_path(clip.start_time)
            assert viewport.width > 0
            assert viewport.height > 0
    
    def test_planner_uses_image_loader_cache(self, tmp_path: Path):
        """Test that planner benefits from image loader cache."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create clips using same image
        clips = [
            ImageClip(str(image_path), 2.0, MotionPreset.STATIC),
            ImageClip(str(image_path), 2.0, MotionPreset.ZOOM_IN),
            ImageClip(str(image_path), 2.0, MotionPreset.PAN_LEFT),
        ]
        scene = Scene(clips=clips)
        
        # Plan timeline with shared loader
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify cache has only one entry (image loaded once)
        assert len(loader._cache) == 1
        
        # Verify all clips were planned successfully
        assert len(timeline.clips) == 3


class TestResolvedClipAttributes:
    """Test ResolvedClip dataclass attributes."""
    
    def test_resolved_clip_has_all_attributes(self, tmp_path: Path):
        """Test that ResolvedClip has all required attributes."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create and plan scene
        clip = ImageClip(str(image_path), 5.0, MotionPreset.STATIC)
        scene = Scene(clips=[clip])
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify ResolvedClip attributes
        resolved = timeline.clips[0]
        assert isinstance(resolved, ResolvedClip)
        assert isinstance(resolved.source, Path)
        assert isinstance(resolved.start_time, float)
        assert isinstance(resolved.end_time, float)
        assert callable(resolved.camera_path)
    
    def test_resolved_clip_source_is_path(self, tmp_path: Path):
        """Test that ResolvedClip source is converted to Path."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create clip with string path
        clip = ImageClip(str(image_path), 5.0, MotionPreset.STATIC)
        scene = Scene(clips=[clip])
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify source is Path object
        resolved = timeline.clips[0]
        assert isinstance(resolved.source, Path)
        assert resolved.source == Path(image_path)


class TestResolvedTimelineAttributes:
    """Test ResolvedTimeline dataclass attributes."""
    
    def test_resolved_timeline_has_all_attributes(self, tmp_path: Path):
        """Test that ResolvedTimeline has all required attributes."""
        # Create test image
        image_path = tmp_path / "test.png"
        Image.new('RGB', (1920, 1080), color='red').save(image_path)
        
        # Create and plan scene
        clip = ImageClip(str(image_path), 5.0, MotionPreset.STATIC)
        scene = Scene(clips=[clip], resolution=(1280, 720), fps=24)
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify ResolvedTimeline attributes
        assert isinstance(timeline, ResolvedTimeline)
        assert isinstance(timeline.clips, list)
        assert isinstance(timeline.resolution, tuple)
        assert isinstance(timeline.fps, int)
        assert isinstance(timeline.duration, float)
        
        # Verify values
        assert timeline.resolution == (1280, 720)
        assert timeline.fps == 24
        assert timeline.duration == 5.0
