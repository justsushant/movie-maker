"""
Core abstractions for TTS engines.

This module defines the interface that all TTS engines must implement,
along with the data structures for TTS results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class TTSToken:
    """
    Raw token from TTS engine with timing information.
    
    Attributes:
        text: The text content of the token
        whitespace: Trailing whitespace after the token
        start_ts: Start timestamp in seconds
        end_ts: End timestamp in seconds
    """
    text: str
    whitespace: str
    start_ts: float
    end_ts: float


@dataclass
class TTSResult:
    """
    Complete TTS generation result.
    
    Attributes:
        audio: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        tokens: List of tokens with timing information
    """
    audio: np.ndarray
    sample_rate: int
    tokens: List[TTSToken]


class ITTSEngine(ABC):
    """
    Interface for text-to-speech engines.
    
    This interface abstracts TTS operations, allowing different TTS
    implementations to be swapped without modifying downstream components.
    """
    
    @abstractmethod
    def generate(self, text: str) -> TTSResult:
        """
        Generate speech audio and word-level timing data from text.
        
        Args:
            text: Input text to synthesize
            
        Returns:
            TTSResult containing audio samples and token timing data
            
        Raises:
            Exception: If TTS generation fails
        """
        pass
