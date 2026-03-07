"""
Legacy API for generating videos from pre-existing audio and JSON files.

This module maintains backward compatibility with the original api.py interface,
allowing users to render videos when they already have TTS output files.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from subtitle_config import SubtitleConfig, SubtitleMode
from subtitle.interfaces import ISubtitleLayout, ISubtitleRenderer, ISubtitleSource
from subtitle.layouts import (
    StackingLayout,
    SentenceLayout,
    WordHighlightLayout,
    WordOnlyLayout,
)
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.source import JsonSubtitleSource

from renderer import create_video


def _default_layout(mode: SubtitleMode) -> ISubtitleLayout:
    """Select default layout implementation based on subtitle mode."""
    if mode == SubtitleMode.SENTENCE:
        return SentenceLayout()
    if mode == SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT:
        return WordHighlightLayout()
    if mode == SubtitleMode.WORD:
        return WordOnlyLayout()
    if mode == SubtitleMode.STACKING:
        return StackingLayout()
    return WordHighlightLayout()


def generate_video(
    json_file: str,
    audio_file: str,
    output_video: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    bg_color: Tuple[int, int, int] = (0, 0, 0),
    subtitle_config: Optional[SubtitleConfig] = None,
    subtitle_source: Optional[ISubtitleSource] = None,
    layout: Optional[ISubtitleLayout] = None,
    renderer: Optional[ISubtitleRenderer] = None,
    **extra_config: Any,
) -> None:
    """
    Render a video with subtitles from existing JSON + audio files.

    Use this when you already have TTS output (json_file, audio_file) and want
    to control subtitle behavior via SubtitleConfig and/or custom components.
    
    This is the legacy API maintained for backward compatibility. For generating
    videos from text, use generate_video_from_text() or generate_video_from_file()
    from the api.library module.

    Args:
        json_file: Path to moviepy-style subtitle JSON.
        audio_file: Path to WAV audio.
        output_video: Path for the output MP4.
        width: Video width in pixels.
        height: Video height in pixels.
        fps: Frame rate.
        bg_color: Background RGB tuple.
        subtitle_config: Subtitle appearance and mode. If None, built from
            extra_config or defaults (sentence_with_word_highlight, white/yellow).
        subtitle_source: Optional custom source; if None, JsonSubtitleSource(json_file).
        layout: Optional custom layout; if None, chosen from subtitle_config.mode.
        renderer: Optional custom renderer; if None, PillowSubtitleRenderer().
        **extra_config: Merged into the config dict for SubtitleConfig.from_dict
            (e.g. text_color, highlight_color, subtitle={...}).
    """
    # Build config dict with defaults and user overrides
    cfg: Dict[str, Any] = {
        "json_file": json_file,
        "audio_file": audio_file,
        "output_video": output_video,
        "width": width,
        "height": height,
        "fps": fps,
        "bg_color": bg_color,
        "font_size": 40,
        "text_color": (255, 255, 255),
        "highlight_color": (255, 255, 0),
        **extra_config,
    }
    
    # Build subtitle config if not provided
    if subtitle_config is None:
        subtitle_config = SubtitleConfig.from_dict(cfg)

    # Delegate to renderer with appropriate components
    create_video(
        cfg,
        subtitle_source=subtitle_source if subtitle_source is not None else JsonSubtitleSource(json_file),
        layout=layout if layout is not None else _default_layout(subtitle_config.mode),
        renderer=renderer if renderer is not None else PillowSubtitleRenderer(),
    )
