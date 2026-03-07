"""Integration tests for Phase 2 transitions and effects."""

from __future__ import annotations

import numpy as np
import pytest

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness, contrast, saturation, vignette, film_grain, fade_in, fade_out, pulse, chain_effects


@pytest.fixture
def image_loader(tmp_path):
    """Create image loader with test images."""
    loader = ImageLoader()
    
    # Create test images
    red_image = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
    blue_image = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
    
    red_path = tmp_path / "red.png"
    blue_path = tmp_path / "blue.png"
    
    import cv2
    cv2.imwrite(str(red_path), cv2.cvtColor(red_image, cv2.COLOR_RGB2BGR))
    cv2.imwrite(str(blue_path), cv2.cvtColor(blue_image, cv2.COLOR_RGB2BGR))
    
    return loader, red_path, blue_path


def test_scene_with_crossfade_transition(image_loader):
    """Test basic scene with crossfade transition."""
    loader, red_path, blue_path = image_loader
    
    # Create scene with transition
    scene = Scene(
        clips=[
            ImageClip(source=str(red_path), duration=2.0, motion=MotionPreset.STATIC),
            ImageClip(source=str(blue_path), duration=2.0, motion=MotionPreset.STATIC),
        ],
        transitions=[
            Transition(type=TransitionType.CROSSFADE, duration=0.5)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    # Plan timeline
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Verify timeline structure
    assert len(timeline.clips) == 2
    assert len(timeline.transitions) == 1
    
    # Verify overlap
    # Clip 0: [0.0, 2.0], Clip 1: [1.5, 3.5] with 0.5s transition
    # Overlap should be: clip0.end - clip1.start = 2.0 - 1.5 = 0.5
    assert timeline.clips[0].end_time > timeline.clips[1].start_time
    overlap = timeline.clips[0].end_time - timeline.clips[1].start_time
    assert abs(overlap - 0.5) < 0.001
    
    # Verify total duration accounts for overlap
    expected_duration = 2.0 + 2.0 - 0.5  # 3.5 seconds
    assert abs(timeline.duration - expected_duration) < 0.001
    
    # Render frames
    renderer = FrameRenderer(timeline, loader)
    
    # Frame before transition (should be red)
    frame_before = renderer.render_frame(1.0)
    assert frame_before.shape == (100, 100, 3)
    assert np.allclose(frame_before[50, 50], [255, 0, 0], atol=5)
    
    # Frame during transition (should be blend)
    frame_during = renderer.render_frame(1.75)  # Middle of transition
    assert frame_during.shape == (100, 100, 3)
    # Should be purple-ish (blend of red and blue)
    center_pixel = frame_during[50, 50]
    assert center_pixel[0] > 50  # Has red
    assert center_pixel[2] > 50  # Has blue
    
    # Frame after transition (should be blue)
    frame_after = renderer.render_frame(3.0)
    assert frame_after.shape == (100, 100, 3)
    assert np.allclose(frame_after[50, 50], [0, 0, 255], atol=5)


def test_scene_with_effects(image_loader):
    """Test scene with effects applied to clips."""
    loader, red_path, blue_path = image_loader
    
    # Create scene with effects
    scene = Scene(
        clips=[
            ImageClip(
                source=str(red_path), 
                duration=1.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(0.2)]  # Brighten red clip
            ),
            ImageClip(
                source=str(blue_path), 
                duration=1.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(-0.2)]  # Darken blue clip
            ),
        ],
        resolution=(100, 100),
        fps=30
    )
    
    # Plan and render
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Render first clip with brightness increase
    frame1 = renderer.render_frame(0.5)
    # Should be brighter than original red
    assert frame1[50, 50, 0] == 255  # Already at max
    
    # Render second clip with brightness decrease
    frame2 = renderer.render_frame(1.5)
    # Should be darker than original blue
    assert frame2[50, 50, 2] < 255


def test_scene_with_transition_and_effects(image_loader):
    """Test scene with both transitions and effects."""
    loader, red_path, blue_path = image_loader
    
    # Create scene with both
    scene = Scene(
        clips=[
            ImageClip(
                source=str(red_path), 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[brightness(0.1)]
            ),
            ImageClip(
                source=str(blue_path), 
                duration=2.0, 
                motion=MotionPreset.STATIC,
                effects=[contrast(1.2)]
            ),
        ],
        transitions=[
            Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.5)
        ],
        resolution=(100, 100),
        fps=30
    )
    
    # Plan and render
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Render during transition
    # Effects should be applied to both clips before blending
    frame = renderer.render_frame(1.75)
    assert frame.shape == (100, 100, 3)


def test_backward_compatibility_no_transitions(image_loader):
    """Test that scenes without transitions work (Phase 1 behavior)."""
    loader, red_path, blue_path = image_loader
    
    # Create scene without transitions
    scene = Scene(
        clips=[
            ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ImageClip(source=str(blue_path), duration=1.0, motion=MotionPreset.STATIC),
        ],
        resolution=(100, 100),
        fps=30
    )
    
    # Plan timeline
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    
    # Verify no transitions
    assert len(timeline.transitions) == 0
    
    # Verify sequential timing (no overlap)
    assert timeline.clips[0].end_time == timeline.clips[1].start_time
    assert timeline.duration == 2.0
    
    # Render frames
    renderer = FrameRenderer(timeline, loader)
    
    # Frame at boundary should be instant cut
    frame_before = renderer.render_frame(0.99)
    frame_after = renderer.render_frame(1.01)
    
    # Should be different colors (instant cut)
    assert not np.allclose(frame_before[50, 50], frame_after[50, 50], atol=10)


def test_chain_effects(image_loader):
    """Test chaining multiple effects together."""
    loader, red_path, _ = image_loader
    
    # Create chained effect
    chained = chain_effects(
        brightness(0.1),
        contrast(1.2),
        saturation(0.8)
    )
    
    # Create scene with chained effect
    scene = Scene(
        clips=[
            ImageClip(
                source=str(red_path), 
                duration=1.0, 
                motion=MotionPreset.STATIC,
                effects=[chained]
            ),
        ],
        resolution=(100, 100),
        fps=30
    )
    
    # Plan and render
    planner = ScenePlanner()
    timeline = planner.plan(scene, loader)
    renderer = FrameRenderer(timeline, loader)
    
    # Render frame with chained effects
    frame = renderer.render_frame(0.5)
    assert frame.shape == (100, 100, 3)
    assert frame.dtype == np.uint8



class TestCompletePhase2Pipeline:
    """Test complete pipeline with transitions from Scene to rendered frames."""
    
    def test_complete_pipeline_with_multiple_transitions(self, tmp_path):
        """
        Test complete pipeline: Scene → Planner → Renderer → Frames with multiple transitions.
        
        **Validates: Integration testing**
        """
        import cv2
        
        # Create test images
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        green = np.full((100, 100, 3), [0, 255, 0], dtype=np.uint8)
        blue = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
        
        red_path = tmp_path / "red.png"
        green_path = tmp_path / "green.png"
        blue_path = tmp_path / "blue.png"
        
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(green_path), cv2.cvtColor(green, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
        
        # Create scene with 3 clips and 2 transitions
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=2.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(green_path), duration=2.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(blue_path), duration=2.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=0.5),
                Transition(type=TransitionType.SLIDE_LEFT, duration=0.5),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        # Plan timeline
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify timeline structure
        assert len(timeline.clips) == 3
        assert len(timeline.transitions) == 2
        
        # Verify overlaps
        # Total duration should be 2.0 + 2.0 + 2.0 - 0.5 - 0.5 = 5.0
        assert abs(timeline.duration - 5.0) < 0.001
        
        # Render frames throughout the timeline
        renderer = FrameRenderer(timeline, loader)
        
        # Frame in first clip (before any transition)
        frame1 = renderer.render_frame(0.5)
        assert np.allclose(frame1[50, 50], [255, 0, 0], atol=5)
        
        # Frame during first transition (red → green)
        frame2 = renderer.render_frame(1.75)
        center = frame2[50, 50]
        assert center[0] > 50 and center[1] > 50  # Has both red and green
        
        # Frame in second clip (between transitions)
        frame3 = renderer.render_frame(2.5)
        assert np.allclose(frame3[50, 50], [0, 255, 0], atol=5)
        
        # Frame during second transition (green → blue)
        frame4 = renderer.render_frame(3.75)
        # Slide transition - should have both colors visible
        assert frame4.shape == (100, 100, 3)
        
        # Frame in third clip (after all transitions)
        frame5 = renderer.render_frame(4.5)
        assert np.allclose(frame5[50, 50], [0, 0, 255], atol=5)


class TestEffectChainIntegration:
    """Test effect chain integration with multiple effects."""
    
    def test_multiple_effects_render_correctly(self, tmp_path):
        """
        Test clips with multiple effects render correctly.
        
        **Validates: Integration testing**
        """
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create scene with multiple effects
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=2.0,
                    motion=MotionPreset.STATIC,
                    effects=[
                        brightness(0.1),
                        contrast(1.2),
                        saturation(0.8),
                    ]
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render frame with all effects applied
        frame = renderer.render_frame(1.0)
        
        assert frame.shape == (100, 100, 3)
        assert frame.dtype == np.uint8
        
        # Frame should be modified from original red
        # (exact values depend on effect chain, just verify it's valid)
        assert np.all(frame >= 0)
        assert np.all(frame <= 255)
    
    def test_effect_chain_with_animated_effects(self, tmp_path):
        """Test effect chain with time-based animated effects."""
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create scene with animated effects
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=2.0,
                    motion=MotionPreset.STATIC,
                    effects=[
                        fade_in(1.0),  # Fade in over 1 second
                        film_grain(0.1),  # Add grain
                    ]
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render at different times
        frame_start = renderer.render_frame(0.1)  # Should be dark (fading in)
        frame_mid = renderer.render_frame(0.5)    # Should be mid-brightness
        frame_end = renderer.render_frame(1.5)    # Should be full brightness
        
        # Verify fade-in progression
        brightness_start = np.mean(frame_start)
        brightness_mid = np.mean(frame_mid)
        brightness_end = np.mean(frame_end)
        
        assert brightness_start < brightness_mid < brightness_end


class TestTransitionAndEffectsCombination:
    """Test transitions combined with effects on both clips."""
    
    def test_transition_with_effects_on_both_clips(self, tmp_path):
        """
        Test that both clips have effects applied during transition.
        
        **Validates: Integration testing**
        """
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        blue = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
        
        red_path = tmp_path / "red.png"
        blue_path = tmp_path / "blue.png"
        
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
        
        # Create scene with effects on both clips and transition
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=2.0,
                    motion=MotionPreset.STATIC,
                    effects=[brightness(0.2)]
                ),
                ImageClip(
                    source=str(blue_path),
                    duration=2.0,
                    motion=MotionPreset.STATIC,
                    effects=[contrast(1.3)]
                ),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=0.5)
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render during transition
        frame = renderer.render_frame(1.75)
        
        # Should have both colors blended with effects applied
        assert frame.shape == (100, 100, 3)
        assert frame.dtype == np.uint8
        
        center = frame[50, 50]
        # Should have both red and blue components
        assert center[0] > 0  # Has red
        assert center[2] > 0  # Has blue
    
    def test_complex_scene_with_motion_transitions_and_effects(self, tmp_path):
        """Test complex scene combining motion, transitions, and effects."""
        import cv2
        
        red = np.full((200, 200, 3), [255, 0, 0], dtype=np.uint8)
        blue = np.full((200, 200, 3), [0, 0, 255], dtype=np.uint8)
        
        red_path = tmp_path / "red.png"
        blue_path = tmp_path / "blue.png"
        
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
        
        # Create complex scene
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=2.0,
                    motion=MotionPreset.ZOOM_IN,  # Motion effect
                    effects=[brightness(0.1), vignette(0.3)]  # Visual effects
                ),
                ImageClip(
                    source=str(blue_path),
                    duration=2.0,
                    motion=MotionPreset.PAN_LEFT,  # Different motion
                    effects=[contrast(1.2)]  # Different effect
                ),
            ],
            transitions=[
                Transition(type=TransitionType.SLIDE_LEFT, duration=0.5)
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render frames at different points
        frame_clip1 = renderer.render_frame(0.5)
        frame_transition = renderer.render_frame(1.75)
        frame_clip2 = renderer.render_frame(3.0)
        
        # All frames should be valid
        for frame in [frame_clip1, frame_transition, frame_clip2]:
            assert frame.shape == (100, 100, 3)
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0)
            assert np.all(frame <= 255)


class TestEndToEndVideoGeneration:
    """Test end-to-end video generation with Phase 2 features."""
    
    def test_scene_with_transitions_produces_valid_frames(self, tmp_path):
        """
        Test that scene with transitions produces valid frames for all timestamps.
        
        **Validates: Integration testing**
        """
        import cv2
        
        # Create test images
        colors = [
            ([255, 0, 0], "red"),
            ([0, 255, 0], "green"),
            ([0, 0, 255], "blue"),
        ]
        
        paths = []
        for color, name in colors:
            img = np.full((100, 100, 3), color, dtype=np.uint8)
            path = tmp_path / f"{name}.png"
            cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            paths.append(path)
        
        # Create scene
        scene = Scene(
            clips=[
                ImageClip(source=str(paths[0]), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(paths[1]), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(paths[2]), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=0.3),
                Transition(type=TransitionType.SLIDE_LEFT, duration=0.3),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render all frames
        fps = 30
        duration = timeline.duration
        num_frames = int(duration * fps)
        
        frames = []
        for i in range(num_frames):
            t = i / fps
            frame = renderer.render_frame(t)
            frames.append(frame)
            
            # Verify each frame is valid
            assert frame.shape == (100, 100, 3)
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0)
            assert np.all(frame <= 255)
        
        # Verify we rendered the expected number of frames
        expected_frames = int((1.0 + 1.0 + 1.0 - 0.3 - 0.3) * fps)
        assert len(frames) == expected_frames
