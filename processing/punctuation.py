"""
Punctuation merging component.

This module provides functionality to merge standalone punctuation tokens
into adjacent words, cleaning up the token stream from TTS engines.
"""

from __future__ import annotations

import re
from typing import List, TYPE_CHECKING

from processing.models import WordToken

if TYPE_CHECKING:
    from tts.interfaces import TTSToken


class PunctuationMerger:
    """
    Merges punctuation tokens into adjacent words.
    
    TTS engines often emit punctuation as separate tokens. This class
    merges standalone punctuation into the preceding word to create
    cleaner subtitle segments.
    
    Example:
        Input tokens: ["Hello", ",", "world", "!"]
        Output tokens: ["Hello,", "world!"]
    """
    
    def merge(self, tokens: List[TTSToken]) -> List[WordToken]:
        """
        Merge standalone punctuation into preceding words.
        
        Iterates through TTS tokens and appends punctuation-only tokens
        to the previous word token. If a token contains alphanumeric
        characters, it's treated as a word; otherwise, it's punctuation.
        
        Args:
            tokens: Raw TTS tokens from the TTS engine
            
        Returns:
            List of word tokens with punctuation merged
            
        Note:
            - Punctuation at the start (no preceding word) is kept as-is
            - Empty tokens are skipped
            - Whitespace is preserved in the text field
        """
        merged_words: List[WordToken] = []
        
        for token in tokens:
            text_content = token.text.strip()
            
            # Check if this token is purely punctuation (no alphanumeric chars)
            is_punctuation = not bool(re.search(r'[a-zA-Z0-9]', text_content))
            
            if is_punctuation and merged_words:
                # Append punctuation to the previous word
                merged_words[-1].text += token.text + token.whitespace
            else:
                # This is a valid word or the first token
                merged_words.append(WordToken(
                    text=token.text + token.whitespace,
                    clean_word=text_content,
                    start_time=token.start_ts,
                    end_time=token.end_ts
                ))
        
        return merged_words
