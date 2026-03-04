"""Modular subtitle pipeline: source, layout, renderer, and composer."""

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
    "ISubtitleSource",
    "ISubtitleLayout",
    "ISubtitleRenderer",
    "SubtitleSegment",
    "WordSegment",
    "PositionedSubtitle",
    "SubtitleLayoutContext",
    "JsonSubtitleSource",
    "SentenceLayout",
    "WordHighlightLayout",
    "WordOnlyLayout",
    "StackingLayout",
    "PillowSubtitleRenderer",
    "SubtitleFrameComposer",
]
