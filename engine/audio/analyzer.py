"""Audio analysis using librosa for Phase 3.

This module provides the AudioAnalyzer class which wraps librosa to extract
temporal and spectral features from audio files:
- Beats: Rhythmic pulses detected using beat tracking
- Onsets: Sharp transients marking sound event starts
- Energy: RMS loudness envelope over time
- Spectral Centroid: Brightness/tone of the audio spectrum
"""

from __future__ import annotations
from pathlib import Path
from typing import Union, Optional
import numpy as np


class AudioAnalyzer:
    """Analyzes audio files using librosa to extract temporal and spectral features.
    
    This class loads an audio file and provides methods to analyze various
    audio characteristics that can drive visual effects in the video engine.
    
    All analysis results are cached to avoid redundant computation.
    
    Attributes:
        y: Audio samples as numpy array
        sr: Sample rate in Hz
        duration: Audio duration in seconds
    
    Raises:
        ImportError: If librosa is not installed
        FileNotFoundError: If audio file does not exist
        ValueError: If audio file format is unsupported or corrupted
    """
    
    def __init__(self, audio_path: Union[str, Path]):
        """Initialize analyzer with audio file.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, OGG, FLAC, etc.)
            
        Raises:
            ImportError: If librosa is not installed
            FileNotFoundError: If audio file does not exist
            ValueError: If audio file format is unsupported
        """
        # Check librosa availability first
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required for audio analysis. "
                "Install with: pip install librosa"
            )
        
        # Validate file exists
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load audio
        try:
            self.y, self.sr = librosa.load(str(audio_path), sr=None)
        except Exception as e:
            raise ValueError(
                f"Failed to load audio file {audio_path}: {e}"
            )
        
        self.duration = len(self.y) / self.sr
        self._librosa = librosa
        
        # Cache for analysis results
        self._beats: Optional[np.ndarray] = None
        self._onsets: Optional[np.ndarray] = None
        self._energy: Optional[tuple[np.ndarray, np.ndarray]] = None
        self._spectral_centroid: Optional[tuple[np.ndarray, np.ndarray]] = None
    
    def analyze_beats(self) -> np.ndarray:
        """Detect beat timestamps using librosa.
        
        Uses librosa's beat tracking algorithm to find rhythmic pulses in the audio.
        Results are cached for subsequent calls.
        
        Returns:
            Array of beat timestamps in seconds, sorted in ascending order
        """
        if self._beats is None:
            tempo, beat_frames = self._librosa.beat.beat_track(y=self.y, sr=self.sr)
            self._beats = self._librosa.frames_to_time(beat_frames, sr=self.sr)
        return self._beats
    
    def analyze_onsets(self) -> np.ndarray:
        """Detect onset timestamps using librosa.
        
        Onsets are sharp transients in the audio marking the start of sound events
        (e.g., percussive hits, word starts). Results are cached.
        
        Returns:
            Array of onset timestamps in seconds, sorted in ascending order
        """
        if self._onsets is None:
            onset_frames = self._librosa.onset.onset_detect(y=self.y, sr=self.sr)
            self._onsets = self._librosa.frames_to_time(onset_frames, sr=self.sr)
        return self._onsets
    
    def analyze_energy(self) -> tuple[np.ndarray, np.ndarray]:
        """Compute RMS energy envelope using librosa.
        
        The energy envelope represents audio loudness over time using
        Root Mean Square (RMS) of the audio signal. Results are cached.
        
        Returns:
            Tuple of (timestamps, energy_values) where:
            - timestamps: Array of time points in seconds
            - energy_values: Array of RMS energy values (typically 0.0-1.0 range)
        """
        if self._energy is None:
            rms = self._librosa.feature.rms(y=self.y)[0]
            times = self._librosa.frames_to_time(
                np.arange(len(rms)), 
                sr=self.sr
            )
            self._energy = (times, rms)
        return self._energy
    
    def analyze_spectral_centroid(self) -> tuple[np.ndarray, np.ndarray]:
        """Compute spectral centroid using librosa.
        
        The spectral centroid represents the "center of mass" of the audio spectrum,
        indicating brightness or tone. Higher values = brighter/higher-pitched sound.
        Results are cached.
        
        Returns:
            Tuple of (timestamps, centroid_values) where:
            - timestamps: Array of time points in seconds
            - centroid_values: Array of spectral centroid values in Hz
        """
        if self._spectral_centroid is None:
            centroid = self._librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
            times = self._librosa.frames_to_time(
                np.arange(len(centroid)), 
                sr=self.sr
            )
            self._spectral_centroid = (times, centroid)
        return self._spectral_centroid
    
    def analyze_all(self) -> dict:
        """Run all analyses and return results.
        
        Convenience method that runs all analysis methods and returns
        a dictionary with all results. Uses caching so repeated calls
        are efficient.
        
        Returns:
            Dictionary with keys:
            - 'beats': Array of beat timestamps
            - 'onsets': Array of onset timestamps
            - 'energy': Tuple of (timestamps, energy_values)
            - 'spectral_centroid': Tuple of (timestamps, centroid_values)
        """
        return {
            'beats': self.analyze_beats(),
            'onsets': self.analyze_onsets(),
            'energy': self.analyze_energy(),
            'spectral_centroid': self.analyze_spectral_centroid()
        }
