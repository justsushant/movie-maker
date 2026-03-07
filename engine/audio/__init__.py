"""Audio analysis and synchronization module for Phase 3.

This module provides audio analysis capabilities using librosa to extract
beats, onsets, energy envelopes, and spectral features from audio files.
These features drive audio-reactive visual effects in the video engine.

Key components:
- AudioAnalyzer: Analyzes audio files using librosa
- AudioSync: Maps audio features to video timeline with interpolation
"""

from __future__ import annotations

__all__ = ["AudioAnalyzer", "AudioSync"]

# Lazy imports to avoid requiring librosa when not using audio features
def __getattr__(name: str):
    if name == "AudioAnalyzer":
        from engine.audio.analyzer import AudioAnalyzer
        return AudioAnalyzer
    elif name == "AudioSync":
        from engine.audio.sync import AudioSync
        return AudioSync
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
