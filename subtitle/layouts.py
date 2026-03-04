"""Subtitle layout strategies: sentence, word-highlight, word-only, rolling."""

from __future__ import annotations

from typing import List

from subtitle_config import SubtitleConfig, SubtitleMode

from subtitle.interfaces import (
    ISubtitleLayout,
    PositionedSubtitle,
    SubtitleLayoutContext,
    SubtitleSegment,
)


def _base_y(context: SubtitleLayoutContext, line_index: int = 0) -> int:
    """Vertical position for one line (single line or first of multiple)."""
    if context.vertical_align == "top":
        return context.y_margin_px + line_index * context.line_height_px
    if context.vertical_align == "center":
        total_h = context.line_height_px
        return (context.height - total_h) // 2 + line_index * context.line_height_px
    # bottom
    return context.height - context.y_margin_px - context.line_height_px * (1 + line_index)


def _anchor_x(context: SubtitleLayoutContext, text_width: int) -> int:
    """Starting x for a line of given width based on align."""
    if context.align == "left":
        return context.x_margin_px
    if context.align == "right":
        return context.width - context.x_margin_px - text_width
    return (context.width - text_width) // 2


def _wrap_sentence_text(text: str, context: SubtitleLayoutContext) -> List[str]:
    """
    Wrap text to fit within context.max_text_width_px using a conservative
    character-width estimate (layout remains renderer-agnostic).
    """
    clean = text.strip()
    if not clean:
        return []

    avg_char_px = max(1, int(context.font_size * 0.55))
    max_chars = max(8, context.max_text_width_px // avg_char_px)
    words = clean.split()

    lines: List[str] = []
    current: List[str] = []
    for word in words:
        tentative = " ".join(current + [word]).strip()
        if current and len(tentative) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))

    return lines


def _line_y_positions(context: SubtitleLayoutContext, line_count: int) -> List[int]:
    """Compute y positions for a multi-line subtitle block."""
    if line_count <= 0:
        return []

    if context.vertical_align == "top":
        start = context.y_margin_px
    elif context.vertical_align == "center":
        block_height = line_count * context.line_height_px
        start = (context.height - block_height) // 2
    else:
        # bottom: keep the last line where the old single-line baseline was.
        bottom_line_y = context.height - context.y_margin_px - context.line_height_px
        start = bottom_line_y - (line_count - 1) * context.line_height_px

    return [start + i * context.line_height_px for i in range(line_count)]


class SentenceLayout(ISubtitleLayout):
    """One sentence at a time, full text in base color."""

    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        if not segments:
            return []
        seg = segments[0]
        lines = _wrap_sentence_text(seg.sentence_text, context)
        if not lines:
            return []

        y_positions = _line_y_positions(context, len(lines))
        return [
            PositionedSubtitle(
                text=line,
                x=0,
                y=y,
                color=config.base_color,
                font_size=context.font_size,
                is_highlight=False,
            )
            for line, y in zip(lines, y_positions)
        ]


class WordHighlightLayout(ISubtitleLayout):
    """Sentence with one word highlighted at a time (word-by-word coloring)."""

    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        if not segments:
            return []
        seg = segments[0]
        y = _base_y(context, 0)
        result: List[PositionedSubtitle] = []
        # We emit one PositionedSubtitle per word so renderer can draw each with its own color.
        # x will be set by renderer when it has font metrics; we use relative order and store
        # highlight flag. Renderer expects list of spans; for word-highlight it draws word by word.
        for w in seg.words:
            is_highlight = w.start_time <= t <= w.end_time
            result.append(
                PositionedSubtitle(
                    text=w.text,
                    x=0,
                    y=y,
                    color=config.highlight_color if is_highlight else config.base_color,
                    font_size=context.font_size,
                    is_highlight=is_highlight,
                )
            )
        return result


class WordOnlyLayout(ISubtitleLayout):
    """Only the current word, typically larger/centered."""

    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        if not segments:
            return []
        seg = segments[0]
        for w in seg.words:
            if w.start_time <= t <= w.end_time:
                y = _base_y(context, 0)
                return [
                    PositionedSubtitle(
                        text=w.text.strip(),
                        x=0,
                        y=y,
                        color=config.highlight_color,
                        font_size=int(context.font_size * 1.2),
                        is_highlight=True,
                    )
                ]
        return []


class RollingLayout(ISubtitleLayout):
    """Multiple lines visible, scrolling (e.g. last N sentences). Expects all segments from composer."""

    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        n = config.rolling.max_visible_lines
        # Segments that have already started by t; take last n (composer passes all segments for rolling).
        started = [s for s in segments if s.start_time <= t]
        visible = started[-n:] if len(started) > n else started
        result: List[PositionedSubtitle] = []
        # Newest (last) at bottom; oldest (first) at top
        for i, seg in enumerate(visible):
            line_index = len(visible) - 1 - i
            y = _base_y(context, line_index)
            result.append(
                PositionedSubtitle(
                    text=seg.sentence_text.strip(),
                    x=0,
                    y=y,
                    color=config.base_color,
                    font_size=context.font_size,
                    is_highlight=False,
                )
            )
        return result
