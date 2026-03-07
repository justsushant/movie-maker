"""I/O interfaces for KokoroMoviePy.

This module defines abstract interfaces for input/output operations,
following the Dependency Inversion Principle to enable testability
and flexibility in implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    import numpy as np
    from processing.models import SentenceSegment


class ITextReader(ABC):
    """Interface for reading input text.
    
    Implementations can read from files, strings, network sources, etc.
    This abstraction enables testing without filesystem dependencies.
    """
    
    @abstractmethod
    def read(self) -> str:
        """Read and return text content.
        
        Returns:
            The text content as a string
        """
        pass


class IAudioWriter(ABC):
    """Interface for writing audio data.
    
    Implementations can write to files, memory, or other destinations.
    This abstraction enables testing without filesystem dependencies.
    """
    
    @abstractmethod
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        """Write audio data.
        
        Args:
            audio: Audio samples as a numpy array
            sample_rate: Sample rate in Hz (e.g., 24000)
        """
        pass


class IMetadataWriter(ABC):
    """Interface for writing subtitle metadata.
    
    Implementations can write to JSON files, databases, or memory.
    This abstraction enables testing without filesystem dependencies.
    """
    
    @abstractmethod
    def write(self, segments: List[SentenceSegment]) -> None:
        """Write subtitle segments to storage.
        
        Args:
            segments: List of sentence segments with word-level timing
        """
        pass
