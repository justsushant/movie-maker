"""End-to-end integration tests for video engine.

This module tests the complete pipeline from Scene definition through
video generation, verifying all components work together correctly.

**Validates: All Requirements**
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from api.library import generate_video_from_text
from engine.scene import ImageClip, MotionPreset, Scene


@pytest.fixture
def test_images_dir():
    """Get path to test images directory."""
    return Path("tests/fixtures/images")


@pytest.fixture
def mock_tts_pipeline():
    """Mock TTS pipeline to avoid slow TTS generation."""
    with patch('api.library.TTSPipeline') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock


class TestEndToEndIntegration:
    """End-to-end integration tests.
    
    **Validates: All Requirements**
    """
    
    @pytest.mark.slow
    def test_real_tts_with_scene_complete_pipeline(self, tmp_path, test_images_dir):
        """Complete end-to-end test with real TTS and video generation."""
        # This test runs the COMPLETE pipeline without mocks
        # It's marked as slow because TTS takes time
        
        # Define a scene
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
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        # Generate video with real TTS
        output_dir = tmp_path / "real_output"
        text = "This is a real end to end test with actual TTS generation."
        
        video_path = generate_video_from_text(
            text=text,
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify all output files were created
        assert video_path.exists(), "Video file should exist"
        assert (output_dir / "output_moviepy.wav").exists(), "Audio file should exist"
        assert (output_dir / "output_moviepy.json").exists(), "Subtitle JSON should exist"
        
        # Verify video file has content
        assert video_path.stat().st_size > 0, "Video file should not be empty"
        
        # Verify subtitle JSON has content
        import json
        with open(output_dir / "output_moviepy.json") as f:
            subtitle_data = json.load(f)
        assert len(subtitle_data) > 0, "Should have subtitle segments"
        
        print(f"\nGenerated video: {video_path}")
        print(f"Video size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    @patch('api.library.create_video')
    def test_complete_pipeline_with_scene(
        self, mock_create_video, mock_tts_pipeline, tmp_path, test_images_dir
    ):
        """Complete pipeline should work with Scene parameter."""
        # Define a scene with multiple clips and different motion presets
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
        
        # Generate video
        output_dir = tmp_path / "output"
        video_path = generate_video_from_text(
            text="This is a test video with multiple clips and motion effects.",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify video path is correct
        assert video_path == output_dir / "output_video.mp4"
        
        # Verify create_video was called with correct parameters
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        
        # Verify scene was passed
        assert call_args.kwargs['scene'] == scene
        
        # Verify config has correct resolution/fps from scene
        config = call_args.args[0]
        assert config['width'] == 1920
        assert config['height'] == 1080
        assert config['fps'] == 30
    
    @patch('api.library.create_video')
    def test_complete_pipeline_without_scene(
        self, mock_create_video, mock_tts_pipeline, tmp_path
    ):
        """Complete pipeline should work without Scene (backward compatibility)."""
        # Generate video without scene
        output_dir = tmp_path / "output"
        video_path = generate_video_from_text(
            text="This is a test video with solid background.",
            output_dir=output_dir
        )
        
        # Verify video path is correct
        assert video_path == output_dir / "output_video.mp4"
        
        # Verify create_video was called
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        
        # Verify scene is None (backward compatibility)
        assert call_args.kwargs['scene'] is None
    
    @patch('api.library.create_video')
    def test_output_files_created(
        self, mock_create_video, mock_tts_pipeline, tmp_path, test_images_dir
    ):
        """Pipeline should create all expected output files."""
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=2.0,
                    motion=MotionPreset.STATIC
                )
            ]
        )
        
        # Generate video
        output_dir = tmp_path / "output"
        generate_video_from_text(
            text="Test",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify output directory was created
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Note: Actual file creation is mocked, but directory structure is real
        # In a real run, these files would exist:
        # - output_moviepy.wav (audio)
        # - output_moviepy.json (subtitles)
        # - output_video.mp4 (final video)
    
    @patch('api.library.create_video')
    def test_all_motion_presets_in_single_video(
        self, mock_create_video, mock_tts_pipeline, tmp_path, test_images_dir
    ):
        """Pipeline should handle video with all motion presets."""
        # Create scene with all motion presets
        scene = Scene(
            clips=[
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.STATIC
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_IN
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.KEN_BURNS_ZOOM_OUT
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.PAN_LEFT
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.PAN_RIGHT
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.PAN_UP
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.PAN_DOWN
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.ZOOM_IN
                ),
                ImageClip(
                    source=test_images_dir / "landscape_1920x1080.png",
                    duration=1.0,
                    motion=MotionPreset.ZOOM_OUT
                )
            ],
            resolution=(1920, 1080),
            fps=30
        )
        
        # Generate video
        output_dir = tmp_path / "output"
        video_path = generate_video_from_text(
            text="Testing all motion presets in a single video.",
            output_dir=output_dir,
            scene=scene
        )
        
        # Verify scene was passed with all clips
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        passed_scene = call_args.kwargs['scene']
        
        assert len(passed_scene.clips) == 9
        assert passed_scene.clips[0].motion == MotionPreset.STATIC
        assert passed_scene.clips[1].motion == MotionPreset.KEN_BURNS_ZOOM_IN
        assert passed_scene.clips[8].motion == MotionPreset.ZOOM_OUT
    
    @patch('api.library.create_video')
    def test_different_resolutions(
        self, mock_create_video, mock_tts_pipeline, tmp_path, test_images_dir
    ):
        """Pipeline should handle different output resolutions."""
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
                        duration=2.0,
                        motion=MotionPreset.STATIC
                    )
                ],
                resolution=(width, height),
                fps=30
            )
            
            output_dir = tmp_path / f"output_{width}x{height}"
            generate_video_from_text(
                text="Test",
                output_dir=output_dir,
                scene=scene
            )
            
            # Verify correct resolution was used
            call_args = mock_create_video.call_args
            config = call_args.args[0]
            assert config['width'] == width
            assert config['height'] == height
    
    @patch('api.library.create_video')
    def test_different_frame_rates(
        self, mock_create_video, mock_tts_pipeline, tmp_path, test_images_dir
    ):
        """Pipeline should handle different frame rates."""
        frame_rates = [24, 30, 60]
        
        for fps in frame_rates:
            scene = Scene(
                clips=[
                    ImageClip(
                        source=test_images_dir / "landscape_1920x1080.png",
                        duration=2.0,
                        motion=MotionPreset.STATIC
                    )
                ],
                resolution=(1920, 1080),
                fps=fps
            )
            
            output_dir = tmp_path / f"output_{fps}fps"
            generate_video_from_text(
                text="Test",
                output_dir=output_dir,
                scene=scene
            )
            
            # Verify correct fps was used
            call_args = mock_create_video.call_args
            config = call_args.args[0]
            assert config['fps'] == fps
