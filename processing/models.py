"""
Data models for text processing pipeline.

This module defines the data structures used throughout the text processing
pipeline, from raw TTS tokens to final sentence segments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class WordToken:
    """
    Processed word token with merged punctuation.
    
    Represents a single word after punctuation has been merged from
    standalone tokens into adjacent words.
    
    Attributes:
        text: Full text including punctuation and whitespace
        clean_word: The word content without whitespace (may include punctuation)
        start_time: Start timestamp in seconds
        end_time: End timestamp in seconds
    """
    text: str
    clean_word: str
    start_time: float
    end_time: float


@dataclass
class SentenceSegment:
    """
    Sentence segment with word-level timing.
    
    Represents a complete sentence or subtitle segment containing multiple
    words with their individual timing information.
    
    Attributes:
        sentence_text: Complete sentence text
        start_time: Start timestamp of first word in seconds
        end_time: End timestamp of last word in seconds
        words: List of word tokens in this sentence
    """
    sentence_text: str
    start_time: float
    end_time: float
    words: List[WordToken]
