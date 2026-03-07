"""
Sentence grouping component.

This module provides functionality to group words into sentence segments
based on punctuation boundaries and duration constraints.
"""

from __future__ import annotations

import re
from typing import List

from processing.models import WordToken, SentenceSegment


class SentenceGrouper:
    """
    Groups words into sentences based on punctuation and duration.
    
    Organizes a stream of word tokens into sentence segments suitable
    for subtitle display. Sentences are split at punctuation boundaries
    (. ! ?) or when they exceed a maximum duration.
    
    Attributes:
        max_duration: Maximum duration in seconds for a single sentence
                     segment before forcing a split
    """
    
    def __init__(self, max_duration: float = 5.0):
        """
        Initialize the sentence grouper.
        
        Args:
            max_duration: Maximum duration in seconds for a sentence segment.
                         Defaults to 5.0 seconds.
        """
        self._max_duration = max_duration
    
    def group(self, words: List[WordToken]) -> List[SentenceSegment]:
        """
        Group words into sentence segments.
        
        Iterates through words and groups them into sentences based on:
        1. Sentence-ending punctuation (. ! ?)
        2. Maximum duration constraint
        3. End of word list
        
        Args:
            words: List of word tokens to group
            
        Returns:
            List of sentence segments with word-level timing
            
        Note:
            - Empty input returns empty list
            - Sentences are trimmed of leading/trailing whitespace
            - Each segment includes all words that comprise it
        """
        sentences: List[SentenceSegment] = []
        
        if not words:
            return sentences
        
        current_sentence_words: List[WordToken] = []
        start_time = words[0].start_time
        
        for i, word in enumerate(words):
            current_sentence_words.append(word)
            current_end_time = word.end_time
            
            # Check end conditions
            is_sentence_end = bool(re.search(r'[.!?](\s+)?$', word.text))
            is_duration_exceeded = (current_end_time - start_time) >= self._max_duration
            is_last_word = (i == len(words) - 1)
            
            if is_sentence_end or is_duration_exceeded or is_last_word:
                # Compile full sentence text
                full_text = "".join(w.text for w in current_sentence_words).strip()
                
                if full_text:
                    sentences.append(SentenceSegment(
                        sentence_text=full_text,
                        start_time=start_time,
                        end_time=current_end_time,
                        words=current_sentence_words.copy()
                    ))
                
                # Reset for next sentence
                current_sentence_words = []
                if not is_last_word:
                    start_time = words[i + 1].start_time
        
        return sentences
