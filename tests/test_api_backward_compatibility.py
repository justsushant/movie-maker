"""
Tests for api backward compatibility after refactoring.

Verifies that the existing generate_video() API continues to work with
the same parameters and behavior after the refactoring.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from api import generate_video
from subtitle_config import SubtitleConfig, SubtitleMode


def test_generate_video_with_minimal_params(tmp_path):
    """Test generate_video with only required parameters."""
    json_file = tmp_path / "test.json"
    audio_file = tmp_path / "test.wav"
    output_video = tmp_path / "output.mp4"
    
    # Create minimal test data
    test_data = [
        {
            "sentence_text": "Hello world.",
            "start_time": 0.0,
            "end_time": 1.0,
            "words": [
                {"text": "Hello ", "clean_word": "Hello", "start_time": 0.0, "end_time": 0.5},
                {"text": "world.", "clean_word": "world", "start_time": 0.5, "end_time": 1.0}
            ]
        }
    ]
    json_file.write_text(json.dumps(test_data))
    
    # Mock the create_video function to avoid actual video rendering
    with patch('api.legacy.create_video') as mock_create_video:
        generate_video(
            json_file=str(json_file),
            audio_file=str(audio_file),
            output_video=str(output_video)
        )
        
        # Verify create_video was called
        assert mock_create_video.called
        call_args = mock_create_video.call_args
        
        # Verify config dict has expected defaults
        config = call_args[0][0]
        assert config["json_file"] == str(json_file)
        assert config["audio_file"] == str(audio_file)
        assert config["output_video"] == str(output_video)
        assert config["width"] == 1920
        assert config["height"] == 1080
        assert config["fps"] == 30
        assert config["bg_color"] == (0, 0, 0)
        assert config["font_size"] == 40
        assert config["text_color"] == (255, 255, 255)
        assert config["highlight_color"] == (255, 255, 0)


def test_generate_video_with_custom_params(tmp_path):
    """Test generate_video with custom video parameters."""
    json_file = tmp_path / "test.json"
    audio_file = tmp_path / "test.wav"
    output_video = tmp_path / "output.mp4"
    
    test_data = [{"sentence_text": "Test", "start_time": 0.0, "end_time": 1.0, "words": []}]
    json_file.write_text(json.dumps(test_data))
    
    with patch('api.legacy.create_video') as mock_create_video:
        generate_video(
            json_file=str(json_file),
            audio_file=str(audio_file),
            output_video=str(output_video),
            width=1280,
            height=720,
            fps=24,
            bg_color=(255, 0, 0)
        )
        
        config = mock_create_video.call_args[0][0]
        assert config["width"] == 1280
        assert config["height"] == 720
        assert config["fps"] == 24
        assert config["bg_color"] == (255, 0, 0)


def test_generate_video_with_subtitle_config(tmp_path):
    """Test generate_video with custom SubtitleConfig."""
    json_file = tmp_path / "test.json"
    audio_file = tmp_path / "test.wav"
    output_video = tmp_path / "output.mp4"
    
    test_data = [{"sentence_text": "Test", "start_time": 0.0, "end_time": 1.0, "words": []}]
    json_file.write_text(json.dumps(test_data))
    
    custom_config = SubtitleConfig(
        mode=SubtitleMode.WORD,
        font_size=50,
        base_color=(0, 255, 0)
    )
    
    with patch('api.legacy.create_video') as mock_create_video:
        generate_video(
            json_file=str(json_file),
            audio_file=str(audio_file),
            output_video=str(output_video),
            subtitle_config=custom_config
        )
        
        # Verify subtitle_config was passed through
        assert mock_create_video.called


def test_generate_video_with_extra_config(tmp_path):
    """Test generate_video with extra_config kwargs."""
    json_file = tmp_path / "test.json"
    audio_file = tmp_path / "test.wav"
    output_video = tmp_path / "output.mp4"
    
    test_data = [{"sentence_text": "Test", "start_time": 0.0, "end_time": 1.0, "words": []}]
    json_file.write_text(json.dumps(test_data))
    
    with patch('api.legacy.create_video') as mock_create_video:
        generate_video(
            json_file=str(json_file),
            audio_file=str(audio_file),
            output_video=str(output_video),
            text_color=(100, 100, 100),
            highlight_color=(200, 200, 0),
            custom_param="test_value"
        )
        
        config = mock_create_video.call_args[0][0]
        assert config["text_color"] == (100, 100, 100)
        assert config["highlight_color"] == (200, 200, 0)
        assert config["custom_param"] == "test_value"


def test_generate_video_with_custom_components(tmp_path):
    """Test generate_video with custom subtitle components."""
    json_file = tmp_path / "test.json"
    audio_file = tmp_path / "test.wav"
    output_video = tmp_path / "output.mp4"
    
    test_data = [{"sentence_text": "Test", "start_time": 0.0, "end_time": 1.0, "words": []}]
    json_file.write_text(json.dumps(test_data))
    
    mock_source = Mock()
    mock_layout = Mock()
    mock_renderer = Mock()
    
    with patch('api.legacy.create_video') as mock_create_video:
        generate_video(
            json_file=str(json_file),
            audio_file=str(audio_file),
            output_video=str(output_video),
            subtitle_source=mock_source,
            layout=mock_layout,
            renderer=mock_renderer
        )
        
        # Verify custom components were passed through
        call_kwargs = mock_create_video.call_args[1]
        assert call_kwargs["subtitle_source"] == mock_source
        assert call_kwargs["layout"] == mock_layout
        assert call_kwargs["renderer"] == mock_renderer


def test_api_exports():
    """Test that api.py exports the expected functions and classes."""
    import api
    
    # Verify legacy API is available
    assert hasattr(api, 'generate_video')
    
    # Verify new library API functions are re-exported
    assert hasattr(api, 'generate_video_from_text')
    assert hasattr(api, 'generate_video_from_file')
    
    # Verify config classes are re-exported
    assert hasattr(api, 'SubtitleConfig')
    assert hasattr(api, 'SubtitleMode')
    assert hasattr(api, 'TTSConfig')
    assert hasattr(api, 'VideoConfig')
    
    # Verify __all__ contains expected exports
    assert 'generate_video' in api.__all__
    assert 'generate_video_from_text' in api.__all__
    assert 'generate_video_from_file' in api.__all__
