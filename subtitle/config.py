from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple, Any


Color = Tuple[int, int, int]


class SubtitleMode(str, Enum):
    SENTENCE = "sentence"
    SENTENCE_WITH_WORD_HIGHLIGHT = "sentence_with_word_highlight"
    WORD = "word"
    STACKING = "stacking"


@dataclass
class StackingConfig:
    """Configuration specific to stacking subtitles."""

    speed: float = 1.0
    max_visible_lines: int = 3
    direction: str = "up"  # could be \"up\" or \"down\"
    fade_old_lines: bool = True


@dataclass
class SubtitleConfig:
    """
    Central configuration for subtitle appearance and behavior.

    This is intentionally decoupled from the raw config dict returned by
    `config.get_config` so it can be constructed either from that dict or
    directly from Python code.
    """

    mode: SubtitleMode = SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT

    # Colors
    base_color: Color = (255, 255, 255)
    highlight_color: Color = (255, 255, 0)
    shadow_color: Optional[Color] = None
    outline_color: Optional[Color] = None

    # Positioning (fractions of width/height)
    vertical_align: str = "bottom"  # \"bottom\", \"center\", \"top\"
    x_margin: float = 0.05
    y_margin: float = 0.05
    max_width_ratio: float = 0.9

    # Font
    font_path: Optional[str] = None
    font_size_strategy: str = "scale_with_height"  # or \"fixed\"
    font_size: Optional[int] = None
    line_spacing: float = 1.0
    align: str = "center"  # \"left\", \"center\", \"right\"

    # Dimension adaptation
    scale_font_to_height: bool = True
    max_lines_for_height: Optional[int] = None

    # Overflow / multiline behavior
    multiline_enabled: bool = False
    overflow_strategy: str = "chunk_single_line"
    min_words_per_chunk: int = 1
    max_words_per_chunk: Optional[int] = None
    prefer_break_on_punctuation: bool = True

    # Stacking behavior
    stacking: StackingConfig = field(default_factory=StackingConfig)

    @staticmethod
    def _parse_mode(raw_mode: Optional[str]) -> SubtitleMode:
        if not raw_mode:
            return SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT

        normalized = raw_mode.lower()
        mapping = {
            "sentence": SubtitleMode.SENTENCE,
            "word": SubtitleMode.WORD,
            "sentence_with_word_highlight": SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
            "sentence-word-highlight": SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
            "sentence_word_highlight": SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
            "stacking": SubtitleMode.STACKING,
        }
        return mapping.get(normalized, SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT)

    @classmethod
    def from_dict(cls, cfg: Dict[str, Any]) -> "SubtitleConfig":
        """
        Build a SubtitleConfig from the global configuration dict.

        - Looks for a nested `subtitle` section first.
        - Falls back to existing top-level keys such as `text_color`,
          `highlight_color`, and `font_size`.
        """
        subtitle_section = cfg.get("subtitle", {}) or {}

        # Colors – fallback to existing top-level values
        base_color: Color = subtitle_section.get(
            "base_color", cfg.get("text_color", (255, 255, 255))
        )
        highlight_color: Color = subtitle_section.get(
            "highlight_color", cfg.get("highlight_color", (255, 255, 0))
        )

        # Font
        font_path = subtitle_section.get("font_path")
        font_size_strategy = subtitle_section.get("font_size_strategy", "scale_with_height")
        # If a specific font size is given in subtitle section, prefer that.
        font_size = subtitle_section.get("font_size", cfg.get("font_size"))

        # Positioning / layout
        vertical_align = subtitle_section.get("vertical_align", "bottom")
        x_margin = float(subtitle_section.get("x_margin", 0.05))
        y_margin = float(subtitle_section.get("y_margin", 0.05))
        max_width_ratio = float(subtitle_section.get("max_width_ratio", 0.9))

        # Mode
        mode = cls._parse_mode(subtitle_section.get("mode"))

        # Dimension adaptation
        scale_font_to_height = bool(subtitle_section.get("scale_font_to_height", True))
        max_lines_for_height = subtitle_section.get("max_lines_for_height")

        # Optional advanced styling
        shadow_color = subtitle_section.get("shadow_color")
        outline_color = subtitle_section.get("outline_color")
        line_spacing = float(subtitle_section.get("line_spacing", 1.0))
        align = subtitle_section.get("align", "center")

        # Overflow / multiline
        multiline_enabled = bool(subtitle_section.get("multiline_enabled", False))
        overflow_strategy = subtitle_section.get("overflow_strategy", "chunk_single_line")
        min_words_per_chunk = int(subtitle_section.get("min_words_per_chunk", 1))
        max_words_per_chunk = subtitle_section.get("max_words_per_chunk")
        if max_words_per_chunk is not None:
            max_words_per_chunk = int(max_words_per_chunk)
        prefer_break_on_punctuation = bool(
            subtitle_section.get("prefer_break_on_punctuation", True)
        )

        # Stacking config
        stacking_section = subtitle_section.get("stacking", {}) or {}
        stacking = StackingConfig(
            speed=float(stacking_section.get("speed", 1.0)),
            max_visible_lines=int(stacking_section.get("max_visible_lines", 3)),
            direction=stacking_section.get("direction", "up"),
            fade_old_lines=bool(stacking_section.get("fade_old_lines", True)),
        )

        return cls(
            mode=mode,
            base_color=base_color,
            highlight_color=highlight_color,
            shadow_color=shadow_color,
            outline_color=outline_color,
            vertical_align=vertical_align,
            x_margin=x_margin,
            y_margin=y_margin,
            max_width_ratio=max_width_ratio,
            font_path=font_path,
            font_size_strategy=font_size_strategy,
            font_size=font_size,
            line_spacing=line_spacing,
            align=align,
            scale_font_to_height=scale_font_to_height,
            max_lines_for_height=max_lines_for_height,
            multiline_enabled=multiline_enabled,
            overflow_strategy=overflow_strategy,
            min_words_per_chunk=min_words_per_chunk,
            max_words_per_chunk=max_words_per_chunk,
            prefer_break_on_punctuation=prefer_break_on_punctuation,
            stacking=stacking,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert SubtitleConfig to a dictionary format compatible with from_dict().

        Returns a nested dictionary with a 'subtitle' section containing all
        configuration values.
        """
        return {
            "mode": self.mode.value,
            "base_color": self.base_color,
            "highlight_color": self.highlight_color,
            "shadow_color": self.shadow_color,
            "outline_color": self.outline_color,
            "vertical_align": self.vertical_align,
            "x_margin": self.x_margin,
            "y_margin": self.y_margin,
            "max_width_ratio": self.max_width_ratio,
            "font_path": self.font_path,
            "font_size_strategy": self.font_size_strategy,
            "font_size": self.font_size,
            "line_spacing": self.line_spacing,
            "align": self.align,
            "scale_font_to_height": self.scale_font_to_height,
            "max_lines_for_height": self.max_lines_for_height,
            "multiline_enabled": self.multiline_enabled,
            "overflow_strategy": self.overflow_strategy,
            "min_words_per_chunk": self.min_words_per_chunk,
            "max_words_per_chunk": self.max_words_per_chunk,
            "prefer_break_on_punctuation": self.prefer_break_on_punctuation,
            "stacking": {
                "speed": self.stacking.speed,
                "max_visible_lines": self.stacking.max_visible_lines,
                "direction": self.stacking.direction,
                "fade_old_lines": self.stacking.fade_old_lines,
            },
        }


