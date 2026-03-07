"""Unit tests for Scene DSL data structures."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.scene import ImageClip, MotionPreset, Scene


class TestMotionPreset:
    """Tests for MotionPreset enum."""
    
    def test_motion_preset_has_all_expected_values(self):
        """Test that MotionPreset enum has all required motion types."""
        expected_values = {
            "STATIC",
            "KEN_BURNS_ZOOM_IN",
            "KEN_BURNS_ZOOM_OUT",
            "PAN_LEFT",
            "PAN_RIGHT",
            "PAN_UP",
            "PAN_DOWN",
            "ZOOM_IN",
            "ZOOM_OUT",
        }
        actual_values = {preset.name for preset in MotionPreset}
        assert actual_values == expected_values
    
    def test_motion_preset_values_are_strings(self):
        """Test that MotionPreset enum values are lowercase strings."""
        for preset in MotionPreset:
            assert isinstance(preset.value, str)
            assert preset.value.islower() or "_" in preset.value


class TestImageClip:
    """Tests for ImageClip dataclass."""
    
    def test_image_clip_creation_with_string_path(self):
        """Test creating ImageClip with string source path."""
        clip = ImageClip(source="image.png", duration=5.0)
        assert clip.source == "image.png"
        assert clip.duration == 5.0
        assert clip.motion == MotionPreset.STATIC
    
    def test_image_clip_creation_with_path_object(self):
        """Test creating ImageClip with Path object."""
        path = Path("images/photo.jpg")
        clip = ImageClip(source=path, duration=3.5)
        assert clip.source == path
        assert clip.duration == 3.5
        assert clip.motion == MotionPreset.STATIC
    
    def test_image_clip_default_motion_is_static(self):
        """Test that ImageClip defaults to STATIC motion when not specified."""
        clip = ImageClip(source="test.png", duration=2.0)
        assert clip.motion == MotionPreset.STATIC
    
    def test_image_clip_with_ken_burns_zoom_in(self):
        """Test creating ImageClip with KEN_BURNS_ZOOM_IN motion."""
        clip = ImageClip(
            source="test.png",
            duration=4.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_IN
        )
        assert clip.motion == MotionPreset.KEN_BURNS_ZOOM_IN
    
    def test_image_clip_with_ken_burns_zoom_out(self):
        """Test creating ImageClip with KEN_BURNS_ZOOM_OUT motion."""
        clip = ImageClip(
            source="test.png",
            duration=4.0,
            motion=MotionPreset.KEN_BURNS_ZOOM_OUT
        )
        assert clip.motion == MotionPreset.KEN_BURNS_ZOOM_OUT
    
    def test_image_clip_with_pan_left(self):
        """Test creating ImageClip with PAN_LEFT motion."""
        clip = ImageClip(
            source="test.png",
            duration=3.0,
            motion=MotionPreset.PAN_LEFT
        )
        assert clip.motion == MotionPreset.PAN_LEFT
    
    def test_image_clip_with_pan_right(self):
        """Test creating ImageClip with PAN_RIGHT motion."""
        clip = ImageClip(
            source="test.png",
            duration=3.0,
            motion=MotionPreset.PAN_RIGHT
        )
        assert clip.motion == MotionPreset.PAN_RIGHT
    
    def test_image_clip_with_pan_up(self):
        """Test creating ImageClip with PAN_UP motion."""
        clip = ImageClip(
            source="test.png",
            duration=3.0,
            motion=MotionPreset.PAN_UP
        )
        assert clip.motion == MotionPreset.PAN_UP
    
    def test_image_clip_with_pan_down(self):
        """Test creating ImageClip with PAN_DOWN motion."""
        clip = ImageClip(
            source="test.png",
            duration=3.0,
            motion=MotionPreset.PAN_DOWN
        )
        assert clip.motion == MotionPreset.PAN_DOWN
    
    def test_image_clip_with_zoom_in(self):
        """Test creating ImageClip with ZOOM_IN motion."""
        clip = ImageClip(
            source="test.png",
            duration=2.5,
            motion=MotionPreset.ZOOM_IN
        )
        assert clip.motion == MotionPreset.ZOOM_IN
    
    def test_image_clip_with_zoom_out(self):
        """Test creating ImageClip with ZOOM_OUT motion."""
        clip = ImageClip(
            source="test.png",
            duration=2.5,
            motion=MotionPreset.ZOOM_OUT
        )
        assert clip.motion == MotionPreset.ZOOM_OUT
    
    def test_image_clip_with_static_motion_explicit(self):
        """Test creating ImageClip with explicit STATIC motion."""
        clip = ImageClip(
            source="test.png",
            duration=5.0,
            motion=MotionPreset.STATIC
        )
        assert clip.motion == MotionPreset.STATIC


class TestScene:
    """Tests for Scene dataclass."""
    
    def test_scene_creation_with_defaults(self):
        """Test creating Scene with default parameters."""
        scene = Scene()
        assert scene.clips == []
        assert scene.resolution == (1920, 1080)
        assert scene.fps == 30
    
    def test_scene_creation_with_custom_resolution(self):
        """Test creating Scene with custom resolution."""
        scene = Scene(resolution=(3840, 2160))
        assert scene.resolution == (3840, 2160)
        assert scene.fps == 30
        assert scene.clips == []
    
    def test_scene_creation_with_custom_fps(self):
        """Test creating Scene with custom fps."""
        scene = Scene(fps=60)
        assert scene.fps == 60
        assert scene.resolution == (1920, 1080)
        assert scene.clips == []
    
    def test_scene_creation_with_custom_resolution_and_fps(self):
        """Test creating Scene with both custom resolution and fps."""
        scene = Scene(resolution=(1280, 720), fps=24)
        assert scene.resolution == (1280, 720)
        assert scene.fps == 24
        assert scene.clips == []
    
    def test_scene_with_empty_clips_list(self):
        """Test creating Scene with explicitly empty clips list."""
        scene = Scene(clips=[])
        assert scene.clips == []
        assert len(scene.clips) == 0
    
    def test_scene_with_single_clip(self):
        """Test creating Scene with a single clip."""
        clip = ImageClip(source="image.png", duration=5.0)
        scene = Scene(clips=[clip])
        assert len(scene.clips) == 1
        assert scene.clips[0] == clip
    
    def test_scene_with_multiple_clips(self):
        """Test creating Scene with multiple clips."""
        clip1 = ImageClip(source="image1.png", duration=3.0)
        clip2 = ImageClip(source="image2.png", duration=4.0, motion=MotionPreset.PAN_LEFT)
        clip3 = ImageClip(source="image3.png", duration=2.5, motion=MotionPreset.ZOOM_IN)
        
        scene = Scene(clips=[clip1, clip2, clip3])
        assert len(scene.clips) == 3
        assert scene.clips[0] == clip1
        assert scene.clips[1] == clip2
        assert scene.clips[2] == clip3
    
    def test_scene_with_all_parameters(self):
        """Test creating Scene with all parameters specified."""
        clip1 = ImageClip(source="img1.jpg", duration=2.0, motion=MotionPreset.KEN_BURNS_ZOOM_IN)
        clip2 = ImageClip(source="img2.jpg", duration=3.0, motion=MotionPreset.PAN_RIGHT)
        
        scene = Scene(
            clips=[clip1, clip2],
            resolution=(1280, 720),
            fps=24
        )
        
        assert len(scene.clips) == 2
        assert scene.resolution == (1280, 720)
        assert scene.fps == 24
        assert scene.clips[0].motion == MotionPreset.KEN_BURNS_ZOOM_IN
        assert scene.clips[1].motion == MotionPreset.PAN_RIGHT
