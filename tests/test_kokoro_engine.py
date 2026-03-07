"""
Unit tests for KokoroTTSEngine.

Tests the Kokoro TTS engine implementation to ensure it correctly
generates audio and token timing data.
"""

from __future__ import annotations

import numpy as np
import pytest

from tts import KokoroTTSEngine, TTSConfig, TTSResult, TTSToken


class TestKokoroTTSEngine:
    """Test suite for KokoroTTSEngine."""
    
    def test_initialization(self):
        """Test that KokoroTTSEngine initializes correctly with TTSConfig."""
        config = TTSConfig(lang_code="a", voice="af_heart", speed=1.0)
        engine = KokoroTTSEngine(config)
        
        assert engine._config == config
        assert engine._pipeline is not None
    
    def test_generate_single_sentence(self):
        """Test generating audio from a single sentence."""
        config = TTSConfig()
        engine = KokoroTTSEngine(config)
        
        text = "Hello world."
        result = engine.generate(text)
        
        # Verify result structure
        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, np.ndarray)
        assert result.sample_rate == 24000
        assert isinstance(result.tokens, list)
        assert len(result.tokens) > 0
        
        # Verify tokens
        for token in result.tokens:
            assert isinstance(token, TTSToken)
            assert isinstance(token.text, str)
            assert isinstance(token.whitespace, str)
            assert isinstance(token.start_ts, float)
            assert isinstance(token.end_ts, float)
            assert token.start_ts >= 0
            assert token.end_ts >= token.start_ts
    
    def test_generate_multi_paragraph(self):
        """Test generating audio from multiple paragraphs with time offsets."""
        config = TTSConfig()
        engine = KokoroTTSEngine(config)
        
        text = "First paragraph.\n\nSecond paragraph."
        result = engine.generate(text)
        
        # Verify result structure
        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, np.ndarray)
        assert len(result.audio) > 0
        assert result.sample_rate == 24000
        assert len(result.tokens) > 0
        
        # Verify timestamps are monotonically increasing
        for i in range(len(result.tokens) - 1):
            assert result.tokens[i].end_ts <= result.tokens[i + 1].start_ts or \
                   abs(result.tokens[i].end_ts - result.tokens[i + 1].start_ts) < 0.1
    
    def test_generate_empty_text(self):
        """Test generating audio from empty text."""
        config = TTSConfig()
        engine = KokoroTTSEngine(config)
        
        text = ""
        result = engine.generate(text)
        
        # Should return empty result
        assert isinstance(result, TTSResult)
        assert isinstance(result.audio, np.ndarray)
        assert len(result.audio) == 0
        assert result.sample_rate == 24000
        assert len(result.tokens) == 0
    
    def test_custom_config(self):
        """Test that custom configuration is used."""
        config = TTSConfig(lang_code="a", voice="af_heart", speed=1.5)
        engine = KokoroTTSEngine(config)
        
        assert engine._config.speed == 1.5
        assert engine._config.voice == "af_heart"
        assert engine._config.lang_code == "a"
    
    def test_token_timing_accuracy(self):
        """Test that token timing data is reasonable."""
        config = TTSConfig()
        engine = KokoroTTSEngine(config)
        
        text = "Test sentence."
        result = engine.generate(text)
        
        # Verify timing makes sense
        assert len(result.tokens) > 0
        
        # First token should start near 0
        assert result.tokens[0].start_ts >= 0
        assert result.tokens[0].start_ts < 1.0  # Should start within first second
        
        # Last token should end after it starts
        last_token = result.tokens[-1]
        assert last_token.end_ts > last_token.start_ts
        
        # Audio duration should roughly match last token end time
        audio_duration = len(result.audio) / result.sample_rate
        # Allow some tolerance for processing
        assert abs(audio_duration - last_token.end_ts) < 1.0
