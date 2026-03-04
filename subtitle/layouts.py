"""Subtitle layout strategies: sentence, word-highlight, word-only, stacking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from subtitle_config import SubtitleConfig, SubtitleMode

from subtitle.interfaces import (
    ISubtitleLayout,
    PositionedSubtitle,
    SubtitleLayoutContext,
    SubtitleSegment,
    WordSegment,
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


@dataclass
class _TimedChunk:
    """A single-line chunk of words with timing derived from word boundaries."""

    text: str
    start_time: float
    end_time: float


def _max_chars_for_context(context: SubtitleLayoutContext) -> int:
    avg_char_px = max(1, int(context.font_size * 0.55))
    return max(8, context.max_text_width_px // avg_char_px)


def _build_single_line_chunks(
    segment: SubtitleSegment,
    context: SubtitleLayoutContext,
    config: SubtitleConfig,
) -> List[_TimedChunk]:
    """
    Split a segment's words into single-line chunks that each fit
    within ``context.max_text_width_px``.  Each chunk's timing spans
    from its first word's start_time to its last word's end_time.
    """
    words = segment.words
    if not words:
        return [
            _TimedChunk(
                text=segment.sentence_text.strip(),
                start_time=segment.start_time,
                end_time=segment.end_time,
            )
        ]

    max_chars = _max_chars_for_context(context)
    max_words = config.max_words_per_chunk

    chunks: List[_TimedChunk] = []
    current_words: List[WordSegment] = []
    current_text = ""

    for w in words:
        word_text = w.text.strip()
        if not word_text:
            continue

        tentative = (current_text + " " + word_text).strip() if current_text else word_text
        hit_word_cap = max_words is not None and len(current_words) >= max_words

        if current_words and (len(tentative) > max_chars or hit_word_cap):
            chunks.append(
                _TimedChunk(
                    text=current_text,
                    start_time=current_words[0].start_time,
                    end_time=current_words[-1].end_time,
                )
            )
            current_words = [w]
            current_text = word_text
        else:
            current_words.append(w)
            current_text = tentative

    if current_words:
        chunks.append(
            _TimedChunk(
                text=current_text,
                start_time=current_words[0].start_time,
                end_time=current_words[-1].end_time,
            )
        )

    return chunks


def _active_chunk_at(t: float, chunks: List[_TimedChunk]) -> Optional[_TimedChunk]:
    """Return the chunk that should be visible at time *t*."""
    if not chunks:
        return None

    for chunk in chunks:
        if chunk.start_time <= t <= chunk.end_time:
            return chunk

    for chunk in reversed(chunks):
        if chunk.start_time <= t:
            return chunk

    return chunks[0]


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
    """One sentence at a time, full text in base color.

    When ``config.multiline_enabled`` is True the sentence is wrapped into
    multiple lines.  When False (the default), the sentence is split into
    timed single-line chunks derived from word timings so that each chunk
    fits on screen without clipping.
    """

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

        if config.multiline_enabled:
            return self._layout_multiline(seg, context, config)

        return self._layout_single_line(t, seg, context, config)

    @staticmethod
    def _layout_multiline(
        seg: SubtitleSegment,
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
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

    @staticmethod
    def _layout_single_line(
        t: float,
        seg: SubtitleSegment,
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        chunks = _build_single_line_chunks(seg, context, config)
        active = _active_chunk_at(t, chunks)
        if active is None:
            return []
        y = _base_y(context, 0)
        return [
            PositionedSubtitle(
                text=active.text,
                x=0,
                y=y,
                color=config.base_color,
                font_size=context.font_size,
                is_highlight=False,
            )
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


class StackingLayout(ISubtitleLayout):
    """Multiple lines visible, stacking (e.g. last N sentences). Expects all segments from composer."""

    def layout_frame(
        self,
        t: float,
        segments: List[SubtitleSegment],
        context: SubtitleLayoutContext,
        config: SubtitleConfig,
    ) -> List[PositionedSubtitle]:
        n = config.stacking.max_visible_lines
        # Segments that have already started by t; take last n (composer passes all segments for stacking).
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
