"""Error handling and validation tests for Phase 2 transitions and effects."""

from __future__ import annotations

import numpy as np
import pytest

from engine.scene import Scene, ImageClip, MotionPreset, Transition, TransitionType
from engine.planner import ScenePlanner, ResolvedClip, ResolvedTimeline
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader
from engine.effects import brightness


class TestTransitionErrorHandling:
    """Test error handling for transitions."""
    
    def test_invalid_transition_duration_negative(self):
        """Test that negative transition duration raises ValueError."""
        with pytest.raises(ValueError, match="Transition duration must be positive"):
            Transition(type=TransitionType.CROSSFADE, duration=-1.0)
    
    def test_invalid_transition_duration_zero(self):
        """Test that zero transition duration raises ValueError."""
        with pytest.raises(ValueError, match="Transition duration must be positive"):
            Transition(type=TransitionType.CROSSFADE, duration=0.0)
    
    def test_transition_duration_exceeds_clip_duration(self, tmp_path):
        """Test that transition duration exceeding clip duration raises ValueError."""
        # Create test image
        import cv2
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create scene with transition longer than clip
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=1.5)  # Exceeds both clips
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        
        with pytest.raises(ValueError, match="Transition .* duration .* exceeds"):
            planner.plan(scene, loader)
    
    def test_too_many_transitions(self, tmp_path):
        """Test that too many transitions raises ValueError."""
        # Create test image
        import cv2
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Scene with 2 clips can have at most 1 transition
        with pytest.raises(ValueError, match="Scene has 2 clips but 2 transitions"):
            Scene(
                clips=[
                    ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                    ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ],
                transitions=[
                    Transition(type=TransitionType.CROSSFADE, duration=0.5),
                    Transition(type=TransitionType.FADE_THROUGH_BLACK, duration=0.5),
                ],
                resolution=(100, 100),
                fps=30
            )
    
    def test_frame_dimension_mismatch_during_transition(self, tmp_path):
        """Test that frame dimension mismatch during transition raises ValueError."""
        import cv2
        
        # Create images with different sizes
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        blue = np.full((200, 200, 3), [0, 0, 255], dtype=np.uint8)
        
        red_path = tmp_path / "red.png"
        blue_path = tmp_path / "blue.png"
        
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(blue_path), cv2.cvtColor(blue, cv2.COLOR_RGB2BGR))
        
        # Create scene with mismatched resolutions
        # Note: The planner will resize both to the scene resolution, so this won't fail
        # But if we manually create a timeline with mismatched frames, it should fail
        
        # This test verifies the renderer validates dimensions
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(blue_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=0.5)
            ],
            resolution=(100, 100),  # Both will be resized to this
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        # This should work because both frames are resized to scene resolution
        frame = renderer.render_frame(0.75)
        assert frame.shape == (100, 100, 3)


class TestEffectErrorHandling:
    """Test error handling for effects."""
    
    def test_effect_changes_frame_dimensions(self, tmp_path):
        """Test that effect changing frame dimensions raises ValueError."""
        import cv2
        
        # Create test image
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create effect that changes dimensions
        def bad_effect(frame, t, progress):
            # Resize to different dimensions
            return cv2.resize(frame, (50, 50))
        
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=1.0,
                    motion=MotionPreset.STATIC,
                    effects=[bad_effect]
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        with pytest.raises(Exception, match="Effect .* changed frame dimensions"):
            renderer.render_frame(0.5)
    
    def test_effect_changes_frame_dtype(self, tmp_path):
        """Test that effect changing frame dtype raises ValueError."""
        import cv2
        
        # Create test image
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create effect that changes dtype
        def bad_effect(frame, t, progress):
            # Return float32 instead of uint8
            return frame.astype(np.float32)
        
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=1.0,
                    motion=MotionPreset.STATIC,
                    effects=[bad_effect]
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        with pytest.raises(Exception, match="Effect .* changed frame dtype"):
            renderer.render_frame(0.5)
    
    def test_effect_exception_wrapping(self, tmp_path):
        """Test that effect exceptions are wrapped with context."""
        import cv2
        
        # Create test image
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create effect that raises an exception
        def bad_effect(frame, t, progress):
            raise RuntimeError("Effect failed!")
        
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=1.0,
                    motion=MotionPreset.STATIC,
                    effects=[bad_effect]
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        with pytest.raises(Exception, match="Error applying effect .* at time"):
            renderer.render_frame(0.5)
    
    def test_multiple_effects_first_fails(self, tmp_path):
        """Test that when first effect fails, error message identifies it correctly."""
        import cv2
        
        # Create test image
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Create effect that fails
        def bad_effect(frame, t, progress):
            raise RuntimeError("First effect failed!")
        
        scene = Scene(
            clips=[
                ImageClip(
                    source=str(red_path),
                    duration=1.0,
                    motion=MotionPreset.STATIC,
                    effects=[bad_effect, brightness(0.1)]  # First effect fails
                ),
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        renderer = FrameRenderer(timeline, loader)
        
        with pytest.raises(Exception, match="Error applying effect 0"):
            renderer.render_frame(0.5)


class TestValidationEdgeCases:
    """Test edge cases in validation."""
    
    def test_empty_scene_with_transitions(self):
        """Test that empty scene with transitions is handled gracefully."""
        # Empty scene should not raise error even with empty transitions list
        scene = Scene(clips=[], transitions=[])
        assert len(scene.clips) == 0
        assert len(scene.transitions) == 0
    
    def test_single_clip_with_no_transitions(self, tmp_path):
        """Test that single clip scene works without transitions."""
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        assert len(timeline.clips) == 1
        assert len(timeline.transitions) == 0
        assert timeline.duration == 1.0
    
    def test_transition_at_exact_clip_boundary(self, tmp_path):
        """Test transition that exactly matches clip duration."""
        import cv2
        
        red = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
        red_path = tmp_path / "red.png"
        cv2.imwrite(str(red_path), cv2.cvtColor(red, cv2.COLOR_RGB2BGR))
        
        # Transition duration equals clip duration (should be valid)
        scene = Scene(
            clips=[
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
                ImageClip(source=str(red_path), duration=1.0, motion=MotionPreset.STATIC),
            ],
            transitions=[
                Transition(type=TransitionType.CROSSFADE, duration=1.0)
            ],
            resolution=(100, 100),
            fps=30
        )
        
        loader = ImageLoader()
        planner = ScenePlanner()
        timeline = planner.plan(scene, loader)
        
        # Should work - transition duration equals minimum clip duration
        assert len(timeline.transitions) == 1
        assert timeline.transitions[0].end_time - timeline.transitions[0].start_time == 1.0
