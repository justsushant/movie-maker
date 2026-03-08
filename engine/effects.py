"""Effect function implementations for Phase 2.

This module provides effect functions that transform individual frames.
All effects follow the EffectFunction protocol: (frame, t, progress) -> frame.

Effect Categories:
- Color: Brightness, contrast, saturation, vignette
- Texture: Film grain
- Animated: Fade in/out, pulse

Effects are composable and can be chained together using chain_effects().
"""

from __future__ import annotations
import numpy as np
import cv2
from typing import Callable


# ============================================================================
# Color Effects
# ============================================================================

def brightness(amount: float) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a brightness adjustment effect.
    
    Args:
        amount: Brightness adjustment (-1.0 to 1.0)
                Positive values increase brightness
                Negative values decrease brightness
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to float for arithmetic
        adjusted = frame.astype(np.float32) + (amount * 255)
        # Clamp to valid range
        adjusted = np.clip(adjusted, 0, 255)
        return adjusted.astype(np.uint8)
    
    return effect


def contrast(amount: float) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a contrast adjustment effect.
    
    Args:
        amount: Contrast multiplier (0.0 to 2.0)
                1.0 = no change
                >1.0 = increase contrast
                <1.0 = decrease contrast
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to float and center around 128
        adjusted = (frame.astype(np.float32) - 128) * amount + 128
        # Clamp to valid range
        adjusted = np.clip(adjusted, 0, 255)
        return adjusted.astype(np.uint8)
    
    return effect


def saturation(amount: float) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a saturation adjustment effect.
    
    Args:
        amount: Saturation multiplier (0.0 to 2.0)
                1.0 = no change
                >1.0 = increase saturation
                <1.0 = decrease saturation
                0.0 = grayscale
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert RGB to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Adjust saturation channel
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * amount, 0, 255)
        
        # Convert back to RGB
        hsv = hsv.astype(np.uint8)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return rgb
    
    return effect


def vignette(
    intensity: float = 0.5,
    radius: float = 0.8
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a vignette effect that darkens frame edges.
    
    Args:
        intensity: Darkness of vignette (0.0 to 1.0)
        radius: Size of bright center (0.0 to 1.0)
                Larger values = larger bright area
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        center_y, center_x = h // 2, w // 2
        
        # Create radial gradient
        y, x = np.ogrid[:h, :w]
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        # Normalize distances
        normalized = distances / max_distance
        
        # Apply vignette curve
        mask = np.clip((normalized - radius) / (1 - radius), 0, 1)
        mask = 1 - (mask * intensity)
        mask = mask[:, :, np.newaxis]  # Add channel dimension
        
        # Apply mask
        result = (frame * mask).astype(np.uint8)
        return result
    
    return effect


# ============================================================================
# Texture Effects
# ============================================================================

def film_grain(
    intensity: float = 0.1,
    seed: int = None
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a film grain effect.
    
    Args:
        intensity: Grain intensity (0.0 to 1.0)
        seed: Random seed for reproducibility (None = time-based)
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Use time-based seed for different grain per frame
        if seed is None:
            np.random.seed(int(t * 1000) % (2**32))
        else:
            np.random.seed(seed + int(t * 1000))
        
        # Generate grain
        h, w = frame.shape[:2]
        grain = np.random.normal(0, intensity * 255, (h, w, 3))
        
        # Add grain to frame
        result = frame.astype(np.float32) + grain
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    
    return effect


# ============================================================================
# Animated Effects
# ============================================================================

def fade_in(duration: float) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a fade-in effect from black.
    
    Args:
        duration: Fade duration in seconds
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Use clip progress for fade
        fade_progress = min(progress * (1.0 / duration) if duration > 0 else 1.0, 1.0)
        result = (frame * fade_progress).astype(np.uint8)
        return result
    
    return effect


def fade_out(duration: float) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a fade-out effect to black.
    
    Args:
        duration: Fade duration in seconds
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Fade out in the last 'duration' seconds
        fade_progress = max(0.0, 1.0 - (progress - (1.0 - duration)) / duration)
        result = (frame * fade_progress).astype(np.uint8)
        return result
    
    return effect


def pulse(
    frequency: float = 1.0,
    amount: float = 0.2
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a pulsing brightness effect.
    
    Args:
        frequency: Pulses per second
        amount: Pulse intensity (0.0 to 1.0)
                
    Returns:
        Effect function
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Sine wave based on absolute time
        pulse_value = np.sin(t * frequency * 2 * np.pi) * amount
        multiplier = 1.0 + pulse_value
        
        result = (frame.astype(np.float32) * multiplier)
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    
    return effect


# ============================================================================
# Effect Utilities
# ============================================================================

def chain_effects(*effects: Callable) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Chain multiple effects together.
    
    Args:
        *effects: Effect functions to chain
        
    Returns:
        Combined effect function
    """
    def combined_effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame
        for effect in effects:
            result = effect(result, t, progress)
        return result
    
    return combined_effect


# ============================================================================
# Phase 3: Audio-Reactive Effects
# ============================================================================

class OnsetFlash:
    """
    Flash effect triggered by audio onsets.
    
    Brightens the frame when an onset (sharp transient) is detected in the audio.
    The brightness decays over time using an easing function.
    
    Args:
        audio_sync: AudioSync object with onset data (None for graceful degradation)
        flash_duration: Duration of flash effect in seconds
        intensity: Flash intensity (0.0 to 1.0, where 1.0 doubles brightness)
        easing: Easing function for flash decay (defaults to ease_out_cubic)
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        flash_duration: float = 0.2,
        intensity: float = 0.5,
        easing = None
    ):
        self.audio_sync = audio_sync
        self.flash_duration = flash_duration
        self.intensity = intensity
        
        if easing is None:
            from engine.easing import ease_out_cubic
            self.easing = ease_out_cubic
        else:
            self.easing = easing
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """
        Apply onset flash effect to frame.
        
        Args:
            frame: Input frame (HxWx3 uint8)
            t: Absolute time in seconds
            progress: Clip progress in [0.0, 1.0] (unused)
            
        Returns:
            Processed frame with flash effect applied
        """
        # Graceful degradation if no audio
        if self.audio_sync is None:
            return frame
        
        # Find all onsets that could affect current time
        # An onset affects time t if: onset_time <= t < onset_time + flash_duration
        max_brightness = 1.0
        
        for onset_time in self.audio_sync.onsets:
            delta = t - onset_time
            
            # Check if this onset is active (within flash duration after onset)
            if 0 <= delta < self.flash_duration:
                # Compute flash progress (0.0 at onset, 1.0 at end of duration)
                flash_progress = delta / self.flash_duration
                
                # Apply easing to create smooth decay
                eased_progress = self.easing(flash_progress)
                
                # Compute brightness multiplier for this onset
                # At onset (progress=0, eased=0): multiplier = 1.0 + intensity
                # At end (progress=1, eased=1): multiplier = 1.0
                brightness_multiplier = 1.0 + self.intensity * (1.0 - eased_progress)
                
                # Use maximum brightness from all active onsets
                max_brightness = max(max_brightness, brightness_multiplier)
        
        # If no onset is active, return unchanged
        if max_brightness == 1.0:
            return frame
        
        # Apply brightness multiplier
        result = frame.astype(np.float32) * max_brightness
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)



class OnsetZoomPulse:
    """
    Zoom pulse effect triggered by audio onsets.
    
    Scales the frame when an onset is detected, creating a pulsing zoom effect.
    The zoom decays over time using an easing function.
    
    Args:
        audio_sync: AudioSync object with onset data (None for graceful degradation)
        pulse_duration: Duration of pulse effect in seconds
        zoom_magnitude: Maximum zoom scale (e.g., 1.1 = 10% zoom)
        easing: Easing function for pulse decay (defaults to ease_out_cubic)
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        pulse_duration: float = 0.3,
        zoom_magnitude: float = 1.1,
        easing = None
    ):
        self.audio_sync = audio_sync
        self.pulse_duration = pulse_duration
        self.zoom_magnitude = zoom_magnitude
        
        if easing is None:
            from engine.easing import ease_out_cubic
            self.easing = ease_out_cubic
        else:
            self.easing = easing
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Apply onset zoom pulse effect to frame."""
        # Graceful degradation if no audio
        if self.audio_sync is None:
            return frame
        
        # Find maximum zoom from all active onsets
        max_zoom = 1.0
        
        for onset_time in self.audio_sync.onsets:
            delta = t - onset_time
            
            # Check if this onset is active
            if 0 <= delta < self.pulse_duration:
                # Compute pulse progress
                pulse_progress = delta / self.pulse_duration
                
                # Apply easing
                eased_progress = self.easing(pulse_progress)
                
                # Compute zoom scale (starts at zoom_magnitude, decays to 1.0)
                zoom_scale = 1.0 + (self.zoom_magnitude - 1.0) * (1.0 - eased_progress)
                
                # Use maximum zoom from all active onsets
                max_zoom = max(max_zoom, zoom_scale)
        
        # If no onset is active, return unchanged
        if max_zoom == 1.0:
            return frame
        
        # Apply zoom by scaling and cropping
        h, w = frame.shape[:2]
        
        # Compute new dimensions
        new_h = int(h * max_zoom)
        new_w = int(w * max_zoom)
        
        # Scale up
        scaled = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Crop to original dimensions (center crop)
        start_y = (new_h - h) // 2
        start_x = (new_w - w) // 2
        cropped = scaled[start_y:start_y + h, start_x:start_x + w]
        
        return cropped


class EnergyZoom:
    """
    Zoom effect driven by audio energy.
    
    Scales the frame based on the audio energy level, creating a dynamic zoom
    that responds to loudness.
    
    Args:
        audio_sync: AudioSync object with energy data (None for graceful degradation)
        zoom_range: Tuple of (min_zoom, max_zoom) scales
        energy_range: Tuple of (min_energy, max_energy) for mapping
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        zoom_range: tuple[float, float] = (1.0, 1.2),
        energy_range: tuple[float, float] = (0.0, 1.0)
    ):
        self.audio_sync = audio_sync
        self.zoom_range = zoom_range
        self.energy_range = energy_range
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Apply energy-driven zoom effect to frame."""
        # Graceful degradation if no audio or empty energy data
        if self.audio_sync is None or len(self.audio_sync.energy_times) == 0:
            return frame
        
        # Query energy at current time
        energy = self.audio_sync.get_energy_at_time(t)
        
        # Map energy to zoom range
        energy_min, energy_max = self.energy_range
        zoom_min, zoom_max = self.zoom_range
        
        # Normalize energy to [0, 1]
        if energy_max > energy_min:
            normalized_energy = (energy - energy_min) / (energy_max - energy_min)
            normalized_energy = np.clip(normalized_energy, 0.0, 1.0)
        else:
            normalized_energy = 0.0
        
        # Map to zoom range
        zoom_scale = zoom_min + normalized_energy * (zoom_max - zoom_min)
        zoom_scale = np.clip(zoom_scale, zoom_min, zoom_max)
        
        # If zoom is 1.0, return unchanged
        if abs(zoom_scale - 1.0) < 0.001:
            return frame
        
        # Apply zoom
        h, w = frame.shape[:2]
        new_h = int(h * zoom_scale)
        new_w = int(w * zoom_scale)
        
        scaled = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Crop to original dimensions
        start_y = (new_h - h) // 2
        start_x = (new_w - w) // 2
        cropped = scaled[start_y:start_y + h, start_x:start_x + w]
        
        return cropped


class EnergyBrightness:
    """
    Brightness effect driven by audio energy.
    
    Adjusts frame brightness based on audio energy level.
    
    Args:
        audio_sync: AudioSync object with energy data (None for graceful degradation)
        brightness_range: Tuple of (min_brightness, max_brightness) multipliers
        energy_range: Tuple of (min_energy, max_energy) for mapping
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        brightness_range: tuple[float, float] = (0.8, 1.2),
        energy_range: tuple[float, float] = (0.0, 1.0)
    ):
        self.audio_sync = audio_sync
        self.brightness_range = brightness_range
        self.energy_range = energy_range
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Apply energy-driven brightness effect to frame."""
        # Graceful degradation if no audio or empty energy data
        if self.audio_sync is None or len(self.audio_sync.energy_times) == 0:
            return frame
        
        # Query energy at current time
        energy = self.audio_sync.get_energy_at_time(t)
        
        # Map energy to brightness range
        energy_min, energy_max = self.energy_range
        bright_min, bright_max = self.brightness_range
        
        # Normalize energy to [0, 1]
        if energy_max > energy_min:
            normalized_energy = (energy - energy_min) / (energy_max - energy_min)
            normalized_energy = np.clip(normalized_energy, 0.0, 1.0)
        else:
            normalized_energy = 0.0
        
        # Map to brightness range
        brightness_multiplier = bright_min + normalized_energy * (bright_max - bright_min)
        brightness_multiplier = np.clip(brightness_multiplier, bright_min, bright_max)
        
        # Apply brightness
        result = frame.astype(np.float32) * brightness_multiplier
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)


class EnergyShake:
    """
    Camera shake effect driven by audio energy.
    
    Translates the frame based on audio energy level, creating a shaking effect.
    
    Args:
        audio_sync: AudioSync object with energy data (None for graceful degradation)
        shake_range: Tuple of (min_shake, max_shake) in pixels
        energy_range: Tuple of (min_energy, max_energy) for mapping
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        shake_range: tuple[float, float] = (0.0, 10.0),
        energy_range: tuple[float, float] = (0.0, 1.0)
    ):
        self.audio_sync = audio_sync
        self.shake_range = shake_range
        self.energy_range = energy_range
        self._rng = np.random.RandomState(42)  # Deterministic for testing
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Apply energy-driven shake effect to frame."""
        # Graceful degradation if no audio or empty energy data
        if self.audio_sync is None or len(self.audio_sync.energy_times) == 0:
            return frame
        
        # Query energy at current time
        energy = self.audio_sync.get_energy_at_time(t)
        
        # Map energy to shake magnitude
        energy_min, energy_max = self.energy_range
        shake_min, shake_max = self.shake_range
        
        # Normalize energy to [0, 1]
        if energy_max > energy_min:
            normalized_energy = (energy - energy_min) / (energy_max - energy_min)
            normalized_energy = np.clip(normalized_energy, 0.0, 1.0)
        else:
            normalized_energy = 0.0
        
        # Map to shake range
        shake_magnitude = shake_min + normalized_energy * (shake_max - shake_min)
        
        # If shake is near zero, return unchanged
        if shake_magnitude < 0.1:
            return frame
        
        # Generate random shake offset
        offset_x = self._rng.uniform(-shake_magnitude, shake_magnitude)
        offset_y = self._rng.uniform(-shake_magnitude, shake_magnitude)
        
        # Create translation matrix
        h, w = frame.shape[:2]
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        
        # Apply translation
        shaken = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        return shaken


class SpectralColorShift:
    """
    Color temperature shift effect driven by spectral centroid.
    
    Adjusts color temperature based on the spectral centroid (brightness of sound).
    Higher centroid = warmer colors, lower centroid = cooler colors.
    
    Args:
        audio_sync: AudioSync object with spectral data (None for graceful degradation)
        temperature_range: Tuple of (cool_shift, warm_shift) in range [-1, 1]
        centroid_range: Tuple of (min_centroid, max_centroid) in Hz for mapping
    """
    
    def __init__(
        self,
        audio_sync,  # Optional[AudioSync]
        temperature_range: tuple[float, float] = (-0.2, 0.2),
        centroid_range: tuple[float, float] = (1000.0, 3000.0)
    ):
        self.audio_sync = audio_sync
        self.temperature_range = temperature_range
        self.centroid_range = centroid_range
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Make the effect callable like Phase 2 effects."""
        return self.apply(frame, t, progress)
    
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """Apply spectral-driven color shift effect to frame."""
        # Graceful degradation if no audio or empty spectral data
        if self.audio_sync is None or len(self.audio_sync.spectral_times) == 0:
            return frame
        
        # Query spectral centroid at current time
        centroid = self.audio_sync.get_spectral_centroid_at_time(t)
        
        # Map centroid to temperature shift
        centroid_min, centroid_max = self.centroid_range
        temp_min, temp_max = self.temperature_range
        
        # Normalize centroid to [0, 1]
        if centroid_max > centroid_min:
            normalized_centroid = (centroid - centroid_min) / (centroid_max - centroid_min)
            normalized_centroid = np.clip(normalized_centroid, 0.0, 1.0)
        else:
            normalized_centroid = 0.5
        
        # Map to temperature range
        temperature_shift = temp_min + normalized_centroid * (temp_max - temp_min)
        
        # If shift is near zero, return unchanged
        if abs(temperature_shift) < 0.01:
            return frame
        
        # Apply temperature shift by adjusting red and blue channels
        result = frame.astype(np.float32)
        
        if temperature_shift > 0:
            # Warm shift: increase red, decrease blue
            result[:, :, 0] *= (1.0 + temperature_shift)  # Red
            result[:, :, 2] *= (1.0 - temperature_shift * 0.5)  # Blue
        else:
            # Cool shift: decrease red, increase blue
            result[:, :, 0] *= (1.0 + temperature_shift)  # Red
            result[:, :, 2] *= (1.0 - temperature_shift)  # Blue
        
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)
