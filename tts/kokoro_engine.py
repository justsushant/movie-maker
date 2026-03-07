"""
Kokoro TTS engine implementation.

This module provides a concrete implementation of ITTSEngine using the
Kokoro TTS library. It handles text-to-speech generation with word-level
timing information.
"""

from __future__ import annotations

import re
import numpy as np
from kokoro import KPipeline

from tts.interfaces import ITTSEngine, TTSResult, TTSToken
from tts.config import TTSConfig


class KokoroTTSEngine(ITTSEngine):
    """
    Kokoro TTS implementation.
    
    This class wraps the Kokoro TTS library and provides word-level timing
    information for generated speech. It handles multi-paragraph text by
    processing each paragraph separately and adjusting timestamps accordingly.
    
    Attributes:
        _config: TTS configuration settings
        _pipeline: Initialized Kokoro pipeline instance
    """
    
    def __init__(self, config: TTSConfig):
        """
        Initialize the Kokoro TTS engine.
        
        Args:
            config: TTS configuration with lang_code, voice, and speed settings
        """
        self._config = config
        self._pipeline = KPipeline(lang_code=config.lang_code)
    
    def generate(self, text: str) -> TTSResult:
        """
        Generate speech using Kokoro TTS.
        
        This method processes the input text by splitting it into paragraphs,
        generating audio for each paragraph, and combining the results with
        properly adjusted timestamps.
        
        Args:
            text: Input text to synthesize
            
        Returns:
            TTSResult containing audio samples at 24kHz and token timing data
            
        Raises:
            Exception: If TTS generation fails
        """
        # Split into paragraphs
        paragraphs = re.split(r'\n+', text.strip())
        
        audio_segments = []
        all_tokens = []
        
        for paragraph in paragraphs:
            generator = self._pipeline(
                paragraph,
                voice=self._config.voice,
                speed=self._config.speed
            )
            
            paragraph_audio = []
            paragraph_tokens = []
            
            for result in generator:
                paragraph_audio.append(result.audio.cpu().numpy())
                paragraph_tokens.extend(result.tokens)
            
            # Calculate time offset for this paragraph based on previous audio
            time_offset = sum(len(seg) for seg in audio_segments) / 24000 if audio_segments else 0
            
            # Convert Kokoro tokens to our format with offset
            # Skip tokens with None timestamps (e.g., special characters)
            for token in paragraph_tokens:
                if token.start_ts is not None and token.end_ts is not None:
                    all_tokens.append(TTSToken(
                        text=token.text,
                        whitespace=token.whitespace,
                        start_ts=token.start_ts + time_offset,
                        end_ts=token.end_ts + time_offset
                    ))
            
            if paragraph_audio:
                audio_segments.append(np.concatenate(paragraph_audio))
        
        # Concatenate all audio
        if audio_segments:
            audio = np.concatenate(audio_segments)
        else:
            audio = np.array([])
        
        return TTSResult(
            audio=audio,
            sample_rate=24000,
            tokens=all_tokens
        )
