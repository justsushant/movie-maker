"""
Unit tests for PunctuationMerger.

**Validates: Requirements 6.2**

Tests punctuation merging logic including trailing punctuation,
standalone punctuation handling, empty input, and words without punctuation.
"""

from __future__ import annotations

import pytest

from processing.punctuation import PunctuationMerger
from processing.models import WordToken
from tts.interfaces import TTSToken


class TestPunctuationMergerBasicMerging:
    """Test basic punctuation merging functionality."""
    
    def test_merge_trailing_comma(self):
        """Test merging a trailing comma into the preceding word."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text=",", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Hello , "
        assert result[0].clean_word == "Hello"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
    
    def test_merge_trailing_period(self):
        """Test merging a trailing period into the preceding word."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="world", whitespace="", start_ts=1.0, end_ts=1.5),
            TTSToken(text=".", whitespace="", start_ts=1.5, end_ts=1.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "world."
        assert result[0].clean_word == "world"
        assert result[0].start_time == 1.0
        assert result[0].end_time == 1.5
    
    def test_merge_multiple_punctuation(self):
        """Test merging multiple punctuation marks into the preceding word."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Wait", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text=".", whitespace="", start_ts=0.5, end_ts=0.6),
            TTSToken(text=".", whitespace="", start_ts=0.6, end_ts=0.7),
            TTSToken(text=".", whitespace=" ", start_ts=0.7, end_ts=0.8),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Wait... "
        assert result[0].clean_word == "Wait"
    
    def test_merge_exclamation_mark(self):
        """Test merging an exclamation mark into the preceding word."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Stop", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text="!", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Stop! "
        assert result[0].clean_word == "Stop"
    
    def test_merge_question_mark(self):
        """Test merging a question mark into the preceding word."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Why", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text="?", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Why? "
        assert result[0].clean_word == "Why"


class TestPunctuationMergerStandalonePunctuation:
    """Test handling of standalone punctuation tokens."""
    
    def test_standalone_punctuation_at_start(self):
        """Test that standalone punctuation at start is kept as-is."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text=".", whitespace=" ", start_ts=0.0, end_ts=0.1),
            TTSToken(text="Hello", whitespace=" ", start_ts=0.1, end_ts=0.5),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == ". "
        assert result[0].clean_word == "."
        assert result[1].text == "Hello "
        assert result[1].clean_word == "Hello"
    
    def test_multiple_standalone_punctuation_at_start(self):
        """Test multiple standalone punctuation marks at start."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text=".", whitespace="", start_ts=0.0, end_ts=0.1),
            TTSToken(text=".", whitespace="", start_ts=0.1, end_ts=0.2),
            TTSToken(text=".", whitespace=" ", start_ts=0.2, end_ts=0.3),
            TTSToken(text="word", whitespace=" ", start_ts=0.3, end_ts=0.8),
        ]
        
        result = merger.merge(tokens)
        
        # First punctuation becomes a token, subsequent ones merge into it
        assert len(result) == 2
        assert result[0].text == "... "
        assert result[1].text == "word "
    
    def test_only_punctuation_tokens(self):
        """Test input with only punctuation tokens."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text=".", whitespace=" ", start_ts=0.0, end_ts=0.1),
            TTSToken(text=",", whitespace=" ", start_ts=0.1, end_ts=0.2),
            TTSToken(text="!", whitespace=" ", start_ts=0.2, end_ts=0.3),
        ]
        
        result = merger.merge(tokens)
        
        # First punctuation is kept, rest merge into it
        assert len(result) == 1
        assert result[0].text == ". , ! "
        assert result[0].clean_word == "."


class TestPunctuationMergerEmptyInput:
    """Test handling of empty and edge case inputs."""
    
    def test_empty_token_list(self):
        """Test that empty token list returns empty result."""
        merger = PunctuationMerger()
        tokens = []
        
        result = merger.merge(tokens)
        
        assert result == []
        assert len(result) == 0
    
    def test_single_word_token(self):
        """Test single word token without punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace=" ", start_ts=0.0, end_ts=0.5),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Hello "
        assert result[0].clean_word == "Hello"
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
    
    def test_single_punctuation_token(self):
        """Test single punctuation token."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text=".", whitespace=" ", start_ts=0.0, end_ts=0.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == ". "
        assert result[0].clean_word == "."


class TestPunctuationMergerWordsWithoutPunctuation:
    """Test handling of words without punctuation."""
    
    def test_multiple_words_no_punctuation(self):
        """Test multiple words without any punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text="world", whitespace=" ", start_ts=0.5, end_ts=1.0),
            TTSToken(text="today", whitespace=" ", start_ts=1.0, end_ts=1.5),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 3
        assert result[0].text == "Hello "
        assert result[0].clean_word == "Hello"
        assert result[1].text == "world "
        assert result[1].clean_word == "world"
        assert result[2].text == "today "
        assert result[2].clean_word == "today"
    
    def test_words_with_numbers_no_punctuation(self):
        """Test words containing numbers without punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Test123", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text="456", whitespace=" ", start_ts=0.5, end_ts=1.0),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == "Test123 "
        assert result[0].clean_word == "Test123"
        assert result[1].text == "456 "
        assert result[1].clean_word == "456"
    
    def test_words_no_whitespace(self):
        """Test words without trailing whitespace."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text="world", whitespace="", start_ts=0.5, end_ts=1.0),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == "Hello"
        assert result[1].text == "world"


class TestPunctuationMergerComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_sentence_with_mixed_punctuation(self):
        """Test a complete sentence with various punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text=",", whitespace=" ", start_ts=0.5, end_ts=0.6),
            TTSToken(text="world", whitespace="", start_ts=0.6, end_ts=1.0),
            TTSToken(text="!", whitespace=" ", start_ts=1.0, end_ts=1.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == "Hello, "
        assert result[0].clean_word == "Hello"
        assert result[1].text == "world! "
        assert result[1].clean_word == "world"
    
    def test_question_with_multiple_words(self):
        """Test a question with multiple words and punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="How", whitespace=" ", start_ts=0.0, end_ts=0.3),
            TTSToken(text="are", whitespace=" ", start_ts=0.3, end_ts=0.6),
            TTSToken(text="you", whitespace="", start_ts=0.6, end_ts=0.9),
            TTSToken(text="?", whitespace=" ", start_ts=0.9, end_ts=1.0),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 3
        assert result[0].text == "How "
        assert result[1].text == "are "
        assert result[2].text == "you? "
        assert result[2].clean_word == "you"
    
    def test_paragraph_with_multiple_sentences(self):
        """Test multiple sentences with various punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="First", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text="sentence", whitespace="", start_ts=0.5, end_ts=1.0),
            TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.1),
            TTSToken(text="Second", whitespace=" ", start_ts=1.1, end_ts=1.6),
            TTSToken(text="one", whitespace="", start_ts=1.6, end_ts=2.0),
            TTSToken(text="!", whitespace=" ", start_ts=2.0, end_ts=2.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 4
        assert result[0].text == "First "
        assert result[1].text == "sentence. "
        assert result[2].text == "Second "
        assert result[3].text == "one! "
    
    def test_word_with_apostrophe(self):
        """Test that words with apostrophes are not treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="don't", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text="worry", whitespace="", start_ts=0.5, end_ts=1.0),
            TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == "don't "
        assert result[0].clean_word == "don't"
        assert result[1].text == "worry. "
    
    def test_hyphenated_word(self):
        """Test that hyphenated words are not treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="well-known", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text="fact", whitespace="", start_ts=0.5, end_ts=1.0),
            TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].text == "well-known "
        assert result[0].clean_word == "well-known"
        assert result[1].text == "fact. "


class TestPunctuationMergerWhitespaceHandling:
    """Test whitespace preservation in merged tokens."""
    
    def test_whitespace_preserved_in_text(self):
        """Test that whitespace is preserved in the text field."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace="  ", start_ts=0.0, end_ts=0.5),
            TTSToken(text=",", whitespace="   ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Hello  ,   "
    
    def test_no_whitespace_in_clean_word(self):
        """Test that clean_word strips whitespace."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="  Hello  ", whitespace=" ", start_ts=0.0, end_ts=0.5),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "  Hello   "
        assert result[0].clean_word == "Hello"
    
    def test_mixed_whitespace_types(self):
        """Test handling of different whitespace types."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Word", whitespace="\t", start_ts=0.0, end_ts=0.5),
            TTSToken(text=".", whitespace="\n", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Word\t.\n"


class TestPunctuationMergerTimingPreservation:
    """Test that timing information is preserved correctly."""
    
    def test_timing_from_first_token(self):
        """Test that merged token uses timing from the word, not punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Hello", whitespace=" ", start_ts=1.5, end_ts=2.0),
            TTSToken(text=",", whitespace=" ", start_ts=2.0, end_ts=2.1),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].start_time == 1.5
        assert result[0].end_time == 2.0
    
    def test_timing_preserved_for_each_word(self):
        """Test that each word retains its original timing."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="First", whitespace=" ", start_ts=0.0, end_ts=0.5),
            TTSToken(text=",", whitespace=" ", start_ts=0.5, end_ts=0.6),
            TTSToken(text="second", whitespace=" ", start_ts=0.6, end_ts=1.2),
            TTSToken(text=".", whitespace=" ", start_ts=1.2, end_ts=1.3),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 2
        assert result[0].start_time == 0.0
        assert result[0].end_time == 0.5
        assert result[1].start_time == 0.6
        assert result[1].end_time == 1.2
    
    def test_timing_with_zero_duration(self):
        """Test handling of tokens with zero duration."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Word", whitespace=" ", start_ts=1.0, end_ts=1.0),
            TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.0),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].start_time == 1.0
        assert result[0].end_time == 1.0


class TestPunctuationMergerSpecialCharacters:
    """Test handling of special characters and edge cases."""
    
    def test_semicolon_as_punctuation(self):
        """Test that semicolons are treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="clause", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text=";", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "clause; "
    
    def test_colon_as_punctuation(self):
        """Test that colons are treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="Note", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text=":", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "Note: "
    
    def test_parentheses_as_punctuation(self):
        """Test that parentheses are treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="word", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text=")", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "word) "
    
    def test_quotes_as_punctuation(self):
        """Test that quotes are treated as punctuation."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="word", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text='"', whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == 'word" '
    
    def test_unicode_punctuation(self):
        """Test handling of Unicode punctuation marks."""
        merger = PunctuationMerger()
        tokens = [
            TTSToken(text="word", whitespace="", start_ts=0.0, end_ts=0.5),
            TTSToken(text="…", whitespace=" ", start_ts=0.5, end_ts=0.6),
        ]
        
        result = merger.merge(tokens)
        
        assert len(result) == 1
        assert result[0].text == "word… "
