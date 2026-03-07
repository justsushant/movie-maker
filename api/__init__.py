"""
Library API for PRISM.

This module provides the public programmatic API for generating
narrated videos from text using the refactored pipeline architecture.
"""

from __future__ import annotations

from api.library import generate_video_from_text, generate_video_from_file
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode

__all__ = [
    # Library API
    "generate_video_from_text",
    "generate_video_from_file",
    # Configuration classes
    "TTSConfig",
    "VideoConfig",
    "SubtitleConfig",
    "SubtitleMode",
]
