"""
Text processing components for movie-maker.

This module provides components for processing TTS output:
- Data models for tokens and segments
- Punctuation merging to combine punctuation with adjacent words
- Sentence grouping to organize words into subtitle segments
"""

from __future__ import annotations

from processing.models import WordToken, SentenceSegment
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper

__all__ = [
    "WordToken",
    "SentenceSegment",
    "PunctuationMerger",
    "SentenceGrouper",
]
