"""Concrete implementations of I/O interfaces.

This module provides file-based and in-memory implementations
of the I/O interfaces defined in io.interfaces.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from io_adapters.interfaces import ITextReader, IAudioWriter, IMetadataWriter

if TYPE_CHECKING:
    from typing import List, Optional
    import numpy as np
    from processing.models import SentenceSegment


class FileTextReader(ITextReader):
    """Reads text from a file.
    
    This is the standard implementation for reading input text files.
    """
    
    def __init__(self, path: Path):
        """Initialize with file path.
        
        Args:
            path: Path to the text file to read
        """
        self._path = path
    
    def read(self) -> str:
        """Read text from the file.
        
        Returns:
            The file content as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file cannot be read
        """
        with open(self._path, 'r', encoding='utf-8') as f:
            return f.read()


class StringTextReader(ITextReader):
    """Reads text from a string (for testing).
    
    This implementation is useful for unit tests and programmatic usage
    where text is already in memory.
    """
    
    def __init__(self, text: str):
        """Initialize with text string.
        
        Args:
            text: The text content to provide
        """
        self._text = text
    
    def read(self) -> str:
        """Return the stored text.
        
        Returns:
            The text content
        """
        return self._text


class FileAudioWriter(IAudioWriter):
    """Writes audio to a WAV file.
    
    This is the standard implementation for writing audio output.
    Uses soundfile library to write WAV format.
    """
    
    def __init__(self, path: Path):
        """Initialize with output file path.
        
        Args:
            path: Path where the WAV file will be written
        """
        self._path = path
    
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        """Write audio data to WAV file.
        
        Args:
            audio: Audio samples as a numpy array
            sample_rate: Sample rate in Hz (e.g., 24000)
            
        Raises:
            IOError: If the file cannot be written
        """
        import soundfile as sf
        sf.write(str(self._path), audio, sample_rate)


class InMemoryAudioWriter(IAudioWriter):
    """Stores audio in memory (for testing).
    
    This implementation is useful for unit tests where we want to
    verify audio generation without writing to disk.
    """
    
    def __init__(self):
        """Initialize with empty storage."""
        self.audio: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
    
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        """Store audio data in memory.
        
        Args:
            audio: Audio samples as a numpy array
            sample_rate: Sample rate in Hz (e.g., 24000)
        """
        self.audio = audio
        self.sample_rate = sample_rate


class JsonMetadataWriter(IMetadataWriter):
    """Writes subtitle metadata to JSON file.
    
    This implementation maintains the existing JSON format with
    hierarchical structure: sentences containing word arrays.
    """
    
    def __init__(self, path: Path):
        """Initialize with output file path.
        
        Args:
            path: Path where the JSON file will be written
        """
        self._path = path
    
    def write(self, segments: List[SentenceSegment]) -> None:
        """Write subtitle segments to JSON file.
        
        The output format matches the existing structure:
        [
            {
                "sentence_text": "...",
                "start_time": 0.0,
                "end_time": 1.5,
                "words": [
                    {
                        "text": "word ",
                        "clean_word": "word",
                        "start_time": 0.0,
                        "end_time": 0.5
                    },
                    ...
                ]
            },
            ...
        ]
        
        Args:
            segments: List of sentence segments with word-level timing
            
        Raises:
            IOError: If the file cannot be written
        """
        data = []
        for seg in segments:
            data.append({
                "sentence_text": seg.sentence_text,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "words": [
                    {
                        "text": w.text,
                        "clean_word": w.clean_word,
                        "start_time": w.start_time,
                        "end_time": w.end_time
                    }
                    for w in seg.words
                ]
            })
        
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


class InMemoryMetadataWriter(IMetadataWriter):
    """Stores metadata in memory (for testing).
    
    This implementation is useful for unit tests where we want to
    verify metadata generation without writing to disk.
    """
    
    def __init__(self):
        """Initialize with empty storage."""
        self.segments: List[SentenceSegment] = []
    
    def write(self, segments: List[SentenceSegment]) -> None:
        """Store subtitle segments in memory.
        
        Args:
            segments: List of sentence segments with word-level timing
        """
        self.segments = segments
