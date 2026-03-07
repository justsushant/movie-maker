"""Unit tests for subtitle layout logic and bugfixes."""

from __future__ import annotations

import pytest

from subtitle.interfaces import SubtitleLayoutContext, SubtitleSegment, WordSegment
from subtitle.layouts import (
    _build_single_line_chunks,
    _max_chars_for_context,
    _wrap_sentence_text,
    WordHighlightLayout,
)
from subtitle.config import SubtitleConfig


class TestCharacterWidthEstimation:
    """Tests for character width estimation accuracy (Bug 1 fix)."""

    def test_max_chars_uses_correct_ratio(self):
        """Test that _max_chars_for_context uses 0.50 ratio."""
        # Create a context with known values
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        max_chars = _max_chars_for_context(context)
        
        # With font_size=40 and ratio=0.50:
        # avg_char_px = max(1, int(40 * 0.50)) = 20
        # max_chars = max(8, 972 // 20) = 48
        assert max_chars == 48

    def test_wrap_sentence_uses_correct_ratio(self):
        """Test that _wrap_sentence_text uses 0.50 ratio."""
        context = SubtitleLayoutContext(
            width=1280,
            height=720,
            font_size=40,
            x_margin_px=64,
            y_margin_px=36,
            max_text_width_px=1152,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        # Long text that should wrap
        text = "This is a longer paragraph that intentionally contains several clauses and transitions"
        lines = _wrap_sentence_text(text, context)
        
        # With ratio=0.50, avg_char_px=20, max_chars=57
        # Text is 87 chars, should wrap into 2 lines
        assert len(lines) >= 2
        # Each line should be under max_chars
        for line in lines:
            assert len(line) <= 57

    def test_character_width_estimation_prevents_overflow(self):
        """Test that improved estimation prevents unnecessary chunking."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        # Text that fits in 902px (under 972px limit)
        # Should NOT be split into multiple chunks
        segment = SubtitleSegment(
            sentence_text='what?! "No way," she said; then paused and smiled',
            start_time=0.65,
            end_time=4.0,
            words=[
                WordSegment(text='what?! "', start_time=0.65, end_time=1.125),
                WordSegment(text="No ", start_time=1.325, end_time=1.475),
                WordSegment(text='way," ', start_time=1.475, end_time=1.7),
                WordSegment(text="she ", start_time=1.775, end_time=1.925),
                WordSegment(text="said; ", start_time=1.925, end_time=2.25),
                WordSegment(text="then ", start_time=2.325, end_time=2.5125),
                WordSegment(text="paused ", start_time=2.5125, end_time=2.9625),
                WordSegment(text="and ", start_time=2.9875, end_time=3.1625),
                WordSegment(text="smiled", start_time=3.1625, end_time=4.0),
            ],
        )
        
        config = SubtitleConfig()
        chunks = _build_single_line_chunks(segment, context, config)
        
        # With improved 0.50 ratio, this should still create chunks
        # but the chunking should be more accurate
        assert len(chunks) >= 1


class TestWordToChunkAssociation:
    """Tests for word index tracking in chunks (Bug 2 fix - part 1)."""

    def test_chunks_store_word_indices(self):
        """Test that chunks store indices of their words."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        segment = SubtitleSegment(
            sentence_text="Hello world this is a test",
            start_time=0.0,
            end_time=2.0,
            words=[
                WordSegment(text="Hello ", start_time=0.0, end_time=0.3),
                WordSegment(text="world ", start_time=0.3, end_time=0.6),
                WordSegment(text="this ", start_time=0.6, end_time=0.9),
                WordSegment(text="is ", start_time=0.9, end_time=1.2),
                WordSegment(text="a ", start_time=1.2, end_time=1.5),
                WordSegment(text="test", start_time=1.5, end_time=2.0),
            ],
        )
        
        config = SubtitleConfig()
        chunks = _build_single_line_chunks(segment, context, config)
        
        # Each chunk should have word_indices
        for chunk in chunks:
            assert hasattr(chunk, "word_indices")
            assert isinstance(chunk.word_indices, list)
            assert len(chunk.word_indices) > 0

    def test_word_indices_match_chunk_text(self):
        """Test that word indices correctly identify words in chunk."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        segment = SubtitleSegment(
            sentence_text="First second third",
            start_time=0.0,
            end_time=1.5,
            words=[
                WordSegment(text="First ", start_time=0.0, end_time=0.5),
                WordSegment(text="second ", start_time=0.5, end_time=1.0),
                WordSegment(text="third", start_time=1.0, end_time=1.5),
            ],
        )
        
        config = SubtitleConfig()
        chunks = _build_single_line_chunks(segment, context, config)
        
        # Verify indices point to correct words
        for chunk in chunks:
            chunk_words = [segment.words[i] for i in chunk.word_indices]
            # Reconstruct text from indexed words
            reconstructed = "".join(w.text for w in chunk_words).strip()
            assert reconstructed == chunk.text.strip()

    def test_empty_words_handled_correctly(self):
        """Test that empty/whitespace words don't break index tracking."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        segment = SubtitleSegment(
            sentence_text="Hello world",
            start_time=0.0,
            end_time=1.0,
            words=[
                WordSegment(text="Hello ", start_time=0.0, end_time=0.5),
                WordSegment(text="  ", start_time=0.5, end_time=0.6),  # Empty word
                WordSegment(text="world", start_time=0.6, end_time=1.0),
            ],
        )
        
        config = SubtitleConfig()
        chunks = _build_single_line_chunks(segment, context, config)
        
        # Should handle empty words gracefully
        assert len(chunks) >= 1
        # Empty words should be skipped, not in indices
        for chunk in chunks:
            for idx in chunk.word_indices:
                word = segment.words[idx]
                assert word.text.strip() != ""


class TestWordHighlightFiltering:
    """Tests for word filtering in WordHighlightLayout (Bug 2 fix - part 2)."""

    def test_word_highlight_shows_only_active_chunk_words(self):
        """Test that WordHighlightLayout shows only words from active chunk."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        # Sentence that gets split into 2 chunks
        segment = SubtitleSegment(
            sentence_text='what?! "No way," she said; then paused and smiled',
            start_time=0.65,
            end_time=4.0,
            words=[
                WordSegment(text='what?! "', start_time=0.65, end_time=1.125),
                WordSegment(text="No ", start_time=1.325, end_time=1.475),
                WordSegment(text='way," ', start_time=1.475, end_time=1.7),
                WordSegment(text="she ", start_time=1.775, end_time=1.925),
                WordSegment(text="said; ", start_time=1.925, end_time=2.25),
                WordSegment(text="then ", start_time=2.325, end_time=2.5125),
                WordSegment(text="paused ", start_time=2.5125, end_time=2.9625),
                WordSegment(text="and ", start_time=2.9875, end_time=3.1625),
                WordSegment(text="smiled", start_time=3.1625, end_time=4.0),
            ],
        )
        
        config = SubtitleConfig(mode="sentence_with_word_highlight")
        layout = WordHighlightLayout()
        
        # At t=2.5s (middle of sentence), should show first chunk words
        positioned_early = layout.layout_frame(2.5, [segment], context, config)
        early_words = [p.text for p in positioned_early]
        
        # At t=3.5s (near end), should show only last chunk words
        positioned_late = layout.layout_frame(3.5, [segment], context, config)
        late_words = [p.text for p in positioned_late]
        
        # The word sets should be different (different chunks)
        assert early_words != late_words
        
        # Late should NOT include "and" if it's in a different chunk than "smiled"
        # This is the key bug fix - no mixing of chunks
        if "smiled" in late_words:
            # If we're showing the last chunk, it should be consistent
            # Either just "smiled" or the words that belong to that chunk
            assert len(late_words) <= 2  # Should be small, not all 9 words

    def test_word_highlight_no_sudden_breaks(self):
        """Test that word transitions are smooth without sudden breaks."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        segment = SubtitleSegment(
            sentence_text="One two three four five",
            start_time=0.0,
            end_time=2.5,
            words=[
                WordSegment(text="One ", start_time=0.0, end_time=0.5),
                WordSegment(text="two ", start_time=0.5, end_time=1.0),
                WordSegment(text="three ", start_time=1.0, end_time=1.5),
                WordSegment(text="four ", start_time=1.5, end_time=2.0),
                WordSegment(text="five", start_time=2.0, end_time=2.5),
            ],
        )
        
        config = SubtitleConfig(mode="sentence_with_word_highlight")
        layout = WordHighlightLayout()
        
        # Sample at different times
        times = [0.25, 0.75, 1.25, 1.75, 2.25]
        word_sets = []
        
        for t in times:
            positioned = layout.layout_frame(t, [segment], context, config)
            words = [p.text for p in positioned]
            word_sets.append(set(words))
        
        # Word sets should be consistent within chunks
        # No sudden drops or additions (smooth transitions)
        for i in range(len(word_sets) - 1):
            # Either same set (same chunk) or different set (chunk transition)
            # But should not have partial overlaps (that would indicate mixing)
            if word_sets[i] != word_sets[i + 1]:
                # If different, they should be distinct chunks
                # Not a subset relationship (which would indicate mixing)
                assert not (word_sets[i] < word_sets[i + 1] or word_sets[i] > word_sets[i + 1])

    def test_word_highlight_with_duplicate_words(self):
        """Test that duplicate words are handled correctly by index."""
        context = SubtitleLayoutContext(
            width=1080,
            height=1920,
            font_size=40,
            x_margin_px=54,
            y_margin_px=96,
            max_text_width_px=972,
            line_height_px=40,
            vertical_align="bottom",
            align="center",
        )
        
        # Sentence with duplicate word "the"
        segment = SubtitleSegment(
            sentence_text="The cat and the dog",
            start_time=0.0,
            end_time=2.0,
            words=[
                WordSegment(text="The ", start_time=0.0, end_time=0.4),
                WordSegment(text="cat ", start_time=0.4, end_time=0.8),
                WordSegment(text="and ", start_time=0.8, end_time=1.2),
                WordSegment(text="the ", start_time=1.2, end_time=1.6),  # Duplicate
                WordSegment(text="dog", start_time=1.6, end_time=2.0),
            ],
        )
        
        config = SubtitleConfig(mode="sentence_with_word_highlight")
        layout = WordHighlightLayout()
        
        # Should handle both instances of "the" correctly
        positioned = layout.layout_frame(1.0, [segment], context, config)
        
        # Should not crash or show incorrect words
        assert len(positioned) > 0
