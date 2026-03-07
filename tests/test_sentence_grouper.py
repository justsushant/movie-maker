"""
Unit tests for SentenceGrouper.

**Validates: Requirements 6.3**

Tests sentence grouping logic including sentence boundary detection,
duration-based splitting, last word handling, and empty input.
"""

from __future__ import annotations

import pytest

from processing.grouping import SentenceGrouper
from processing.models import WordToken, SentenceSegment


class TestSentenceGrouperBasicSentences:
    """Test basic sentence boundary detection."""
    
    def test_single_sentence_with_period(self):
        """Test grouping a single sentence ending with a period."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world. ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world."
        assert result[0].start_time == 0.0
        assert result[0].end_time == 1.0
        assert len(result[0].words) == 2
    
    def test_single_sentence_with_question_mark(self):
        """Test grouping a sentence ending with a question mark."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="How ", clean_word="How", start_time=0.0, end_time=0.3),
            WordToken(text="are ", clean_word="are", start_time=0.3, end_time=0.6),
            WordToken(text="you? ", clean_word="you?", start_time=0.6, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "How are you?"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 1.0
        assert len(result[0].words) == 3
    
    def test_single_sentence_with_exclamation_mark(self):
        """Test grouping a sentence ending with an exclamation mark."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Stop! ", clean_word="Stop!", start_time=0.0, end_time=0.5),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Stop!"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
        assert len(result[0].words) == 1
    
    def test_multiple_sentences_with_periods(self):
        """Test grouping multiple sentences each ending with a period."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="First ", clean_word="First", start_time=0.0, end_time=0.5),
            WordToken(text="sentence. ", clean_word="sentence.", start_time=0.5, end_time=1.0),
            WordToken(text="Second ", clean_word="Second", start_time=1.0, end_time=1.5),
            WordToken(text="sentence. ", clean_word="sentence.", start_time=1.5, end_time=2.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].sentence_text == "First sentence."
        assert result[0].start_time == 0.0
        assert result[0].end_time == 1.0
        assert result[1].sentence_text == "Second sentence."
        assert result[1].start_time == 1.0
        assert result[1].end_time == 2.0
    
    def test_mixed_punctuation_endings(self):
        """Test sentences with different punctuation marks."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello. ", clean_word="Hello.", start_time=0.0, end_time=0.5),
            WordToken(text="How ", clean_word="How", start_time=0.5, end_time=0.8),
            WordToken(text="are ", clean_word="are", start_time=0.8, end_time=1.0),
            WordToken(text="you? ", clean_word="you?", start_time=1.0, end_time=1.3),
            WordToken(text="Great! ", clean_word="Great!", start_time=1.3, end_time=1.8),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 3
        assert result[0].sentence_text == "Hello."
        assert result[1].sentence_text == "How are you?"
        assert result[2].sentence_text == "Great!"


class TestSentenceGrouperDurationSplitting:
    """Test duration-based sentence splitting."""
    
    def test_split_on_max_duration(self):
        """Test that sentences are split when exceeding max duration."""
        grouper = SentenceGrouper(max_duration=2.0)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=0.5),
            WordToken(text="Word2 ", clean_word="Word2", start_time=0.5, end_time=1.0),
            WordToken(text="Word3 ", clean_word="Word3", start_time=1.0, end_time=1.5),
            WordToken(text="Word4 ", clean_word="Word4", start_time=1.5, end_time=2.5),  # Exceeds 2.0s
            WordToken(text="Word5 ", clean_word="Word5", start_time=2.5, end_time=3.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].sentence_text == "Word1 Word2 Word3 Word4"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 2.5
        assert result[1].sentence_text == "Word5"
        assert result[1].start_time == 2.5
        assert result[1].end_time == 3.0
    
    def test_duration_exactly_at_limit(self):
        """Test behavior when duration exactly equals max_duration."""
        grouper = SentenceGrouper(max_duration=2.0)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=1.0),
            WordToken(text="Word2 ", clean_word="Word2", start_time=1.0, end_time=2.0),  # Exactly 2.0s
            WordToken(text="Word3 ", clean_word="Word3", start_time=2.0, end_time=3.0),
        ]
        
        result = grouper.group(words)
        
        # At exactly max_duration, should split
        assert len(result) == 2
        assert result[0].sentence_text == "Word1 Word2"
        assert result[1].sentence_text == "Word3"
    
    def test_custom_max_duration(self):
        """Test using a custom max_duration value."""
        grouper = SentenceGrouper(max_duration=1.0)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=0.5),
            WordToken(text="Word2 ", clean_word="Word2", start_time=0.5, end_time=1.5),  # Exceeds 1.0s
            WordToken(text="Word3 ", clean_word="Word3", start_time=1.5, end_time=2.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].sentence_text == "Word1 Word2"
        assert result[1].sentence_text == "Word3"
    
    def test_punctuation_takes_precedence_over_duration(self):
        """Test that punctuation boundaries are respected even within duration limit."""
        grouper = SentenceGrouper(max_duration=10.0)  # Very long duration
        words = [
            WordToken(text="Short. ", clean_word="Short.", start_time=0.0, end_time=0.5),
            WordToken(text="Next ", clean_word="Next", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        # Should split on punctuation even though duration is well under limit
        assert len(result) == 2
        assert result[0].sentence_text == "Short."
        assert result[1].sentence_text == "Next"


class TestSentenceGrouperLastWordHandling:
    """Test handling of the last word in the input."""
    
    def test_last_word_without_punctuation(self):
        """Test that the last word is included even without punctuation."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world ", clean_word="world", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 1.0
        assert len(result[0].words) == 2
    
    def test_last_word_with_punctuation(self):
        """Test that the last word with punctuation creates a proper sentence."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world. ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world."
        assert len(result[0].words) == 2
    
    def test_single_word_as_last(self):
        """Test a single word as the entire input."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Word ", clean_word="Word", start_time=0.0, end_time=0.5),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Word"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
    
    def test_last_word_after_sentence_boundary(self):
        """Test that last word forms its own sentence after a boundary."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="First. ", clean_word="First.", start_time=0.0, end_time=0.5),
            WordToken(text="Last ", clean_word="Last", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].sentence_text == "First."
        assert result[1].sentence_text == "Last"


class TestSentenceGrouperEmptyInput:
    """Test handling of empty and edge case inputs."""
    
    def test_empty_word_list(self):
        """Test that empty word list returns empty result."""
        grouper = SentenceGrouper()
        words = []
        
        result = grouper.group(words)
        
        assert result == []
        assert len(result) == 0
    
    def test_empty_word_list_custom_duration(self):
        """Test empty list with custom max_duration."""
        grouper = SentenceGrouper(max_duration=3.0)
        words = []
        
        result = grouper.group(words)
        
        assert result == []


class TestSentenceGrouperWhitespaceHandling:
    """Test whitespace handling in sentence text."""
    
    def test_trailing_whitespace_stripped(self):
        """Test that trailing whitespace is stripped from sentence text."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world.   ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world."
        assert not result[0].sentence_text.endswith("   ")
    
    def test_leading_whitespace_stripped(self):
        """Test that leading whitespace is stripped from sentence text."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="   Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world. ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world."
        assert not result[0].sentence_text.startswith("   ")
    
    def test_internal_whitespace_preserved(self):
        """Test that internal whitespace between words is preserved."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello  ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world. ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Hello  world."
    
    def test_words_without_whitespace(self):
        """Test words that have no trailing whitespace."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world.", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Helloworld."


class TestSentenceGrouperTimingAccuracy:
    """Test that timing information is accurate."""
    
    def test_sentence_timing_from_first_and_last_word(self):
        """Test that sentence timing uses first word start and last word end."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="First ", clean_word="First", start_time=1.0, end_time=1.5),
            WordToken(text="middle ", clean_word="middle", start_time=1.5, end_time=2.0),
            WordToken(text="last. ", clean_word="last.", start_time=2.0, end_time=2.5),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].start_time == 1.0
        assert result[0].end_time == 2.5
    
    def test_multiple_sentences_timing(self):
        """Test timing for multiple sentences."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="First. ", clean_word="First.", start_time=0.0, end_time=0.5),
            WordToken(text="Second ", clean_word="Second", start_time=0.5, end_time=1.0),
            WordToken(text="sentence. ", clean_word="sentence.", start_time=1.0, end_time=1.5),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
        assert result[1].start_time == 0.5
        assert result[1].end_time == 1.5
    
    def test_timing_with_duration_split(self):
        """Test timing accuracy when splitting on duration."""
        grouper = SentenceGrouper(max_duration=1.0)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=0.5),
            WordToken(text="Word2 ", clean_word="Word2", start_time=0.5, end_time=1.5),  # Exceeds 1.0s
            WordToken(text="Word3 ", clean_word="Word3", start_time=1.5, end_time=2.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 2
        assert result[0].start_time == 0.0
        assert result[0].end_time == 1.5
        assert result[1].start_time == 1.5
        assert result[1].end_time == 2.0


class TestSentenceGrouperWordListPreservation:
    """Test that word lists are correctly preserved in segments."""
    
    def test_words_list_contains_all_words(self):
        """Test that the words list contains all words in the sentence."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="One ", clean_word="One", start_time=0.0, end_time=0.5),
            WordToken(text="two ", clean_word="two", start_time=0.5, end_time=1.0),
            WordToken(text="three. ", clean_word="three.", start_time=1.0, end_time=1.5),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert len(result[0].words) == 3
        assert result[0].words[0].clean_word == "One"
        assert result[0].words[1].clean_word == "two"
        assert result[0].words[2].clean_word == "three."
    
    def test_words_list_independent_from_accumulator(self):
        """Test that each sentence gets its own word list."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="First. ", clean_word="First.", start_time=0.0, end_time=0.5),
            WordToken(text="Second. ", clean_word="Second.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        # Each sentence should have its own word list
        assert len(result[0].words) == 1
        assert len(result[1].words) == 1
        assert result[0].words[0].text == "First. "
        assert result[1].words[0].text == "Second. "
        
        # The two sentences should have different word lists
        assert result[0].words is not result[1].words
    
    def test_words_list_preserves_all_attributes(self):
        """Test that all word attributes are preserved in the words list."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world. ", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert result[0].words[0].text == "Hello "
        assert result[0].words[0].clean_word == "Hello"
        assert result[0].words[0].start_time == 0.0
        assert result[0].words[0].end_time == 0.5
        assert result[0].words[1].text == "world. "
        assert result[0].words[1].clean_word == "world."
        assert result[0].words[1].start_time == 0.5
        assert result[0].words[1].end_time == 1.0


class TestSentenceGrouperComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_paragraph_with_multiple_sentence_types(self):
        """Test a paragraph with statements, questions, and exclamations."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="This ", clean_word="This", start_time=0.0, end_time=0.3),
            WordToken(text="is ", clean_word="is", start_time=0.3, end_time=0.5),
            WordToken(text="great. ", clean_word="great.", start_time=0.5, end_time=0.8),
            WordToken(text="Isn't ", clean_word="Isn't", start_time=0.8, end_time=1.1),
            WordToken(text="it? ", clean_word="it?", start_time=1.1, end_time=1.3),
            WordToken(text="Yes! ", clean_word="Yes!", start_time=1.3, end_time=1.6),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 3
        assert result[0].sentence_text == "This is great."
        assert result[1].sentence_text == "Isn't it?"
        assert result[2].sentence_text == "Yes!"
    
    def test_long_sentence_with_duration_split(self):
        """Test a long sentence that gets split by duration."""
        grouper = SentenceGrouper(max_duration=2.0)
        words = [
            WordToken(text="This ", clean_word="This", start_time=0.0, end_time=0.5),
            WordToken(text="is ", clean_word="is", start_time=0.5, end_time=0.8),
            WordToken(text="a ", clean_word="a", start_time=0.8, end_time=1.0),
            WordToken(text="very ", clean_word="very", start_time=1.0, end_time=1.3),
            WordToken(text="long ", clean_word="long", start_time=1.3, end_time=1.6),
            WordToken(text="sentence ", clean_word="sentence", start_time=1.6, end_time=2.0),
            WordToken(text="without ", clean_word="without", start_time=2.0, end_time=2.5),
            WordToken(text="punctuation ", clean_word="punctuation", start_time=2.5, end_time=3.0),
        ]
        
        result = grouper.group(words)
        
        # Should split when duration exceeds 2.0s
        assert len(result) == 2
        assert result[0].end_time - result[0].start_time >= 2.0
        assert "This is a very long sentence" in result[0].sentence_text
        assert "without punctuation" in result[1].sentence_text
    
    def test_multiple_punctuation_marks(self):
        """Test handling of multiple punctuation marks (ellipsis, etc.)."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Wait... ", clean_word="Wait...", start_time=0.0, end_time=0.5),
            WordToken(text="What?! ", clean_word="What?!", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        # Both should be detected as sentence endings
        assert len(result) == 2
        assert result[0].sentence_text == "Wait..."
        assert result[1].sentence_text == "What?!"
    
    def test_sentence_with_abbreviations(self):
        """Test that abbreviations with periods don't cause premature splits."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Dr. ", clean_word="Dr.", start_time=0.0, end_time=0.3),
            WordToken(text="Smith ", clean_word="Smith", start_time=0.3, end_time=0.6),
            WordToken(text="arrived. ", clean_word="arrived.", start_time=0.6, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        # Dr. should trigger a split since it ends with period
        assert len(result) == 2
        assert result[0].sentence_text == "Dr."
        assert result[1].sentence_text == "Smith arrived."
    
    def test_mixed_duration_and_punctuation_splits(self):
        """Test combination of duration-based and punctuation-based splits."""
        grouper = SentenceGrouper(max_duration=1.5)
        words = [
            WordToken(text="Short. ", clean_word="Short.", start_time=0.0, end_time=0.5),
            WordToken(text="This ", clean_word="This", start_time=0.5, end_time=0.8),
            WordToken(text="is ", clean_word="is", start_time=0.8, end_time=1.0),
            WordToken(text="longer ", clean_word="longer", start_time=1.0, end_time=1.5),
            WordToken(text="text ", clean_word="text", start_time=1.5, end_time=2.5),  # Exceeds duration
            WordToken(text="here. ", clean_word="here.", start_time=2.5, end_time=3.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 3
        assert result[0].sentence_text == "Short."
        # Second sentence split by duration
        assert "This is longer text" in result[1].sentence_text
        assert result[2].sentence_text == "here."


class TestSentenceGrouperEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_duration_words(self):
        """Test handling of words with zero duration."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=1.0, end_time=1.0),
            WordToken(text="Word2. ", clean_word="Word2.", start_time=1.0, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Word1 Word2."
        assert result[0].start_time == 1.0
        assert result[0].end_time == 1.0
    
    def test_very_small_max_duration(self):
        """Test with a very small max_duration value."""
        grouper = SentenceGrouper(max_duration=0.1)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=0.5),
            WordToken(text="Word2 ", clean_word="Word2", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        # Each word should be its own sentence due to small duration
        assert len(result) == 2
    
    def test_very_large_max_duration(self):
        """Test with a very large max_duration value."""
        grouper = SentenceGrouper(max_duration=1000.0)
        words = [
            WordToken(text="Word1 ", clean_word="Word1", start_time=0.0, end_time=10.0),
            WordToken(text="Word2 ", clean_word="Word2", start_time=10.0, end_time=20.0),
            WordToken(text="Word3 ", clean_word="Word3", start_time=20.0, end_time=30.0),
        ]
        
        result = grouper.group(words)
        
        # All words should be in one sentence since duration is huge
        assert len(result) == 1
        assert len(result[0].words) == 3
    
    def test_punctuation_at_end_with_no_whitespace(self):
        """Test punctuation detection when there's no trailing whitespace."""
        grouper = SentenceGrouper()
        words = [
            WordToken(text="Hello", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world.", clean_word="world.", start_time=0.5, end_time=1.0),
        ]
        
        result = grouper.group(words)
        
        assert len(result) == 1
        assert result[0].sentence_text == "Helloworld."
