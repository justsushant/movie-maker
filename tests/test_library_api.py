"""
Unit and integration tests for the library API.

Tests the generate_video_from_text() and generate_video_from_file() functions
using both mock implementations (unit tests) and real components (integration tests).

Test Coverage:
--------------
1. Unit Tests (TestGenerateVideoFromTextUnit, TestGenerateVideoFromFileUnit):
   - Test component instantiation and configuration
   - Test pipeline orchestration with mocks
   - Test error handling
   - Fast execution, no external dependencies

2. Integration Tests (TestGenerateVideoFromTextIntegration, TestGenerateVideoFromFileIntegration):
   - Test complete pipeline with real TTS generation
   - Test with various text inputs (short, long, multi-sentence, multi-paragraph)
   - Test with fixture files
   - Test with custom configurations
   - Verify actual output files are created

3. Output Comparison Tests (TestLibraryAPIOutputComparison):
   - Verify subtitle JSON structure matches expected format
   - Verify audio file format (WAV)
   - Verify video file format (MP4)
   - Can be used as baseline for regression testing

Requirements Validated:
-----------------------
- Requirement 6.6: Comprehensive unit testing for library API
- Requirement 7.2: Integration tests verify complete pipeline functionality
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

import pytest

from api.library import generate_video_from_text, generate_video_from_file
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig


class TestGenerateVideoFromTextUnit:
    """Tests for generate_video_from_text() function."""
    
    def test_creates_output_directory(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "test_output"
        assert not output_dir.exists()
        
        with patch('api.library.KokoroTTSEngine'), \
             patch('api.library.TTSPipeline'), \
             patch('api.library.create_video'):
            
            generate_video_from_text("Test text", output_dir)
            
            assert output_dir.exists()
            assert output_dir.is_dir()
    
    def test_uses_default_configs_when_none_provided(self, tmp_path):
        """Test that default configs are used when not provided."""
        output_dir = tmp_path / "test_output"
        
        with patch('api.library.KokoroTTSEngine') as mock_engine_class, \
             patch('api.library.TTSPipeline') as mock_pipeline_class, \
             patch('api.library.create_video'):
            
            generate_video_from_text("Test text", output_dir)
            
            # Verify KokoroTTSEngine was instantiated with default TTSConfig
            mock_engine_class.assert_called_once()
            tts_config = mock_engine_class.call_args[0][0]
            assert isinstance(tts_config, TTSConfig)
            assert tts_config.lang_code == "a"
            assert tts_config.voice == "af_heart"
            assert tts_config.speed == 1.0
    
    def test_uses_provided_configs(self, tmp_path):
        """Test that provided configs are used instead of defaults."""
        output_dir = tmp_path / "test_output"
        
        custom_tts_config = TTSConfig(lang_code="b", voice="custom_voice", speed=1.5)
        custom_video_config = VideoConfig(width=1280, height=720, fps=24)
        custom_subtitle_config = SubtitleConfig()
        
        with patch('api.library.KokoroTTSEngine') as mock_engine_class, \
             patch('api.library.TTSPipeline') as mock_pipeline_class, \
             patch('api.library.create_video') as mock_create_video:
            
            generate_video_from_text(
                "Test text",
                output_dir,
                tts_config=custom_tts_config,
                video_config=custom_video_config,
                subtitle_config=custom_subtitle_config
            )
            
            # Verify custom TTS config was used
            tts_config = mock_engine_class.call_args[0][0]
            assert tts_config.lang_code == "b"
            assert tts_config.voice == "custom_voice"
            assert tts_config.speed == 1.5
            
            # Verify custom video config was passed to renderer
            renderer_config = mock_create_video.call_args[0][0]
            assert renderer_config["width"] == 1280
            assert renderer_config["height"] == 720
            assert renderer_config["fps"] == 24
    
    def test_instantiates_pipeline_components(self, tmp_path):
        """Test that all pipeline components are instantiated correctly."""
        output_dir = tmp_path / "test_output"
        
        with patch('api.library.KokoroTTSEngine') as mock_engine_class, \
             patch('api.library.PunctuationMerger') as mock_merger_class, \
             patch('api.library.SentenceGrouper') as mock_grouper_class, \
             patch('api.library.FileAudioWriter') as mock_audio_writer_class, \
             patch('api.library.JsonMetadataWriter') as mock_metadata_writer_class, \
             patch('api.library.TTSPipeline') as mock_pipeline_class, \
             patch('api.library.create_video'):
            
            generate_video_from_text("Test text", output_dir)
            
            # Verify all components were instantiated
            mock_engine_class.assert_called_once()
            mock_merger_class.assert_called_once()
            mock_grouper_class.assert_called_once()
            mock_audio_writer_class.assert_called_once()
            mock_metadata_writer_class.assert_called_once()
            
            # Verify TTSPipeline was instantiated with all components
            mock_pipeline_class.assert_called_once()
            call_kwargs = mock_pipeline_class.call_args[1]
            assert 'tts_engine' in call_kwargs
            assert 'punctuation_merger' in call_kwargs
            assert 'sentence_grouper' in call_kwargs
            assert 'audio_writer' in call_kwargs
            assert 'metadata_writer' in call_kwargs
    
    def test_calls_pipeline_process(self, tmp_path):
        """Test that pipeline.process() is called with the input text."""
        output_dir = tmp_path / "test_output"
        test_text = "This is a test sentence."
        
        mock_pipeline = Mock()
        
        with patch('api.library.KokoroTTSEngine'), \
             patch('api.library.TTSPipeline', return_value=mock_pipeline), \
             patch('api.library.create_video'):
            
            generate_video_from_text(test_text, output_dir)
            
            # Verify process was called with the text
            mock_pipeline.process.assert_called_once_with(test_text)
    
    def test_calls_create_video_with_correct_config(self, tmp_path):
        """Test that create_video is called with correct configuration."""
        output_dir = tmp_path / "test_output"
        video_config = VideoConfig(width=1280, height=720, fps=24, bg_color=(255, 0, 0))
        
        with patch('api.library.KokoroTTSEngine'), \
             patch('api.library.TTSPipeline'), \
             patch('api.library.create_video') as mock_create_video:
            
            generate_video_from_text(
                "Test text",
                output_dir,
                video_config=video_config
            )
            
            # Verify create_video was called
            mock_create_video.assert_called_once()
            
            # Verify config dict has correct values
            renderer_config = mock_create_video.call_args[0][0]
            assert renderer_config["width"] == 1280
            assert renderer_config["height"] == 720
            assert renderer_config["fps"] == 24
            assert renderer_config["bg_color"] == (255, 0, 0)
            assert "json_file" in renderer_config
            assert "audio_file" in renderer_config
            assert "output_video" in renderer_config
    
    def test_returns_video_file_path(self, tmp_path):
        """Test that the function returns the path to the generated video."""
        output_dir = tmp_path / "test_output"
        
        with patch('api.library.KokoroTTSEngine'), \
             patch('api.library.TTSPipeline'), \
             patch('api.library.create_video'):
            
            result = generate_video_from_text("Test text", output_dir)
            
            assert isinstance(result, Path)
            assert result == output_dir / "output_video.mp4"
    
    def test_creates_correct_output_file_paths(self, tmp_path):
        """Test that output files are created in the correct locations."""
        output_dir = tmp_path / "test_output"
        
        with patch('api.library.KokoroTTSEngine'), \
             patch('api.library.FileAudioWriter') as mock_audio_writer_class, \
             patch('api.library.JsonMetadataWriter') as mock_metadata_writer_class, \
             patch('api.library.TTSPipeline'), \
             patch('api.library.create_video'):
            
            generate_video_from_text("Test text", output_dir)
            
            # Verify audio writer was created with correct path
            audio_path = mock_audio_writer_class.call_args[0][0]
            assert audio_path == output_dir / "output_moviepy.wav"
            
            # Verify metadata writer was created with correct path
            json_path = mock_metadata_writer_class.call_args[0][0]
            assert json_path == output_dir / "output_moviepy.json"


class TestGenerateVideoFromFileUnit:
    """Unit tests for generate_video_from_file() function."""
    
    def test_reads_text_from_file(self, tmp_path):
        """Test that text is read from the input file."""
        input_file = tmp_path / "input.txt"
        output_dir = tmp_path / "output"
        test_text = "This is test content from a file."
        
        input_file.write_text(test_text, encoding='utf-8')
        
        with patch('api.library.generate_video_from_text') as mock_generate:
            generate_video_from_file(input_file, output_dir)
            
            # Verify generate_video_from_text was called with the file content
            mock_generate.assert_called_once()
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs['text'] == test_text
            assert call_kwargs['output_dir'] == output_dir
    
    def test_passes_configs_to_generate_video_from_text(self, tmp_path):
        """Test that configs are passed through to generate_video_from_text."""
        input_file = tmp_path / "input.txt"
        output_dir = tmp_path / "output"
        input_file.write_text("Test", encoding='utf-8')
        
        custom_tts_config = TTSConfig(lang_code="b")
        custom_video_config = VideoConfig(width=1280)
        custom_subtitle_config = SubtitleConfig()
        
        with patch('api.library.generate_video_from_text') as mock_generate:
            generate_video_from_file(
                input_file,
                output_dir,
                tts_config=custom_tts_config,
                video_config=custom_video_config,
                subtitle_config=custom_subtitle_config
            )
            
            # Verify configs were passed through
            call_kwargs = mock_generate.call_args[1]
            assert call_kwargs['tts_config'] == custom_tts_config
            assert call_kwargs['video_config'] == custom_video_config
            assert call_kwargs['subtitle_config'] == custom_subtitle_config
    
    def test_returns_video_path(self, tmp_path):
        """Test that the function returns the video path from generate_video_from_text."""
        input_file = tmp_path / "input.txt"
        output_dir = tmp_path / "output"
        input_file.write_text("Test", encoding='utf-8')
        
        expected_path = output_dir / "video.mp4"
        
        with patch('api.library.generate_video_from_text', return_value=expected_path) as mock_generate:
            result = generate_video_from_file(input_file, output_dir)
            
            assert result == expected_path
    
    def test_raises_error_if_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised if input file doesn't exist."""
        input_file = tmp_path / "nonexistent.txt"
        output_dir = tmp_path / "output"
        
        with pytest.raises(FileNotFoundError):
            generate_video_from_file(input_file, output_dir)


# ============================================================================
# Integration Tests - Test with real components
# ============================================================================

class TestGenerateVideoFromTextIntegration:
    """
    Integration tests for generate_video_from_text() using real components.
    
    These tests run the complete pipeline with actual TTS generation and
    video rendering to verify end-to-end functionality.
    """
    
    def test_generates_video_with_short_text(self, test_output_root):
        """Test generating a video from a short text string."""
        output_dir = test_output_root / "integration_short_text"
        text = "Hello world! This is a test."
        
        # Generate video
        video_path = generate_video_from_text(text, output_dir)
        
        # Verify output files exist
        assert video_path.exists(), "Video file should be created"
        assert (output_dir / "output_moviepy.wav").exists(), "Audio file should be created"
        assert (output_dir / "output_moviepy.json").exists(), "Subtitle JSON should be created"
        
        # Verify video file is not empty
        assert video_path.stat().st_size > 0, "Video file should not be empty"
        
        # Verify subtitle JSON structure
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        assert isinstance(subtitles, list), "Subtitles should be a list"
        assert len(subtitles) > 0, "Should have at least one subtitle segment"
        
        # Verify first segment has required fields
        first_segment = subtitles[0]
        assert "sentence_text" in first_segment
        assert "start_time" in first_segment
        assert "end_time" in first_segment
        assert "words" in first_segment
        assert isinstance(first_segment["words"], list)
        
        # Verify word structure
        if first_segment["words"]:
            first_word = first_segment["words"][0]
            assert "text" in first_word
            assert "clean_word" in first_word
            assert "start_time" in first_word
            assert "end_time" in first_word
    
    def test_generates_video_with_custom_configs(self, test_output_root):
        """Test generating a video with custom configuration."""
        output_dir = test_output_root / "integration_custom_config"
        text = "Testing custom configuration."
        
        # Custom configs
        tts_config = TTSConfig(speed=1.2)
        video_config = VideoConfig(width=1280, height=720, fps=24)
        
        # Generate video
        video_path = generate_video_from_text(
            text,
            output_dir,
            tts_config=tts_config,
            video_config=video_config
        )
        
        # Verify output exists
        assert video_path.exists(), "Video file should be created"
        assert video_path.stat().st_size > 0, "Video file should not be empty"
    
    def test_generates_video_with_punctuation(self, test_output_root):
        """Test that punctuation is properly merged in generated video."""
        output_dir = test_output_root / "integration_punctuation"
        text = "Hello! How are you? I'm fine, thanks."
        
        # Generate video
        video_path = generate_video_from_text(text, output_dir)
        
        # Verify output exists
        assert video_path.exists()
        
        # Verify subtitle JSON has punctuation merged
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        # Check that words contain punctuation (not standalone)
        all_words = []
        for segment in subtitles:
            all_words.extend([w["text"] for w in segment["words"]])
        
        # At least some words should have punctuation attached
        words_with_punct = [w for w in all_words if any(p in w for p in "!?,.")]
        assert len(words_with_punct) > 0, "Punctuation should be merged into words"
    
    def test_generates_video_with_multiple_sentences(self, test_output_root):
        """Test generating video with multiple sentences."""
        output_dir = test_output_root / "integration_multi_sentence"
        text = "First sentence here. Second sentence follows. Third one too."
        
        # Generate video
        video_path = generate_video_from_text(text, output_dir)
        
        # Verify output exists
        assert video_path.exists()
        
        # Verify multiple sentence segments
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        assert len(subtitles) >= 2, "Should have multiple sentence segments"
        
        # Verify timing is sequential
        for i in range(len(subtitles) - 1):
            current_end = subtitles[i]["end_time"]
            next_start = subtitles[i + 1]["start_time"]
            assert current_end <= next_start, "Segments should not overlap"


class TestGenerateVideoFromFileIntegration:
    """
    Integration tests for generate_video_from_file() using real components.
    
    These tests use fixture files to verify the complete pipeline works
    with file input.
    """
    
    def test_generates_video_from_short_sentence_fixture(self, fixture_text_dir, test_output_root):
        """Test generating video from short_single_sentence.txt fixture."""
        input_file = fixture_text_dir / "short_single_sentence.txt"
        output_dir = test_output_root / "integration_file_short"
        
        # Generate video
        video_path = generate_video_from_file(input_file, output_dir)
        
        # Verify output files exist
        assert video_path.exists(), "Video file should be created"
        assert (output_dir / "output_moviepy.wav").exists(), "Audio file should be created"
        assert (output_dir / "output_moviepy.json").exists(), "Subtitle JSON should be created"
        
        # Verify video is not empty
        assert video_path.stat().st_size > 0, "Video file should not be empty"
    
    def test_generates_video_from_long_paragraph_fixture(self, fixture_text_dir, test_output_root):
        """Test generating video from long_paragraph.txt fixture."""
        input_file = fixture_text_dir / "long_paragraph.txt"
        output_dir = test_output_root / "integration_file_long"
        
        # Generate video
        video_path = generate_video_from_file(input_file, output_dir)
        
        # Verify output exists
        assert video_path.exists()
        
        # Verify subtitle JSON has multiple segments
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        assert len(subtitles) > 1, "Long paragraph should produce multiple segments"
    
    def test_generates_video_from_multi_paragraph_fixture(self, fixture_text_dir, test_output_root):
        """Test generating video from multi_paragraph.txt fixture."""
        input_file = fixture_text_dir / "multi_paragraph.txt"
        output_dir = test_output_root / "integration_file_multi"
        
        # Generate video
        video_path = generate_video_from_file(input_file, output_dir)
        
        # Verify output exists
        assert video_path.exists()
        assert video_path.stat().st_size > 0
    
    @pytest.mark.xfail(reason="Kokoro TTS returns None timestamps for certain punctuation patterns (quotes, dashes) - known limitation")
    def test_generates_video_from_punctuation_heavy_fixture(self, fixture_text_dir, test_output_root):
        """Test generating video from punctuation_heavy.txt fixture."""
        input_file = fixture_text_dir / "punctuation_heavy.txt"
        output_dir = test_output_root / "integration_file_punct"
        
        # Generate video
        video_path = generate_video_from_file(input_file, output_dir)
        
        # Verify output exists
        assert video_path.exists()
        
        # Verify punctuation handling in subtitles
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        # Should have segments with punctuation
        assert len(subtitles) > 0
        
        # Check that punctuation is merged into words
        all_words = []
        for segment in subtitles:
            all_words.extend([w["text"] for w in segment["words"]])
        
        words_with_punct = [w for w in all_words if any(p in w for p in "!?,.;:")]
        assert len(words_with_punct) > 0, "Punctuation should be present in words"
    
    def test_generates_video_with_custom_configs_from_file(self, fixture_text_dir, test_output_root):
        """Test generating video from file with custom configurations."""
        input_file = fixture_text_dir / "short_single_sentence.txt"
        output_dir = test_output_root / "integration_file_custom"
        
        # Custom configs
        tts_config = TTSConfig(speed=1.1)
        video_config = VideoConfig(width=1280, height=720, fps=24, bg_color=(10, 10, 10))
        
        # Generate video
        video_path = generate_video_from_file(
            input_file,
            output_dir,
            tts_config=tts_config,
            video_config=video_config
        )
        
        # Verify output exists
        assert video_path.exists()
        assert video_path.stat().st_size > 0


class TestLibraryAPIOutputComparison:
    """
    Tests that compare library API output structure with expected format.
    
    These tests verify that the generated files match the expected structure
    and can be used as baseline comparisons.
    """
    
    def test_subtitle_json_structure_matches_expected_format(self, test_output_root):
        """Test that generated subtitle JSON matches the expected hierarchical format."""
        output_dir = test_output_root / "integration_json_structure"
        text = "Hello world! This is a test sentence."
        
        # Generate video
        generate_video_from_text(text, output_dir)
        
        # Load and verify JSON structure
        with open(output_dir / "output_moviepy.json", 'r') as f:
            subtitles = json.load(f)
        
        # Verify top-level structure
        assert isinstance(subtitles, list), "Root should be a list"
        
        for segment in subtitles:
            # Verify segment structure
            assert "sentence_text" in segment, "Segment should have sentence_text"
            assert "start_time" in segment, "Segment should have start_time"
            assert "end_time" in segment, "Segment should have end_time"
            assert "words" in segment, "Segment should have words array"
            
            # Verify types
            assert isinstance(segment["sentence_text"], str)
            assert isinstance(segment["start_time"], (int, float))
            assert isinstance(segment["end_time"], (int, float))
            assert isinstance(segment["words"], list)
            
            # Verify timing is valid
            assert segment["start_time"] >= 0
            assert segment["end_time"] > segment["start_time"]
            
            # Verify word structure
            for word in segment["words"]:
                assert "text" in word, "Word should have text"
                assert "clean_word" in word, "Word should have clean_word"
                assert "start_time" in word, "Word should have start_time"
                assert "end_time" in word, "Word should have end_time"
                
                # Verify types
                assert isinstance(word["text"], str)
                assert isinstance(word["clean_word"], str)
                assert isinstance(word["start_time"], (int, float))
                assert isinstance(word["end_time"], (int, float))
                
                # Verify timing
                assert word["start_time"] >= segment["start_time"]
                assert word["end_time"] <= segment["end_time"]
                assert word["end_time"] > word["start_time"]
    
    def test_audio_file_format_is_valid_wav(self, test_output_root):
        """Test that generated audio file is a valid WAV file."""
        output_dir = test_output_root / "integration_audio_format"
        text = "Testing audio output."
        
        # Generate video
        generate_video_from_text(text, output_dir)
        
        audio_file = output_dir / "output_moviepy.wav"
        assert audio_file.exists()
        
        # Verify it's a WAV file by checking header
        with open(audio_file, 'rb') as f:
            header = f.read(12)
            assert header[:4] == b'RIFF', "Should have RIFF header"
            assert header[8:12] == b'WAVE', "Should have WAVE format"
    
    def test_video_file_format_is_valid_mp4(self, test_output_root):
        """Test that generated video file is a valid MP4 file."""
        output_dir = test_output_root / "integration_video_format"
        text = "Testing video output."
        
        # Generate video
        video_path = generate_video_from_text(text, output_dir)
        
        assert video_path.exists()
        assert video_path.suffix == ".mp4", "Should have .mp4 extension"
        
        # Verify it's an MP4 file by checking for ftyp box
        with open(video_path, 'rb') as f:
            # Skip first 4 bytes (box size), read next 8 bytes
            f.read(4)
            box_type = f.read(4)
            assert box_type == b'ftyp', "Should have ftyp box (MP4 format)"
