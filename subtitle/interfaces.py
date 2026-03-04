"""Subtitle interfaces and shared data models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Protocol, Tuple

from subtitle_config import SubtitleConfig

if TYPE_CHECKING:
    from PIL import Image

Color = Tuple[int, int, int]


@dataclass
class WordSegment:
    """Single word with timing."""

    text: str
    start_time: float
    end_time: float


@dataclass
class SubtitleSegment:
    """One sentence/segment with optional word-level data."""

    sentence_text: str
    start_time: float
    end_time: float
    words: List[WordSegment]


@dataclass
class PositionedSubtitle:
    """A text span to draw at a specific position (possibly with per-span color)."""

    text: str
    x: int
    y: int
    color: Color
    font_size: int
    is_highlight: bool = False


@dataclass
class SubtitleLayoutContext:
    """
    Video-size-derived context for layout: font size, margins, max width.
    Built once per video so layouts can adapt to dimensions.
    """

    width: int
    height: int
    font_size: int
    x_margin_px: int
    y_margin_px: int
    max_text_width_px: int
    line_height_px: int
    vertical_align: str
    align: str

    @classmethod
    def from_config(cls, width: int, height: int, config: SubtitleConfig) -> "SubtitleLayoutContext":
        """Compute pixel values from video size and SubtitleConfig."""
        # Font size: scale with height or use fixed
        if config.scale_font_to_height and config.font_size is None:
            k = 0.04
            font_size = max(12, min(int(height * k), 120))
        elif config.font_size is not None:
            font_size = config.font_size
        else:
            font_size = max(12, min(int(height * 0.04), 120))

        x_margin_px = int(width * config.x_margin)
        y_margin_px = int(height * config.y_margin)
        max_text_width_px = int(width * config.max_width_ratio)
        line_height_px = int(font_size * config.line_spacing)

        return cls(
            width=width,
            height=height,
            font_size=font_size,
            x_margin_px=x_margin_px,
            y_margin_px=y_margin_px,
            max_text_width_px=max_text_width_px,
            line_height_px=line_height_px,
            vertical_align=config.vertical_align,
            align=config.align,
        )


class ISubtitleSource(Protocol):
    """Read-only source of subtitle segments (e.g. from JSON file)."""

    def get_segments_for_time(self, t: float) -> List[SubtitleSegment]:
        """Return segments that are active at time t (e.g. current sentence)."""
        ...

    def get_all_segments(self) -> List[SubtitleSegment]:
        """Return all segments in order (for rolling / full timeline)."""
        ...


class ISubtitleLayout(ABC):
    """Turns segments + time into positioned text boxes."""

    @abstractmethod
    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        """Produce positioned subtitle items for the given time and segments."""
        ...


class ISubtitleRenderer(ABC):
    """Draws positioned subtitles onto an image."""

    @abstractmethod
    def render_frame(
        self,
        base_image: "Image.Image",
        layout: List[PositionedSubtitle],
        subtitle_config: SubtitleConfig,
        context: SubtitleLayoutContext,
    ) -> "Image.Image":
        """Draw layout onto base_image and return the result."""
        ...
