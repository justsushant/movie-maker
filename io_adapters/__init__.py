"""I/O abstractions for movie-maker.

This module provides interfaces and implementations for input/output operations,
enabling testability and flexibility in how data is read and written.
"""

from __future__ import annotations

from io_adapters.interfaces import (
    ITextReader,
    IAudioWriter,
    IMetadataWriter,
)

from io_adapters.implementations import (
    FileTextReader,
    StringTextReader,
    FileAudioWriter,
    InMemoryAudioWriter,
    JsonMetadataWriter,
    InMemoryMetadataWriter,
)

__all__ = [
    # Interfaces
    "ITextReader",
    "IAudioWriter",
    "IMetadataWriter",
    # Implementations
    "FileTextReader",
    "StringTextReader",
    "FileAudioWriter",
    "InMemoryAudioWriter",
    "JsonMetadataWriter",
    "InMemoryMetadataWriter",
]
