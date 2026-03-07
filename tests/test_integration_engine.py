"""Integration tests for complete video engine pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from engine.camera import compute_motion_path
from engine.image_loader import ImageLoader
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.scene import ImageClip, MotionPreset, Scene


@pytest.fixture
def test_images_dir():
    """Get path to test images directory."""
    return Path("tests/fixtures/images")


@pytest.fixture
def image_loader():
    """Create an image loader for tests."""
    return ImageLoader()


def test_complete_pipeline_single_clip(test_images_dir, image_loader):
    """Test complete pipeline: Scene → Planner → Renderer → Frames."""
    # Create a simple scene with one clip
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    # Plan the scene
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    
    # Verify timeline
    assert timeline.duration == 2.0
    assert len(timeline.clips) == 1
    assert timeline.resolution == (1920, 1080)
    assert timeline.fps == 30
    
    # Create renderer
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render frames at different times
    frame_0 = renderer.render_frame(0.0)
    frame_mid = renderer.render_frame(1.0)
    frame_end = renderer.render_frame(1.99)
    
    # Verify frame properties
    for frame in [frame_0, frame_mid, frame_end]:
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_complete_pipeline_multiple_clips(test_images_dir, image_loader):
    """Test pipeline with multiple clips."""
    # Create scene with 3 clips
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "landscape_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.KEN_BURNS_ZOOM_IN
            ),
            ImageClip(
                source=test_images_dir / "portrait_1080x1920.png",
                duration=1.5,
                motion=MotionPreset.PAN_LEFT
            ),
            ImageClip(
                source=test_images_dir / "square_1080x1080.png",
                duration=2.0,
                motion=MotionPreset.ZOOM_OUT
            ),
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    # Plan and render
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    renderer = FrameRenderer(timeline, image_loader)
    
    # Verify timeline
    assert timeline.duration == 4.5
    assert len(timeline.clips) == 3
    
    # Render frames from each clip
    frame_clip1 = renderer.render_frame(0.5)  # First clip
    frame_clip2 = renderer.render_frame(1.5)  # Second clip
    frame_clip3 = renderer.render_frame(3.0)  # Third clip
    
    # All frames should be valid
    for frame in [frame_clip1, frame_clip2, frame_clip3]:
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_render_all_frames_for_scene(test_images_dir, image_loader):
    """Test rendering all frames for a 2-second scene at 30fps."""
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "landscape_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.ZOOM_IN
            ),
            ImageClip(
                source=test_images_dir / "landscape_gradient_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.PAN_RIGHT
            ),
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render all frames
    fps = 30
    duration = 2.0
    num_frames = int(fps * duration)
    
    frames = []
    for i in range(num_frames):
        t = i / fps
        frame = renderer.render_frame(t)
        frames.append(frame)
    
    # Verify we got all frames
    assert len(frames) == num_frames
    
    # Verify all frames are valid
    for frame in frames:
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_pipeline_with_each_motion_preset(test_images_dir, image_loader):
    """Test rendering with each motion preset."""
    motion_presets = [
        MotionPreset.STATIC,
        MotionPreset.KEN_BURNS_ZOOM_IN,
        MotionPreset.KEN_BURNS_ZOOM_OUT,
        MotionPreset.PAN_LEFT,
        MotionPreset.PAN_RIGHT,
        MotionPreset.PAN_UP,
        MotionPreset.PAN_DOWN,
        MotionPreset.ZOOM_IN,
        MotionPreset.ZOOM_OUT,
    ]
    
    for preset in motion_presets:
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=preset
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        # Render a few frames
        frame_start = renderer.render_frame(0.0)
        frame_mid = renderer.render_frame(0.5)
        frame_end = renderer.render_frame(0.99)
        
        # Verify frames
        for frame in [frame_start, frame_mid, frame_end]:
            assert isinstance(frame, np.ndarray)
            assert frame.shape == (1080, 1920, 3)
            assert frame.dtype == np.uint8


def test_pipeline_with_different_image_formats(test_images_dir, image_loader):
    """Test pipeline with PNG and JPEG images."""
    images = [
        "landscape_1920x1080.png",
        "landscape_1280x720.jpg",
        "portrait_1080x1920.png",
        "square_1080x1080.png",
    ]
    
    for image_name in images:
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / image_name,
                    duration=1.0,
                    motion=MotionPreset.STATIC
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        frame = renderer.render_frame(0.5)
        
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_pipeline_with_different_aspect_ratios(test_images_dir, image_loader):
    """Test pipeline with landscape, portrait, and square images."""
    test_cases = [
        ("landscape_1920x1080.png", "landscape"),
        ("portrait_1080x1920.png", "portrait"),
        ("square_1080x1080.png", "square"),
    ]
    
    for image_name, aspect_type in test_cases:
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / image_name,
                    duration=1.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        frame = renderer.render_frame(0.5)
        
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_pipeline_with_different_output_resolutions(test_images_dir, image_loader):
    """Test pipeline with different output resolutions."""
    resolutions = [
        (1280, 720),   # 720p
        (1920, 1080),  # 1080p
        (3840, 2160),  # 4K
    ]
    
    for width, height in resolutions:
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.STATIC
                )
            ],
            resolution=(width, height),
            fps=30
        )
        
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        frame = renderer.render_frame(0.5)
        
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (height, width, 3)
        assert frame.dtype == np.uint8


def test_image_loader_caching_in_pipeline(test_images_dir):
    """Test that image loader caching works in pipeline."""
    # Create a fresh image loader
    loader = ImageLoader()
    
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "landscape_1920x1080.png",
                duration=2.0,
                motion=MotionPreset.STATIC
            )
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Image should be loaded once during planning
    assert len(loader._cache) == 1
    
    renderer = FrameRenderer(timeline, loader)
    
    # Render multiple frames
    for i in range(10):
        t = i * 0.1
        renderer.render_frame(t)
    
    # Cache should still have only one image
    assert len(loader._cache) == 1


def test_pipeline_with_small_and_large_images(test_images_dir, image_loader):
    """Test pipeline with very small and very large images."""
    test_cases = [
        "small_100x100.png",
        "large_3840x2160.jpg",
    ]
    
    for image_name in test_cases:
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / image_name,
                    duration=1.0,
                    motion=MotionPreset.ZOOM_IN
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        frame = renderer.render_frame(0.5)
        
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (1080, 1920, 3)
        assert frame.dtype == np.uint8


def test_pipeline_motion_smoothness(test_images_dir, image_loader):
    """Test that motion is smooth across frames."""
    # Use ZOOM_IN which will definitely show motion
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "landscape_gradient_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.ZOOM_IN
            )
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    renderer = FrameRenderer(timeline, image_loader)
    
    # Render frames and check they're different (motion is happening)
    frames = []
    for i in range(5):
        t = i * 0.2
        frame = renderer.render_frame(t)
        frames.append(frame)
    
    # Frames should be different (motion is occurring)
    # Compare first and last frame - zoom should show visible change
    assert not np.array_equal(frames[0], frames[-1])


def test_pipeline_with_complex_scene(test_images_dir, image_loader):
    """Test pipeline with complex scene (checkerboard pattern)."""
    scene = Scene(
        clips=[
            ImageClip(
                source=test_images_dir / "checkerboard_1920x1080.png",
                duration=1.0,
                motion=MotionPreset.ZOOM_IN
            )
        ],
        resolution=(1920, 1080),
        fps=30
    )
    
    planner = ScenePlanner()
    timeline = planner.plan(scene, image_loader)
    renderer = FrameRenderer(timeline, image_loader)
    
    frame = renderer.render_frame(0.5)
    
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
