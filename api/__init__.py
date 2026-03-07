"""
Library API for KokoroMoviePy.

This module provides the public programmatic API for generating
narrated videos from text using the refactored pipeline architecture.

It also maintains backward compatibility with the legacy generate_video
function for working with pre-existing audio and JSON files.
"""

from __future__ import annotations

from api.library import generate_video_from_text, generate_video_from_file
from api.legacy import generate_video
from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig, SubtitleMode

__all__ = [
    # New library API
    "generate_video_from_text",
    "generate_video_from_file",
    # Legacy API
    "generate_video",
    # Configuration classes
    "TTSConfig",
    "VideoConfig",
    "SubtitleConfig",
    "SubtitleMode",
]
