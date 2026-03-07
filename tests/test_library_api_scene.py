"""Integration tests for library API with Scene parameter.

This module tests that the library API correctly handles Scene parameters,
overrides resolution/fps, and maintains backward compatibility.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from api.library import generate_video_from_text
from config.video_config import VideoConfig
from engine.scene import ImageClip, MotionPreset, Scene
from subtitle.config import SubtitleConfig, SubtitleMode
from tts.config import TTSConfig


@pytest.fixture
def test_images_dir():
    """Get path to test images directory."""
    return Path("tests/fixtures/images")


@pytest.fixture
def mock_tts_output(tmp_path):
    """Create mock TTS output files."""
    # Create mock audio file (empty WAV)
    audio_file = tmp_path / "output_moviepy.wav"
    audio_file.write_bytes(b"")
    
    # Create mock subtitle JSON
    subtitle_data = [
        {
            "sentence_text": "Test sentence",
            "start_time": 0.0,
            "end_time": 2.0,
            "words": [
                {"text": "Test", "start_time": 0.0, "end_time": 1.0},
                {"text": "sentence", "start_time": 1.0, "end_time": 2.0}
            ]
        }
    ]
    
    json_file = tmp_path / "output_moviepy.json"
    with open(json_file, 'w') as f:
        json.dump(subtitle_data, f)
    
    return audio_file, json_file


class TestLibraryAPIWithScene:
    """Test library API with Scene parameter.
    
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
    """
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_generate_video_with_scene_parameter(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Library API should pass Scene parameter to create_video."""
        # Create a scene
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
        
        # Mock pipeline to avoid actual TTS
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API with scene
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify create_video was called with scene parameter
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        assert call_args.kwargs['scene'] == scene
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_scene_resolution_overrides_video_config(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Scene resolution should override video_config resolution."""
        # Create a scene with custom resolution
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ],
            resolution=(1280, 720),  # Different from video_config
            fps=25
        )
        
        # Create video_config with different resolution
        video_config = VideoConfig(
            width=1920,
            height=1080,
            fps=30
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            video_config=video_config,
            scene=scene
        )
        
        # Verify create_video was called with scene resolution/fps
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        config = call_args.args[0]
        
        # Scene resolution should override video_config
        assert config['width'] == 1280
        assert config['height'] == 720
        assert config['fps'] == 25
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_backward_compatibility_without_scene(
        self, mock_create_video, mock_pipeline, tmp_path
    ):
        """Library API should work without Scene parameter (backward compatibility)."""
        # Create video_config
        video_config = VideoConfig(
            width=1920,
            height=1080,
            fps=30
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API without scene
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            video_config=video_config
        )
        
        # Verify create_video was called with video_config resolution/fps
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        config = call_args.args[0]
        
        # Should use video_config when no scene
        assert config['width'] == 1920
        assert config['height'] == 1080
        assert config['fps'] == 30
        
        # Scene parameter should be None
        assert call_args.kwargs['scene'] is None
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_subtitle_config_properly_passed(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Subtitle config should be properly passed to create_video."""
        # Create subtitle config
        subtitle_config = SubtitleConfig(
            mode=SubtitleMode.SENTENCE,
            base_color=(255, 255, 255),
            highlight_color=(255, 0, 0),
            font_size=48
        )
        
        # Create scene
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ]
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            subtitle_config=subtitle_config,
            scene=scene
        )
        
        # Verify subtitle config was passed
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        config = call_args.args[0]
        
        # Subtitle config should be in renderer config
        assert 'subtitle' in config
        subtitle_dict = config['subtitle']
        assert subtitle_dict['mode'] == 'sentence'
        assert subtitle_dict['base_color'] == (255, 255, 255)
        assert subtitle_dict['highlight_color'] == (255, 0, 0)
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_multiple_clips_scene(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Library API should handle scenes with multiple clips."""
        # Create scene with multiple clips
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                ),
                ImageClip(
                    source=test_images_dir / "landscape_gradient_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.PAN_LEFT
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.ZOOM_OUT
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify create_video was called with scene
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        passed_scene = call_args.kwargs['scene']
        
        # Verify scene has all clips
        assert len(passed_scene.clips) == 3
        assert passed_scene.clips[0].motion == MotionPreset.KEN_BURNS_ZOOM_IN
        assert passed_scene.clips[1].motion == MotionPreset.PAN_LEFT
        assert passed_scene.clips[2].motion == MotionPreset.ZOOM_OUT
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_default_configs_with_scene(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Library API should use default configs when not provided."""
        # Create scene
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ]
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Call library API with minimal parameters
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify create_video was called
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        config = call_args.args[0]
        
        # Should have default subtitle config
        assert 'subtitle' in config
        
        # Should use scene resolution (default 1920x1080)
        assert config['width'] == 1920
        assert config['height'] == 1080
        assert config['fps'] == 30
    
    @patch('api.library.TTSPipeline')
    @patch('api.library.create_video')
    def test_output_directory_creation(
        self, mock_create_video, mock_pipeline, tmp_path, test_images_dir
    ):
        """Library API should create output directory if it doesn't exist."""
        # Create scene
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ]
        )
        
        # Mock pipeline
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Use non-existent directory
        output_dir = tmp_path / "nested" / "output" / "dir"
        assert not output_dir.exists()
        
        # Call library API
        generate_video_from_text(
            text="Test text",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify directory was created
        assert output_dir.exists()
        assert output_dir.is_dir()
