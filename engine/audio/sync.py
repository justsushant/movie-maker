"""Audio synchronization for mapping audio features to video timeline.

This module provides the AudioSync class which stores audio analysis results
and provides interpolation methods to query audio features at any video timestamp.
"""

from __future__ import annotations
from typing import Optional
import numpy as np


class AudioSync:
    """Maps audio features to video timeline with interpolation support.
    
    This class stores the results of audio analysis (beats, onsets, energy envelope,
    spectral centroid) and provides methods to query these features at any point
    in the video timeline. Time-series data (energy, spectral centroid) is
    interpolated linearly between analysis frames for smooth transitions.
    
    Attributes:
        beats: Array of beat timestamps in seconds
        onsets: Array of onset timestamps in seconds
        energy_times: Timestamps for energy envelope samples
        energy_values: Energy (RMS) values corresponding to energy_times
        spectral_times: Timestamps for spectral centroid samples
        spectral_values: Spectral centroid values (Hz) corresponding to spectral_times
    """
    
    def __init__(
        self,
        beats: np.ndarray,
        onsets: np.ndarray,
        energy_times: np.ndarray,
        energy_values: np.ndarray,
        spectral_times: np.ndarray,
        spectral_values: np.ndarray
    ):
        """Initialize with audio analysis results.
        
        Args:
            beats: Array of beat timestamps in seconds
            onsets: Array of onset timestamps in seconds
            energy_times: Timestamps for energy envelope (seconds)
            energy_values: Energy values (RMS, typically 0.0-1.0)
            spectral_times: Timestamps for spectral centroid (seconds)
            spectral_values: Spectral centroid values (Hz)
        """
        self.beats = beats
        self.onsets = onsets
        self.energy_times = energy_times
        self.energy_values = energy_values
        self.spectral_times = spectral_times
        self.spectral_values = spectral_values
    
    def get_energy_at_time(self, t: float) -> float:
        """Get interpolated energy at time t.
        
        Uses linear interpolation between energy envelope samples.
        For times before the first sample or after the last sample,
        returns the boundary value (no extrapolation).
        
        Args:
            t: Time in seconds
            
        Returns:
            Interpolated energy value (0.0 if no data available)
        """
        if len(self.energy_times) == 0:
            return 0.0
        
        # Handle edge cases
        if t <= self.energy_times[0]:
            return float(self.energy_values[0])
        if t >= self.energy_times[-1]:
            return float(self.energy_values[-1])
        
        # Linear interpolation
        return float(np.interp(t, self.energy_times, self.energy_values))
    
    def get_spectral_centroid_at_time(self, t: float) -> float:
        """Get interpolated spectral centroid at time t.
        
        Uses linear interpolation between spectral centroid samples.
        For times before the first sample or after the last sample,
        returns the boundary value (no extrapolation).
        
        Args:
            t: Time in seconds
            
        Returns:
            Interpolated spectral centroid in Hz (0.0 if no data available)
        """
        if len(self.spectral_times) == 0:
            return 0.0
        
        # Handle edge cases
        if t <= self.spectral_times[0]:
            return float(self.spectral_values[0])
        if t >= self.spectral_times[-1]:
            return float(self.spectral_values[-1])
        
        # Linear interpolation
        return float(np.interp(t, self.spectral_times, self.spectral_values))
    
    def get_nearest_beat(self, t: float) -> Optional[float]:
        """Get timestamp of nearest beat to time t.
        
        Finds the beat with minimum absolute distance to the given time.
        
        Args:
            t: Time in seconds
            
        Returns:
            Nearest beat timestamp in seconds, or None if no beats detected
        """
        if len(self.beats) == 0:
            return None
        
        idx = np.argmin(np.abs(self.beats - t))
        return float(self.beats[idx])
    
    def is_onset_active(self, t: float, duration: float) -> bool:
        """Check if any onset is within duration of time t.
        
        Determines if there is an onset event in the time window [t, t + duration].
        Useful for triggering flash or pulse effects.
        
        Args:
            t: Time in seconds
            duration: Window duration in seconds
            
        Returns:
            True if at least one onset is in the window, False otherwise
        """
        if len(self.onsets) == 0:
            return False
        
        # Check if any onset is within [t, t + duration]
        return bool(np.any((self.onsets >= t) & (self.onsets <= t + duration)))
    
    def get_closest_onset(self, t: float, max_distance: float) -> Optional[float]:
        """Get closest onset within max_distance of time t.
        
        Finds the onset with minimum distance to t, but only if that
        distance is within max_distance. Useful for finding the specific
        onset that triggered an effect.
        
        Args:
            t: Time in seconds
            max_distance: Maximum distance in seconds
            
        Returns:
            Closest onset timestamp if within range, None otherwise
        """
        if len(self.onsets) == 0:
            return None
        
        distances = np.abs(self.onsets - t)
        min_idx = np.argmin(distances)
        
        if distances[min_idx] <= max_distance:
            return float(self.onsets[min_idx])
        return None
