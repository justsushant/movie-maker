"""Modular subtitle pipeline: source, layout, renderer, and composer."""

from subtitle.config import (
    Color,
    StackingConfig,
    SubtitleConfig,
    SubtitleMode,
)
from subtitle.interfaces import (
    ISubtitleLayout,
    ISubtitleRenderer,
    ISubtitleSource,
    PositionedSubtitle,
    SubtitleLayoutContext,
    SubtitleSegment,
    WordSegment,
)
from subtitle.source import JsonSubtitleSource
from subtitle.layouts import (
    StackingLayout,
    SentenceLayout,
    WordHighlightLayout,
    WordOnlyLayout,
)
from subtitle.renderer import PillowSubtitleRenderer
from subtitle.composer import SubtitleFrameComposer

__all__ = [
    # Config
    "Color",
    "StackingConfig",
    "SubtitleConfig",
    "SubtitleMode",
    # Interfaces
    "ISubtitleSource",
    "ISubtitleLayout",
    "ISubtitleRenderer",
    "SubtitleSegment",
    "WordSegment",
    "PositionedSubtitle",
    "SubtitleLayoutContext",
    # Implementations
    "JsonSubtitleSource",
    "SentenceLayout",
    "WordHighlightLayout",
    "WordOnlyLayout",
    "StackingLayout",
    "PillowSubtitleRenderer",
    "SubtitleFrameComposer",
]
