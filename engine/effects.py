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
