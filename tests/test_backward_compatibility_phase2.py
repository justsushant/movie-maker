"""Backward compatibility tests for Phase 2 - ensure Phase 1 functionality unchanged."""

from __future__ import annotations

import numpy as np
import pytest

from engine.scene import Scene, ImageClip, MotionPreset
from engine.planner import ScenePlanner, ResolvedClip, ResolvedTimeline
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader


class TestPhase1ScenesWithoutTransitions:
    """Test that Phase 1 scenes without transitions attribute work correctly."""
    
    def test_scene_without_transitions_attribute_renders_sequentially(self, tmp_path):
        """
        Test Phase 1 scenes without transitions attribute render with sequential timing.
        
        **Validates: Requirements 12.1**
        """
        import cv2
        
        # Create test images
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        blue = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
        
        red_path = tmp_path / "red.png"
        blue_path = tmp_path / "blue.png"
        
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
        
        # Create Phase 1 style scene (no transitions)
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=2.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(blue_path), duration=3.0, motion=MotionPreset.STATIC),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Verify sequential timing (no overlap)
        assert len(timeline.clips) == 2
        assert len(timeline.transitions) == 0
        
        # Clip 1 should end exactly when clip 2 starts
        assert timeline.clips[0].start_time == 0.0
        assert timeline.clips[0].end_time == 2.0
        assert timeline.clips[1].start_time == 2.0
        assert timeline.clips[1].end_time == 5.0
        
        # Total duration should be sum of clip durations
        assert timeline.duration == 5.0
        
        # Render frames and verify instant cut
        renderer = FrameRenderer(timeline, loader)
        
        frame_before_cut = renderer.render_frame(1.99)
        frame_after_cut = renderer.render_frame(2.01)
        
        # Should be different colors (instant cut, no transition)
        assert np.allclose(frame_before_cut[50, 50], [255, 0, 0], atol=5)
        assert np.allclose(frame_after_cut[50, 50], [0, 0, 255], atol=5)
    
    def test_scene_with_empty_transitions_list(self, tmp_path):
        """Test scene with explicit empty transitions list."""
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[],  # Explicitly empty
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        assert len(timeline.transitions) == 0
        assert timeline.duration == 2.0


class TestPhase1ClipsWithoutEffects:
    """Test that Phase 1 clips without effects attribute work correctly."""
    
    def test_clips_without_effects_attribute_render_base_frames(self, tmp_path):
        """
        Test Phase 1 clips without effects attribute render base frames unchanged.
        
        **Validates: Requirements 12.3**
        """
        import cv2
        
        # Create test image
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create Phase 1 style clip (no effects)
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Render frame
        frame = renderer.render_frame(0.5)
        
        # Should be unchanged red
        assert frame.shape == (100, 100, 3)
        assert frame.dtype == np.uint8
        assert np.allclose(frame[50, 50], [255, 0, 0], atol=5)
    
    def test_clips_with_empty_effects_list(self, tmp_path):
        """Test clips with explicit empty effects list."""
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=1.0,
                    motion=MotionPreset.STATIC,
                    effects=[]  # Explicitly empty
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        frame = renderer.render_frame(0.5)
        
        # Should be unchanged
        assert np.allclose(frame[50, 50], [255, 0, 0], atol=5)


class TestMissingTransitionsRenderAsCuts:
    """Test that missing transitions between clips render as instant cuts."""
    
    def test_missing_transitions_render_as_cuts(self, tmp_path):
        """
        Property 3: Missing Transitions Render as Cuts
        
        When a scene has N clips but fewer than N-1 transitions, the clips
        without transitions should render as instant cuts (hard boundaries).
        
        **Validates: Requirements 1.7**
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
        
        # Create scene with 3 clips but no transitions
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(green_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(blue_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[],  # No transitions
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # Verify instant cuts at boundaries
        # Red to green at t=1.0
        frame_before_1 = renderer.render_frame(0.99)
        frame_after_1 = renderer.render_frame(1.01)
        
        assert np.allclose(frame_before_1[50, 50], [255, 0, 0], atol=5)  # Red
        assert np.allclose(frame_after_1[50, 50], [0, 255, 0], atol=5)   # Green
        
        # Green to blue at t=2.0
        frame_before_2 = renderer.render_frame(1.99)
        frame_after_2 = renderer.render_frame(2.01)
        
        assert np.allclose(frame_before_2[50, 50], [0, 255, 0], atol=5)  # Green
        assert np.allclose(frame_after_2[50, 50], [0, 0, 255], atol=5)   # Blue
    
    def test_partial_transitions_some_cuts(self, tmp_path):
        """Test scene with some transitions and some cuts."""
        import cv2
        from engine.scene import Transition, TransitionType
        
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
        
        # Create scene with 3 clips but only 1 transition (between first two)
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=2.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(green_path), duration=2.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(blue_path), duration=2.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=0.5),  # Only between red and green
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # First boundary should have transition (smooth blend)
        frame_mid_transition = renderer.render_frame(1.75)
        center_pixel = frame_mid_transition[50, 50]
        # Should have both red and green components
        assert center_pixel[0] > 50  # Has red
        assert center_pixel[1] > 50  # Has green
        
        # Second boundary should be instant cut
        # Green ends at 3.5, blue starts at 3.5
        frame_before_cut = renderer.render_frame(3.49)
        frame_after_cut = renderer.render_frame(3.51)
        
        assert np.allclose(frame_before_cut[50, 50], [0, 255, 0], atol=5)  # Green
        assert np.allclose(frame_after_cut[50, 50], [0, 0, 255], atol=5)   # Blue


class TestPhase1TestSuiteCompatibility:
    """Verify Phase 1 test suite still passes."""
    
    def test_phase1_test_suite_passes(self):
        """
        Test that Phase 1 test suite passes without modification.
        
        This is a meta-test that verifies backward compatibility by
        confirming all Phase 1 tests still pass.
        
        **Validates: Requirements 12.5**
        """
        import subprocess
        
        # Run Phase 1 test suite
        result = subprocess.run(
            [
                "python", "-m", "pytest",
                "tests/test_scene_dsl.py",
                "tests/test_easing.py",
                "tests/test_camera.py",
                "tests/test_motion_presets.py",
                "tests/test_image_loader.py",
                "tests/test_planner.py",
                "tests/test_renderer.py",
                "tests/test_integration_engine.py",
                "tests/test_visual_regression.py",
                "-v", "--tb=no", "-q"
            ],
            capture_output=True,
            text=True
        )
        
        # All Phase 1 tests should pass
        assert result.returncode == 0, f"Phase 1 tests failed:\n{result.stdout}\n{result.stderr}"
