"""
Unit tests for TTSConfig.

Tests default values, from_dict() conversion, and field validation.
"""

from __future__ import annotations

import pytest

from tts.config import TTSConfig


class TestTTSConfigDefaults:
    """Test default values for TTSConfig."""
    
    def test_default_lang_code(self):
        """Test that default lang_code is 'a' (American English)."""
        config = TTSConfig()
        assert config.lang_code == "a"
    
    def test_default_voice(self):
        """Test that default voice is 'af_heart'."""
        config = TTSConfig()
        assert config.voice == "af_heart"
    
    def test_default_speed(self):
        """Test that default speed is 1.0."""
        config = TTSConfig()
        assert config.speed == 1.0
    
    def test_all_defaults(self):
        """Test that all defaults are set correctly together."""
        config = TTSConfig()
        assert config.lang_code == "a"
        assert config.voice == "af_heart"
        assert config.speed == 1.0


class TestTTSConfigCustomValues:
    """Test TTSConfig with custom values."""
    
    def test_custom_lang_code(self):
        """Test setting custom lang_code."""
        config = TTSConfig(lang_code="b")
        assert config.lang_code == "b"
    
    def test_custom_voice(self):
        """Test setting custom voice."""
        config = TTSConfig(voice="custom_voice")
        assert config.voice == "custom_voice"
    
    def test_custom_speed(self):
        """Test setting custom speed."""
        config = TTSConfig(speed=1.5)
        assert config.speed == 1.5
    
    def test_all_custom_values(self):
        """Test setting all custom values together."""
        config = TTSConfig(
            lang_code="c",
            voice="test_voice",
            speed=0.8
        )
        assert config.lang_code == "c"
        assert config.voice == "test_voice"
        assert config.speed == 0.8


class TestTTSConfigFromDict:
    """Test from_dict() conversion method."""
    
    def test_from_dict_with_all_values(self):
        """Test from_dict() with all values provided."""
        config_dict = {
            "lang_code": "b",
            "voice": "custom_voice",
            "speed": 1.2
        }
        config = TTSConfig.from_dict(config_dict)
        
        assert config.lang_code == "b"
        assert config.voice == "custom_voice"
        assert config.speed == 1.2
    
    def test_from_dict_with_empty_dict(self):
        """Test from_dict() with empty dict uses defaults."""
        config = TTSConfig.from_dict({})
        
        assert config.lang_code == "a"
        assert config.voice == "af_heart"
        assert config.speed == 1.0
    
    def test_from_dict_with_partial_values(self):
        """Test from_dict() with only some values provided."""
        config_dict = {"voice": "new_voice"}
        config = TTSConfig.from_dict(config_dict)
        
        assert config.lang_code == "a"  # default
        assert config.voice == "new_voice"  # custom
        assert config.speed == 1.0  # default
    
    def test_from_dict_with_lang_code_only(self):
        """Test from_dict() with only lang_code."""
        config_dict = {"lang_code": "c"}
        config = TTSConfig.from_dict(config_dict)
        
        assert config.lang_code == "c"
        assert config.voice == "af_heart"
        assert config.speed == 1.0
    
    def test_from_dict_with_speed_only(self):
        """Test from_dict() with only speed."""
        config_dict = {"speed": 2.0}
        config = TTSConfig.from_dict(config_dict)
        
        assert config.lang_code == "a"
        assert config.voice == "af_heart"
        assert config.speed == 2.0
    
    def test_from_dict_ignores_extra_keys(self):
        """Test from_dict() ignores keys not in TTSConfig."""
        config_dict = {
            "lang_code": "a",
            "voice": "af_heart",
            "speed": 1.0,
            "extra_key": "should_be_ignored",
            "another_extra": 123
        }
        config = TTSConfig.from_dict(config_dict)
        
        assert config.lang_code == "a"
        assert config.voice == "af_heart"
        assert config.speed == 1.0
        assert not hasattr(config, "extra_key")
        assert not hasattr(config, "another_extra")
    
    def test_from_dict_with_legacy_config(self):
        """Test from_dict() with a legacy config dictionary."""
        # Simulates the existing config.py structure
        legacy_config = {
            "lang_code": "a",
            "voice": "af_heart",
            "speed": 1.0,
            "width": 1920,  # video config
            "height": 1080,  # video config
            "fps": 30,  # video config
            "input_text": "files/input.txt"  # IO config
        }
        config = TTSConfig.from_dict(legacy_config)
        
        # Should extract only TTS-related fields
        assert config.lang_code == "a"
        assert config.voice == "af_heart"
        assert config.speed == 1.0


class TestTTSConfigFieldValidation:
    """Test field validation and edge cases."""
    
    def test_speed_zero(self):
        """Test that speed can be set to zero."""
        config = TTSConfig(speed=0.0)
        assert config.speed == 0.0
    
    def test_speed_negative(self):
        """Test that speed can be negative (no validation enforced)."""
        # Note: Python dataclasses don't enforce type constraints by default
        config = TTSConfig(speed=-1.0)
        assert config.speed == -1.0
    
    def test_speed_very_large(self):
        """Test that speed can be very large."""
        config = TTSConfig(speed=100.0)
        assert config.speed == 100.0
    
    def test_empty_lang_code(self):
        """Test that lang_code can be empty string."""
        config = TTSConfig(lang_code="")
        assert config.lang_code == ""
    
    def test_empty_voice(self):
        """Test that voice can be empty string."""
        config = TTSConfig(voice="")
        assert config.voice == ""
    
    def test_lang_code_with_special_characters(self):
        """Test lang_code with special characters."""
        config = TTSConfig(lang_code="en-US")
        assert config.lang_code == "en-US"
    
    def test_voice_with_special_characters(self):
        """Test voice with special characters and spaces."""
        config = TTSConfig(voice="voice_name-123")
        assert config.voice == "voice_name-123"


class TestTTSConfigEquality:
    """Test equality comparison between TTSConfig instances."""
    
    def test_equal_configs(self):
        """Test that two configs with same values are equal."""
        config1 = TTSConfig(lang_code="a", voice="af_heart", speed=1.0)
        config2 = TTSConfig(lang_code="a", voice="af_heart", speed=1.0)
        assert config1 == config2
    
    def test_unequal_configs_lang_code(self):
        """Test that configs with different lang_code are not equal."""
        config1 = TTSConfig(lang_code="a")
        config2 = TTSConfig(lang_code="b")
        assert config1 != config2
    
    def test_unequal_configs_voice(self):
        """Test that configs with different voice are not equal."""
        config1 = TTSConfig(voice="voice1")
        config2 = TTSConfig(voice="voice2")
        assert config1 != config2
    
    def test_unequal_configs_speed(self):
        """Test that configs with different speed are not equal."""
        config1 = TTSConfig(speed=1.0)
        config2 = TTSConfig(speed=1.5)
        assert config1 != config2


class TestTTSConfigRepr:
    """Test string representation of TTSConfig."""
    
    def test_repr_contains_all_fields(self):
        """Test that repr contains all field values."""
        config = TTSConfig(lang_code="b", voice="test_voice", speed=1.5)
        repr_str = repr(config)
        
        assert "TTSConfig" in repr_str
        assert "lang_code='b'" in repr_str
        assert "voice='test_voice'" in repr_str
        assert "speed=1.5" in repr_str
    
    def test_repr_default_values(self):
        """Test repr with default values."""
        config = TTSConfig()
        repr_str = repr(config)
        
        assert "TTSConfig" in repr_str
        assert "lang_code='a'" in repr_str
        assert "voice='af_heart'" in repr_str
        assert "speed=1.0" in repr_str
