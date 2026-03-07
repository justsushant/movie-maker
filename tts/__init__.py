"""
TTS module for PRISM.

This module provides abstractions for text-to-speech engines, allowing
different TTS implementations to be swapped without modifying downstream
components.

Core components:
- ITTSEngine: Interface for TTS engines
- TTSToken: Raw token from TTS engine with timing information
- TTSResult: Complete TTS generation result
- TTSConfig: Configuration for TTS engines
"""

from __future__ import annotations

from tts.interfaces import ITTSEngine, TTSToken, TTSResult
from tts.config import TTSConfig
from tts.kokoro_engine import KokoroTTSEngine

__all__ = [
    "ITTSEngine",
    "TTSToken",
    "TTSResult",
    "TTSConfig",
    "KokoroTTSEngine",
]
