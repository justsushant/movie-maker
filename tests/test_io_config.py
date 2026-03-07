"""
Unit tests for IOConfig.

**Validates: Requirements 6.4**

Tests IOConfig dataclass including from_dict() conversion and path handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from config.io_config import IOConfig


class TestIOConfigFromDict:
    """Test IOConfig.from_dict() class method."""
    
    def test_from_dict_with_all_values(self):
        """Test creating IOConfig from dict with all values."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text == Path("files/input.txt")
        assert config.output_dir == Path("output/run_20240101_120000")
        assert config.json_file == Path("output/run_20240101_120000/output_moviepy.json")
        assert config.audio_file == Path("output/run_20240101_120000/output_moviepy.wav")
        assert config.srt_file == Path("output/run_20240101_120000/output_moviepy_word.srt")
        assert config.video_file == Path("output/run_20240101_120000/output_video.mp4")
    
    def test_from_dict_paths_are_path_objects(self):
        """Test that from_dict returns Path objects, not strings."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/test",
            "json_file": "output/test/output_moviepy.json",
            "audio_file": "output/test/output_moviepy.wav",
            "srt_file": "output/test/output_moviepy_word.srt",
            "output_video": "output/test/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert isinstance(config.input_text, Path)
        assert isinstance(config.output_dir, Path)
        assert isinstance(config.json_file, Path)
        assert isinstance(config.audio_file, Path)
        assert isinstance(config.srt_file, Path)
        assert isinstance(config.video_file, Path)
    
    def test_from_dict_with_test_run(self):
        """Test creating IOConfig from dict for test run."""
        config_dict = {
            "input_text": "tests/fixtures/text/short_single_sentence.txt",
            "run_dir": "output/test",
            "json_file": "output/test/output_moviepy.json",
            "audio_file": "output/test/output_moviepy.wav",
            "srt_file": "output/test/output_moviepy_word.srt",
            "output_video": "output/test/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text == Path("tests/fixtures/text/short_single_sentence.txt")
        assert config.output_dir == Path("output/test")
        assert config.json_file == Path("output/test/output_moviepy.json")
    
    def test_from_dict_ignores_extra_keys(self):
        """Test that from_dict ignores keys not in IOConfig."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4",
            # Extra keys that should be ignored
            "width": 1920,
            "height": 1080,
            "lang_code": "a",
            "voice": "af_heart"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text == Path("files/input.txt")
        assert config.output_dir == Path("output/run_20240101_120000")
        assert not hasattr(config, "width")
        assert not hasattr(config, "height")
        assert not hasattr(config, "lang_code")
        assert not hasattr(config, "voice")


class TestIOConfigPathHandling:
    """Test IOConfig path handling and manipulation."""
    
    def test_paths_can_be_joined(self):
        """Test that Path objects can be joined with / operator."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        # Test that we can join paths
        new_file = config.output_dir / "new_file.txt"
        assert isinstance(new_file, Path)
        assert str(new_file) == "output/run_20240101_120000/new_file.txt"
    
    def test_paths_have_name_property(self):
        """Test that Path objects have name property for filename."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text.name == "input.txt"
        assert config.json_file.name == "output_moviepy.json"
        assert config.audio_file.name == "output_moviepy.wav"
        assert config.srt_file.name == "output_moviepy_word.srt"
        assert config.video_file.name == "output_video.mp4"
    
    def test_paths_have_parent_property(self):
        """Test that Path objects have parent property for directory."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text.parent == Path("files")
        assert config.json_file.parent == Path("output/run_20240101_120000")
        assert config.audio_file.parent == Path("output/run_20240101_120000")
    
    def test_paths_have_suffix_property(self):
        """Test that Path objects have suffix property for file extension."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.input_text.suffix == ".txt"
        assert config.json_file.suffix == ".json"
        assert config.audio_file.suffix == ".wav"
        assert config.srt_file.suffix == ".srt"
        assert config.video_file.suffix == ".mp4"


class TestIOConfigDirectConstruction:
    """Test IOConfig direct construction with Path objects."""
    
    def test_construct_with_path_objects(self):
        """Test constructing IOConfig directly with Path objects."""
        config = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        
        assert config.input_text == Path("files/input.txt")
        assert config.output_dir == Path("output/test")
        assert config.json_file == Path("output/test/output_moviepy.json")
        assert config.audio_file == Path("output/test/output_moviepy.wav")
        assert config.srt_file == Path("output/test/output_moviepy_word.srt")
        assert config.video_file == Path("output/test/output_video.mp4")
    
    def test_construct_with_string_paths(self):
        """Test constructing IOConfig with string paths (auto-converted to Path)."""
        config = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        
        # All should be Path objects
        assert isinstance(config.input_text, Path)
        assert isinstance(config.output_dir, Path)
        assert isinstance(config.json_file, Path)
        assert isinstance(config.audio_file, Path)
        assert isinstance(config.srt_file, Path)
        assert isinstance(config.video_file, Path)


class TestIOConfigEquality:
    """Test IOConfig equality comparisons."""
    
    def test_equal_configs(self):
        """Test that two configs with same paths are equal."""
        config1 = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        config2 = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        assert config1 == config2
    
    def test_unequal_configs_input_text(self):
        """Test that configs with different input_text are not equal."""
        config1 = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        config2 = IOConfig(
            input_text=Path("files/other.txt"),
            output_dir=Path("output/test"),
            json_file=Path("output/test/output_moviepy.json"),
            audio_file=Path("output/test/output_moviepy.wav"),
            srt_file=Path("output/test/output_moviepy_word.srt"),
            video_file=Path("output/test/output_video.mp4")
        )
        assert config1 != config2
    
    def test_unequal_configs_output_dir(self):
        """Test that configs with different output_dir are not equal."""
        config1 = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test1"),
            json_file=Path("output/test1/output_moviepy.json"),
            audio_file=Path("output/test1/output_moviepy.wav"),
            srt_file=Path("output/test1/output_moviepy_word.srt"),
            video_file=Path("output/test1/output_video.mp4")
        )
        config2 = IOConfig(
            input_text=Path("files/input.txt"),
            output_dir=Path("output/test2"),
            json_file=Path("output/test2/output_moviepy.json"),
            audio_file=Path("output/test2/output_moviepy.wav"),
            srt_file=Path("output/test2/output_moviepy_word.srt"),
            video_file=Path("output/test2/output_video.mp4")
        )
        assert config1 != config2


class TestIOConfigLegacyCompatibility:
    """Test IOConfig compatibility with legacy config dictionary format."""
    
    def test_from_legacy_config_dict(self):
        """Test creating IOConfig from a complete legacy config dictionary."""
        legacy_config = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "json_file": "output/run_20240101_120000/output_moviepy.json",
            "audio_file": "output/run_20240101_120000/output_moviepy.wav",
            "srt_file": "output/run_20240101_120000/output_moviepy_word.srt",
            "output_video": "output/run_20240101_120000/output_video.mp4",
            # Legacy config has other keys that should be ignored
            "lang_code": "a",
            "voice": "af_heart",
            "speed": 1.0,
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "font_size": 40,
            "bg_color": (0, 0, 0),
            "text_color": (255, 255, 255),
            "highlight_color": (255, 255, 0)
        }
        config = IOConfig.from_dict(legacy_config)
        
        assert config.input_text == Path("files/input.txt")
        assert config.output_dir == Path("output/run_20240101_120000")
        assert config.json_file == Path("output/run_20240101_120000/output_moviepy.json")
        assert config.audio_file == Path("output/run_20240101_120000/output_moviepy.wav")
        assert config.srt_file == Path("output/run_20240101_120000/output_moviepy_word.srt")
        assert config.video_file == Path("output/run_20240101_120000/output_video.mp4")
    
    def test_from_test_config_dict(self):
        """Test creating IOConfig from test config dictionary."""
        test_config = {
            "input_text": "tests/fixtures/text/short_single_sentence.txt",
            "run_dir": "output/test/case_1",
            "json_file": "output/test/case_1/output_moviepy.json",
            "audio_file": "output/test/case_1/output_moviepy.wav",
            "srt_file": "output/test/case_1/output_moviepy_word.srt",
            "output_video": "output/test/case_1/output_video.mp4"
        }
        config = IOConfig.from_dict(test_config)
        
        assert config.input_text == Path("tests/fixtures/text/short_single_sentence.txt")
        assert config.output_dir == Path("output/test/case_1")
        assert config.json_file == Path("output/test/case_1/output_moviepy.json")


class TestIOConfigCommonPatterns:
    """Test IOConfig with common usage patterns."""
    
    def test_timestamped_run_directory(self):
        """Test IOConfig with timestamped run directory pattern."""
        config_dict = {
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240315_143022",
            "json_file": "output/run_20240315_143022/output_moviepy.json",
            "audio_file": "output/run_20240315_143022/output_moviepy.wav",
            "srt_file": "output/run_20240315_143022/output_moviepy_word.srt",
            "output_video": "output/run_20240315_143022/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        # Verify all output files are in the same timestamped directory
        assert config.json_file.parent == config.output_dir
        assert config.audio_file.parent == config.output_dir
        assert config.srt_file.parent == config.output_dir
        assert config.video_file.parent == config.output_dir
    
    def test_test_output_directory(self):
        """Test IOConfig with test output directory pattern."""
        config_dict = {
            "input_text": "tests/fixtures/text/test.txt",
            "run_dir": "output/test",
            "json_file": "output/test/output_moviepy.json",
            "audio_file": "output/test/output_moviepy.wav",
            "srt_file": "output/test/output_moviepy_word.srt",
            "output_video": "output/test/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.output_dir == Path("output/test")
        assert str(config.output_dir).startswith("output/")
    
    def test_nested_test_case_directory(self):
        """Test IOConfig with nested test case directory pattern."""
        config_dict = {
            "input_text": "tests/fixtures/text/test.txt",
            "run_dir": "output/test/1080p_sentence_mode",
            "json_file": "output/test/1080p_sentence_mode/output_moviepy.json",
            "audio_file": "output/test/1080p_sentence_mode/output_moviepy.wav",
            "srt_file": "output/test/1080p_sentence_mode/output_moviepy_word.srt",
            "output_video": "output/test/1080p_sentence_mode/output_video.mp4"
        }
        config = IOConfig.from_dict(config_dict)
        
        assert config.output_dir == Path("output/test/1080p_sentence_mode")
        assert config.json_file.parent == config.output_dir
