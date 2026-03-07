"""
Unit tests for VideoConfig.

**Validates: Requirements 6.4**

Tests VideoConfig dataclass including default values, from_dict() conversion,
and field validation.
"""

from __future__ import annotations

import pytest

from config.video_config import VideoConfig


class TestVideoConfigDefaults:
    """Test default values for VideoConfig."""
    
    def test_default_width(self):
        """Test that default width is 1920."""
        config = VideoConfig()
        assert config.width == 1920
    
    def test_default_height(self):
        """Test that default height is 1080."""
        config = VideoConfig()
        assert config.height == 1080
    
    def test_default_fps(self):
        """Test that default fps is 30."""
        config = VideoConfig()
        assert config.fps == 30
    
    def test_default_bg_color(self):
        """Test that default background color is black (0, 0, 0)."""
        config = VideoConfig()
        assert config.bg_color == (0, 0, 0)
    
    def test_all_defaults_together(self):
        """Test that all defaults are set correctly when no args provided."""
        config = VideoConfig()
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30
        assert config.bg_color == (0, 0, 0)


class TestVideoConfigCustomValues:
    """Test VideoConfig with custom values."""
    
    def test_custom_width(self):
        """Test setting custom width."""
        config = VideoConfig(width=1280)
        assert config.width == 1280
        assert config.height == 1080  # Other defaults unchanged
    
    def test_custom_height(self):
        """Test setting custom height."""
        config = VideoConfig(height=720)
        assert config.width == 1920  # Other defaults unchanged
        assert config.height == 720
    
    def test_custom_fps(self):
        """Test setting custom fps."""
        config = VideoConfig(fps=60)
        assert config.fps == 60
        assert config.width == 1920  # Other defaults unchanged
    
    def test_custom_bg_color(self):
        """Test setting custom background color."""
        config = VideoConfig(bg_color=(255, 255, 255))
        assert config.bg_color == (255, 255, 255)
        assert config.width == 1920  # Other defaults unchanged
    
    def test_all_custom_values(self):
        """Test setting all custom values."""
        config = VideoConfig(
            width=1280,
            height=720,
            fps=60,
            bg_color=(128, 128, 128)
        )
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 60
        assert config.bg_color == (128, 128, 128)


class TestVideoConfigFromDict:
    """Test VideoConfig.from_dict() class method."""
    
    def test_from_dict_with_all_values(self):
        """Test creating VideoConfig from dict with all values."""
        config_dict = {
            "width": 1280,
            "height": 720,
            "fps": 60,
            "bg_color": (255, 0, 0)
        }
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 60
        assert config.bg_color == (255, 0, 0)
    
    def test_from_dict_with_partial_values(self):
        """Test creating VideoConfig from dict with only some values."""
        config_dict = {
            "width": 1280,
            "fps": 60
        }
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1280
        assert config.height == 1080  # Default
        assert config.fps == 60
        assert config.bg_color == (0, 0, 0)  # Default
    
    def test_from_dict_with_empty_dict(self):
        """Test creating VideoConfig from empty dict uses all defaults."""
        config_dict = {}
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30
        assert config.bg_color == (0, 0, 0)
    
    def test_from_dict_with_only_width(self):
        """Test creating VideoConfig from dict with only width."""
        config_dict = {"width": 3840}
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 3840
        assert config.height == 1080
        assert config.fps == 30
        assert config.bg_color == (0, 0, 0)
    
    def test_from_dict_with_only_height(self):
        """Test creating VideoConfig from dict with only height."""
        config_dict = {"height": 2160}
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1920
        assert config.height == 2160
        assert config.fps == 30
        assert config.bg_color == (0, 0, 0)
    
    def test_from_dict_with_only_fps(self):
        """Test creating VideoConfig from dict with only fps."""
        config_dict = {"fps": 24}
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 24
        assert config.bg_color == (0, 0, 0)
    
    def test_from_dict_with_only_bg_color(self):
        """Test creating VideoConfig from dict with only bg_color."""
        config_dict = {"bg_color": (100, 150, 200)}
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30
        assert config.bg_color == (100, 150, 200)
    
    def test_from_dict_ignores_extra_keys(self):
        """Test that from_dict ignores keys not in VideoConfig."""
        config_dict = {
            "width": 1280,
            "height": 720,
            "extra_key": "ignored",
            "another_key": 123
        }
        config = VideoConfig.from_dict(config_dict)
        
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 30  # Default
        assert config.bg_color == (0, 0, 0)  # Default
        assert not hasattr(config, "extra_key")
        assert not hasattr(config, "another_key")


class TestVideoConfigCommonResolutions:
    """Test VideoConfig with common video resolutions."""
    
    def test_hd_720p(self):
        """Test 720p HD resolution."""
        config = VideoConfig(width=1280, height=720)
        assert config.width == 1280
        assert config.height == 720
    
    def test_full_hd_1080p(self):
        """Test 1080p Full HD resolution (default)."""
        config = VideoConfig()
        assert config.width == 1920
        assert config.height == 1080
    
    def test_4k_uhd(self):
        """Test 4K UHD resolution."""
        config = VideoConfig(width=3840, height=2160)
        assert config.width == 3840
        assert config.height == 2160
    
    def test_vertical_video_9_16(self):
        """Test vertical video format (9:16 aspect ratio)."""
        config = VideoConfig(width=1080, height=1920)
        assert config.width == 1080
        assert config.height == 1920
    
    def test_square_video(self):
        """Test square video format (1:1 aspect ratio)."""
        config = VideoConfig(width=1080, height=1080)
        assert config.width == 1080
        assert config.height == 1080


class TestVideoConfigCommonFPS:
    """Test VideoConfig with common frame rates."""
    
    def test_cinema_24fps(self):
        """Test cinema standard 24 fps."""
        config = VideoConfig(fps=24)
        assert config.fps == 24
    
    def test_pal_25fps(self):
        """Test PAL standard 25 fps."""
        config = VideoConfig(fps=25)
        assert config.fps == 25
    
    def test_ntsc_30fps(self):
        """Test NTSC standard 30 fps (default)."""
        config = VideoConfig()
        assert config.fps == 30
    
    def test_high_fps_60(self):
        """Test high frame rate 60 fps."""
        config = VideoConfig(fps=60)
        assert config.fps == 60
    
    def test_very_high_fps_120(self):
        """Test very high frame rate 120 fps."""
        config = VideoConfig(fps=120)
        assert config.fps == 120


class TestVideoConfigBackgroundColors:
    """Test VideoConfig with various background colors."""
    
    def test_black_background(self):
        """Test black background (default)."""
        config = VideoConfig()
        assert config.bg_color == (0, 0, 0)
    
    def test_white_background(self):
        """Test white background."""
        config = VideoConfig(bg_color=(255, 255, 255))
        assert config.bg_color == (255, 255, 255)
    
    def test_red_background(self):
        """Test red background."""
        config = VideoConfig(bg_color=(255, 0, 0))
        assert config.bg_color == (255, 0, 0)
    
    def test_green_background(self):
        """Test green background."""
        config = VideoConfig(bg_color=(0, 255, 0))
        assert config.bg_color == (0, 255, 0)
    
    def test_blue_background(self):
        """Test blue background."""
        config = VideoConfig(bg_color=(0, 0, 255))
        assert config.bg_color == (0, 0, 255)
    
    def test_gray_background(self):
        """Test gray background."""
        config = VideoConfig(bg_color=(128, 128, 128))
        assert config.bg_color == (128, 128, 128)
    
    def test_custom_color_background(self):
        """Test custom RGB color background."""
        config = VideoConfig(bg_color=(123, 45, 67))
        assert config.bg_color == (123, 45, 67)


class TestVideoConfigEquality:
    """Test VideoConfig equality comparisons."""
    
    def test_equal_configs(self):
        """Test that two configs with same values are equal."""
        config1 = VideoConfig(width=1280, height=720, fps=60, bg_color=(255, 0, 0))
        config2 = VideoConfig(width=1280, height=720, fps=60, bg_color=(255, 0, 0))
        assert config1 == config2
    
    def test_unequal_configs_width(self):
        """Test that configs with different widths are not equal."""
        config1 = VideoConfig(width=1280)
        config2 = VideoConfig(width=1920)
        assert config1 != config2
    
    def test_unequal_configs_height(self):
        """Test that configs with different heights are not equal."""
        config1 = VideoConfig(height=720)
        config2 = VideoConfig(height=1080)
        assert config1 != config2
    
    def test_unequal_configs_fps(self):
        """Test that configs with different fps are not equal."""
        config1 = VideoConfig(fps=30)
        config2 = VideoConfig(fps=60)
        assert config1 != config2
    
    def test_unequal_configs_bg_color(self):
        """Test that configs with different bg_color are not equal."""
        config1 = VideoConfig(bg_color=(0, 0, 0))
        config2 = VideoConfig(bg_color=(255, 255, 255))
        assert config1 != config2
    
    def test_default_configs_equal(self):
        """Test that two default configs are equal."""
        config1 = VideoConfig()
        config2 = VideoConfig()
        assert config1 == config2


class TestVideoConfigLegacyCompatibility:
    """Test VideoConfig compatibility with legacy config dictionary format."""
    
    def test_from_legacy_config_dict(self):
        """Test creating VideoConfig from a legacy config dictionary."""
        legacy_config = {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "bg_color": (0, 0, 0),
            # Legacy config has other keys that should be ignored
            "input_text": "files/input.txt",
            "run_dir": "output/run_20240101_120000",
            "lang_code": "a",
            "voice": "af_heart",
            "font_size": 40,
            "text_color": (255, 255, 255)
        }
        config = VideoConfig.from_dict(legacy_config)
        
        assert config.width == 1920
        assert config.height == 1080
        assert config.fps == 30
        assert config.bg_color == (0, 0, 0)
    
    def test_from_legacy_config_dict_missing_video_keys(self):
        """Test creating VideoConfig from legacy dict missing some video keys."""
        legacy_config = {
            "width": 1280,
            # height, fps, bg_color missing
            "input_text": "files/input.txt",
            "lang_code": "a"
        }
        config = VideoConfig.from_dict(legacy_config)
        
        assert config.width == 1280
        assert config.height == 1080  # Default
        assert config.fps == 30  # Default
        assert config.bg_color == (0, 0, 0)  # Default
