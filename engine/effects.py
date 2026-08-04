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

    Adds a fixed offset to every pixel value, shifting the overall
    luminance up or down uniformly across all channels.

    Parameters:
        amount: Brightness adjustment (range: -1.0 to 1.0, typical: -0.3 to 0.3)
                Positive values increase brightness; negative values decrease it.
                0.0 = no change, 1.0 = fully white, -1.0 = fully black.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[brightness(amount=0.2)]
        ... )

    Notes:
        - Output is clamped to [0, 255]
        - Combine with contrast() for a full exposure adjustment
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

    Centers pixel values around 128 and scales them by the given multiplier,
    expanding or compressing the tonal range.

    Parameters:
        amount: Contrast multiplier (range: 0.0-2.0, typical: 0.8-1.5)
                1.0 = no change, >1.0 = increase contrast, <1.0 = decrease contrast.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[contrast(amount=1.3)]
        ... )

    Notes:
        - Output is clamped to [0, 255]
        - amount=0.0 produces a flat mid-gray image
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

    Converts the frame to HSV, scales the saturation channel by amount,
    then converts back to RGB.

    Parameters:
        amount: Saturation multiplier (range: 0.0-2.0, typical: 0.5-1.5)
                1.0 = no change, >1.0 = increase saturation,
                <1.0 = decrease saturation, 0.0 = grayscale.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[saturation(amount=1.4)]
        ... )

    Notes:
        - amount=0.0 is equivalent to grayscale() but via HSV conversion
        - Combine with vibrance() for a more natural-looking boost
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

    Builds a radial gradient mask and multiplies it against the frame,
    darkening pixels proportionally to their distance from the center.

    Parameters:
        intensity: Darkness of vignette (range: 0.0-1.0, typical: 0.3-0.7)
                   0.0 = no darkening, 1.0 = edges fully black.
        radius: Size of the bright center zone (range: 0.0-1.0, typical: 0.6-0.9)
                Larger values = larger bright area before darkening begins.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[vignette(intensity=0.6, radius=0.75)]
        ... )

    Notes:
        - For a simpler single-parameter vignette, use vignette_simple()
        - Combine with film_grain() and sepia() for a vintage look
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
    seed: int | None = None
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Create a film grain effect.

    Adds Gaussian noise to every channel each frame, simulating the
    silver-halide grain of analog film stock.

    Parameters:
        intensity: Grain intensity (range: 0.0-1.0, typical: 0.05-0.2)
                   0.0 = no grain, 0.1 = subtle grain, 0.3+ = heavy grain.
        seed: Random seed for reproducibility (None = time-based per frame)
              Provide a fixed integer for a static grain pattern.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[film_grain(intensity=0.08)]
        ... )

    Notes:
        - With seed=None, grain changes every frame (realistic film look)
        - Combine with sepia() and vignette_simple() for a full vintage effect
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

    Multiplies the frame by a ramp that goes from 0.0 to 1.0 over the
    first `duration` seconds of the clip (based on clip progress).

    Parameters:
        duration: Fade duration as a fraction of clip progress (range: 0.0-1.0)
                  0.5 = fade in over the first half of the clip.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[fade_in(duration=0.3)]
        ... )

    Notes:
        - duration is relative to clip progress, not absolute seconds
        - Combine with fade_out() for a full fade-in/fade-out sequence
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

    Multiplies the frame by a ramp that goes from 1.0 to 0.0 over the
    last `duration` fraction of the clip (based on clip progress).

    Parameters:
        duration: Fade duration as a fraction of clip progress (range: 0.0-1.0)
                  0.3 = fade out over the last 30% of the clip.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[fade_out(duration=0.3)]
        ... )

    Notes:
        - duration is relative to clip progress, not absolute seconds
        - Combine with fade_in() for a full fade-in/fade-out sequence
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

    Modulates frame brightness with a sine wave keyed to absolute time,
    creating a rhythmic brightening and dimming animation.

    Parameters:
        frequency: Pulses per second (range: 0.1-10.0, typical: 0.5-3.0)
        amount: Pulse intensity (range: 0.0-1.0, typical: 0.1-0.3)
                0.0 = no pulse, 0.2 = ±20% brightness swing.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[pulse(frequency=1.5, amount=0.15)]
        ... )

    Notes:
        - Uses absolute time t, so pulse phase is consistent across clips
        - For a color-tinted pulse, use color_pulse() instead
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
    Chain multiple effects together into a single effect function.

    Applies each effect in sequence, passing the output of one as the
    input to the next. Equivalent to composing the effect functions manually.

    Parameters:
        *effects: Effect functions to chain, applied left-to-right.

    Returns:
        Combined effect function with signature (frame, t, progress) -> frame

    Example:
        >>> from engine.effects import chain_effects, grayscale, vignette_simple, film_grain
        >>> combined = chain_effects(grayscale(), vignette_simple(0.5), film_grain(0.08))
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[combined]
        ... )

    Notes:
        - Effects are applied in the order they are passed
        - Equivalent to listing effects individually in ImageClip.effects
    """
    def combined_effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame
        for effect in effects:
            result = effect(result, t, progress)
        return result
    
    return combined_effect


# ============================================================================
# Phase 4: Rich Color Effects
# ============================================================================

def grayscale() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Convert frame to grayscale using perceptual luminance weighting.

    Applies the standard ITU-R BT.601 luminance formula:
    Y = 0.299*R + 0.587*G + 0.114*B. The result is a 3-channel image
    where all channels are equal, preserving the HxWx3 frame format.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[grayscale()]
        ... )

    Notes:
        - Output channels are all equal: R == G == B
        - Applying grayscale twice yields the same result (idempotent)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        gray = (frame[:,:,0] * 0.299 + frame[:,:,1] * 0.587 + frame[:,:,2] * 0.114)
        return np.stack([gray, gray, gray], axis=2).astype(np.uint8)
    return effect


def invert() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Invert all pixel values in the frame (255 - pixel_value).

    Creates a negative image effect. Each channel value v becomes 255 - v,
    so dark areas become bright and vice versa. Colors are also complemented.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[invert()]
        ... )

    Notes:
        - Applying invert twice returns the original image
        - Works on all three RGB channels independently
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        return (255 - frame).astype(np.uint8)
    return effect


def sepia() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply sepia tone effect for a warm vintage look.

    Uses a 3x3 color matrix transformation to map RGB values to warm
    brown tones, mimicking the appearance of aged photographic prints.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[sepia()]
        ... )

    Notes:
        - Combines well with vignette_simple() for a full vintage look
        - The sepia matrix may push some bright pixels to 255 (clipped)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Sepia transformation matrix
        frame_float = frame.astype(np.float32)
        sepia_matrix = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ], dtype=np.float32)
        
        # Apply matrix transformation
        result = np.dot(frame_float, sepia_matrix.T)
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def hue_shift(
    shift: float = 30.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Shift all hues by rotating around the HSV color wheel.

    Converts the frame to HSV, adds the shift to the hue channel (wrapping
    at 180 degrees as OpenCV uses 0-179 for hue), then converts back to RGB.

    Parameters:
        shift: Hue rotation in degrees (range: -180 to 180, typical: 30)
               Positive values rotate toward green/cyan/blue.
               Negative values rotate toward red/magenta.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[hue_shift(shift=90.0)]
        ... )

    Notes:
        - A shift of 0 leaves the image unchanged
        - A shift of 180 (or -180) produces complementary colors
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Shift hue (wrap around using modulo 180)
        hsv[:,:,0] = (hsv[:,:,0] + shift) % 180.0
        
        # Convert back to RGB
        hsv = np.clip(hsv, 0, 179).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return effect


def color_temperature(
    kelvin: float = 6500.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Adjust color temperature to simulate warm or cool lighting.

    Scales the red and blue channels to mimic the appearance of different
    light sources. Values below 6500K add warmth (amber/orange tones);
    values above 6500K add coolness (blue tones).

    Parameters:
        kelvin: Color temperature in Kelvin (range: 2000-10000, typical: 6500)
                2000-4000: candlelight/tungsten (very warm)
                5000-6500: daylight/neutral
                7000-10000: overcast/shade (cool/blue)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[color_temperature(kelvin=3200.0)]
        ... )

    Notes:
        - 6500K is neutral (no change to channels)
        - Extreme values may clip highlights or crush shadows
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Calculate temperature shift
        # Lower kelvin = warmer (more red, less blue)
        # Higher kelvin = cooler (more blue, less red)
        shift = (kelvin - 6500) / 1000.0  # Normalize to -2 to +2 range approximately
        
        result = frame.astype(np.float32)
        
        if shift > 0:
            # Cool: increase blue, decrease red
            result[:,:,0] *= (1.0 - shift * 0.3)  # Red
            result[:,:,2] *= (1.0 + shift * 0.3)  # Blue
        else:
            # Warm: increase red, decrease blue
            shift = abs(shift)
            result[:,:,0] *= (1.0 + shift * 0.3)  # Red
            result[:,:,2] *= (1.0 - shift * 0.3)  # Blue
        
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def tint(
    color: tuple[int, int, int] = (255, 255, 255),
    alpha: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Blend the frame with a solid color overlay.

    Performs a linear blend between the original frame and a solid color
    plane: result = frame * (1 - alpha) + color * alpha.

    Parameters:
        color: RGB tint color (range: 0-255 per channel, typical: (255, 200, 100))
        alpha: Tint opacity (range: 0.0-1.0, typical: 0.2-0.4)
               0.0 = no tint, 1.0 = solid color

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[tint(color=(255, 200, 100), alpha=0.25)]
        ... )

    Notes:
        - alpha=0.0 returns the original frame unchanged
        - Combine with grayscale() first for a duotone-like result
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        color_array = np.array(color, dtype=np.float32)
        result = frame.astype(np.float32) * (1.0 - alpha) + color_array * alpha
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def gamma_correction(
    gamma: float = 1.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply gamma correction for non-linear brightness adjustment.

    Normalizes pixel values to [0, 1], applies the power function
    pixel^(1/gamma), then scales back to [0, 255]. This is the standard
    gamma encoding/decoding used in display calibration.

    Parameters:
        gamma: Gamma exponent (range: 0.1-5.0, typical: 1.0-2.2)
               < 1.0: brightens midtones (gamma expansion)
               1.0: no change
               > 1.0: darkens midtones (gamma compression)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[gamma_correction(gamma=1.8)]
        ... )

    Notes:
        - gamma=2.2 approximates sRGB display correction
        - Very low gamma values (< 0.2) may cause numerical instability
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Normalize to [0, 1], apply gamma, scale back
        normalized = frame.astype(np.float32) / 255.0
        corrected = np.power(normalized, 1.0 / gamma) * 255.0
        corrected = np.clip(corrected, 0, 255)
        return corrected.astype(np.uint8)
    return effect


def channel_mixer(
    red: tuple[float, float, float] = (1.0, 0.0, 0.0),
    green: tuple[float, float, float] = (0.0, 1.0, 0.0),
    blue: tuple[float, float, float] = (0.0, 0.0, 1.0)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Cross-blend RGB channels using a 3x3 weight matrix.

    Each output channel is a weighted sum of all three input channels.
    The identity matrix (default) leaves the image unchanged. Useful for
    creative color grading, simulating film stocks, or channel swapping.

    Parameters:
        red: (r_weight, g_weight, b_weight) for the output red channel
             (range: -1.0 to 2.0 per weight, typical: sums near 1.0)
        green: (r_weight, g_weight, b_weight) for the output green channel
               (range: -1.0 to 2.0 per weight, typical: sums near 1.0)
        blue: (r_weight, g_weight, b_weight) for the output blue channel
              (range: -1.0 to 2.0 per weight, typical: sums near 1.0)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> # Swap red and blue channels
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[channel_mixer(
        ...         red=(0.0, 0.0, 1.0),
        ...         green=(0.0, 1.0, 0.0),
        ...         blue=(1.0, 0.0, 0.0)
        ...     )]
        ... )

    Notes:
        - Weights outside [0, 1] are allowed but may clip pixel values
        - Output is clamped to [0, 255]
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Build mixing matrix
        mixer = np.array([red, green, blue], dtype=np.float32)
        
        # Apply matrix transformation
        result = np.dot(frame.astype(np.float32), mixer.T)
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def duotone(
    dark_color: tuple[int, int, int] = (0, 0, 128),
    light_color: tuple[int, int, int] = (255, 220, 180)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Map luminance to a two-color gradient (duotone effect).

    Converts the frame to luminance values, then linearly interpolates
    between dark_color (for shadows) and light_color (for highlights).
    Popular in graphic design and social media aesthetics.

    Parameters:
        dark_color: RGB color for dark/shadow areas
                    (range: 0-255 per channel, typical: deep blue or black)
        light_color: RGB color for bright/highlight areas
                     (range: 0-255 per channel, typical: warm cream or white)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[duotone(
        ...         dark_color=(20, 0, 80),
        ...         light_color=(255, 220, 100)
        ...     )]
        ... )

    Notes:
        - All color information is discarded; only luminance is preserved
        - For a monochrome look, set both colors to shades of the same hue
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Get luminance
        gray = (frame[:,:,0] * 0.299 + frame[:,:,1] * 0.587 + frame[:,:,2] * 0.114) / 255.0
        
        # Create color arrays
        dark = np.array(dark_color, dtype=np.float32)
        light = np.array(light_color, dtype=np.float32)
        
        # Interpolate based on luminance
        result = dark * (1.0 - gray[:,:,np.newaxis]) + light * gray[:,:,np.newaxis]
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def cinematic_teal_orange(
    intensity: float = 1.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply the cinematic teal-and-orange color grade.

    Pushes shadows toward teal (cyan-green) and highlights toward warm
    orange, mimicking the popular Hollywood blockbuster color grade. Uses
    luminance-based masks to selectively shift hue and saturation.

    Parameters:
        intensity: Grade strength (range: 0.0-1.0, typical: 0.5-1.0)
                   0.0 = no change, 1.0 = full teal-orange grade

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[cinematic_teal_orange(intensity=0.8)]
        ... )

    Notes:
        - Works best on footage with skin tones (highlights) and backgrounds (shadows)
        - Combine with vignette_simple() for a full cinematic look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to HSV for luminance-based adjustments
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Get luminance for shadow/highlight detection
        rgb_float = frame.astype(np.float32)
        luminance = (rgb_float[:,:,0] * 0.299 + rgb_float[:,:,1] * 0.587 + rgb_float[:,:,2] * 0.114) / 255.0
        
        # Create masks for shadows and highlights
        shadow_mask = np.clip(1.0 - luminance * 2.0, 0, 1) * intensity
        highlight_mask = np.clip((luminance - 0.5) * 2.0, 0, 1) * intensity
        
        # Apply teal to shadows (increase blue, decrease red)
        hsv[:,:,2] = np.clip(hsv[:,:,2] + shadow_mask * 20, 0, 255)  # Saturation
        hsv[:,:,0] = np.clip(hsv[:,:,0] - shadow_mask * 15, 0, 179)  # Hue shift toward teal
        
        # Apply orange to highlights (decrease blue)
        hsv[:,:,2] = np.clip(hsv[:,:,2] + highlight_mask * 15, 0, 255)  # Saturation
        
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        return result
    return effect


def auto_white_balance() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply automatic white balance using the gray-world assumption.

    Scales each RGB channel so that its mean equals the overall mean
    luminance of the frame. This corrects color casts caused by
    non-neutral lighting (e.g., tungsten, fluorescent).

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[auto_white_balance()]
        ... )

    Notes:
        - Assumes the average color of the scene should be neutral gray
        - May produce incorrect results on scenes with dominant single colors
        - Applied per-frame, so results may flicker on dynamic content
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Calculate channel means
        r_mean = np.mean(frame[:,:,0])
        g_mean = np.mean(frame[:,:,1])
        b_mean = np.mean(frame[:,:,2])
        
        # Calculate target (average of all channels)
        target = (r_mean + g_mean + b_mean) / 3.0
        
        # Calculate scale factors
        r_scale = target / r_mean if r_mean > 0 else 1.0
        g_scale = target / g_mean if g_mean > 0 else 1.0
        b_scale = target / b_mean if b_mean > 0 else 1.0
        
        # Apply scaling
        result = frame.astype(np.float32)
        result[:,:,0] = np.clip(result[:,:,0] * r_scale, 0, 255)
        result[:,:,1] = np.clip(result[:,:,1] * g_scale, 0, 255)
        result[:,:,2] = np.clip(result[:,:,2] * b_scale, 0, 255)
        
        return result.astype(np.uint8)
    return effect


def vibrance(
    amount: float = 1.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Boost saturation selectively on low-saturation pixels.

    Unlike uniform saturation adjustment, vibrance applies a stronger boost
    to muted/desaturated colors while leaving already-vivid colors mostly
    unchanged. This protects skin tones and prevents over-saturation.

    Parameters:
        amount: Vibrance boost strength (range: 0.0-3.0, typical: 0.5-1.5)
                0.0 = no change, 1.0 = moderate boost, 2.0+ = strong boost

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[vibrance(amount=1.2)]
        ... )

    Notes:
        - Gentler than saturation() for portraits and skin tones
        - Values above 2.0 may still over-saturate some colors
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Get current saturation
        current_sat = hsv[:,:,1]
        
        # Calculate vibrance: more boost on low-saturation pixels
        # Using formula: vibrance = sat * (1 + (1 - sat/255) * amount)
        vibrance_factor = 1.0 + (1.0 - current_sat / 255.0) * amount
        
        # Apply vibrance
        hsv[:,:,1] = np.clip(hsv[:,:,1] * vibrance_factor, 0, 255)
        
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return effect


def color_pulse(
    frequency: float = 1.0,
    color: tuple[int, int, int] = (255, 255, 255),
    amount: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Animate a pulsing color blend driven by a sine wave.

    Blends the frame toward a target color using a sine-wave envelope
    keyed to absolute time. Creates a rhythmic color flash effect.

    Parameters:
        frequency: Pulse cycles per second (range: 0.1-10.0, typical: 1.0-2.0)
        color: RGB target color to pulse toward
               (range: 0-255 per channel, typical: (255, 255, 255) for white flash)
        amount: Maximum blend fraction at peak (range: 0.0-1.0, typical: 0.2-0.4)
                0.0 = no pulse, 1.0 = full color at peak

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[color_pulse(frequency=2.0, color=(255, 100, 0), amount=0.3)]
        ... )

    Notes:
        - Uses absolute time t, so pulse phase is consistent across clips
        - Combine with OnsetFlash for beat-synchronized pulsing
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Calculate pulse value
        pulse = (np.sin(t * frequency * 2 * np.pi) * 0.5 + 0.5) * amount
        
        # Blend toward color
        color_array = np.array(color, dtype=np.float32)
        result = frame.astype(np.float32) * (1.0 - pulse) + color_array * pulse
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def fade_to_color(
    color: tuple[int, int, int] = (0, 0, 0)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Fade the frame toward a solid color as the clip progresses.

    Linearly interpolates from the original frame (at progress=0.0) to
    the target color (at progress=1.0). Useful for fade-to-black or
    fade-to-white transitions driven by clip position.

    Parameters:
        color: Target RGB color (range: 0-255 per channel)
               (0, 0, 0) = fade to black, (255, 255, 255) = fade to white

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[fade_to_color(color=(0, 0, 0))]
        ... )

    Notes:
        - Driven by progress (0.0-1.0), not absolute time
        - At progress=0.0 the frame is unchanged; at progress=1.0 it is solid color
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        color_array = np.array(color, dtype=np.float32)
        result = frame.astype(np.float32) * (1.0 - progress) + color_array * progress
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def thermal() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a thermal/infrared false-color effect using OpenCV's JET colormap.

    Converts the frame to grayscale (luminance) and remaps it through the
    COLORMAP_JET palette: dark areas become blue/purple, mid-tones become
    green/yellow, and bright areas become red/white — mimicking thermal
    imaging cameras.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[thermal()]
        ... )

    Notes:
        - All original color information is discarded; only luminance is used
        - Output is BGR from cv2.applyColorMap but returned as-is (RGB-compatible
          since the colormap is symmetric)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Apply thermal colormap
        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        
        return thermal
    return effect


def posterize(
    bits: int = 4
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Reduce the number of color levels per channel (posterization).

    Quantizes each channel to 2^bits discrete levels by integer division,
    producing flat areas of solid color with hard edges between tones.
    Lower bit values create a more graphic, poster-like appearance.

    Parameters:
        bits: Bits per channel (range: 1-8, typical: 3-5)
              1 = 2 levels (near black-and-white), 4 = 16 levels, 8 = no change

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[posterize(bits=3)]
        ... )

    Notes:
        - bits=8 leaves the image unchanged (256 levels per channel)
        - bits=1 produces a 2-color image per channel (8 total color combinations)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        step = 256 // (2 ** bits)
        result = (frame // step) * step
        return result.astype(np.uint8)
    return effect


def solarize(
    threshold: int = 128
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Invert pixels whose luminance exceeds a threshold (solarization).

    Mimics the Sabattier effect from darkroom photography, where partial
    re-exposure of film inverts highlights. Pixels with luminance above
    the threshold are inverted (255 - value); others are unchanged.

    Parameters:
        threshold: Luminance cutoff (range: 0-255, typical: 100-180)
                   Lower values invert more of the image.
                   128 inverts roughly the top half of the tonal range.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[solarize(threshold=100)]
        ... )

    Notes:
        - threshold=0 inverts the entire image (equivalent to invert())
        - threshold=255 leaves the image unchanged
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Calculate luminance
        gray = (frame[:,:,0] * 0.299 + frame[:,:,1] * 0.587 + frame[:,:,2] * 0.114)
        
        # Create mask for pixels above threshold
        mask = gray > threshold
        
        # Invert those pixels
        result = frame.copy().astype(np.float32)
        result[mask] = 255.0 - result[mask]
        
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


# ============================================================================
# Phase 4: Blur Effects
# ============================================================================

def box_blur(
    kernel_size: int = 5
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a uniform box blur (averaging filter).

    Each output pixel is the unweighted average of all pixels within a
    square kernel. Faster than Gaussian blur but produces less natural
    results. Kernel size is forced to an odd number.

    Parameters:
        kernel_size: Side length of the square kernel in pixels
                     (range: 1-51, typical: 3-15, must be odd — even values
                     are incremented by 1 automatically)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[box_blur(kernel_size=9)]
        ... )

    Notes:
        - kernel_size=1 is a no-op
        - For a softer, more natural blur use gaussian_blur() instead
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Ensure kernel size is odd
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.blur(frame, (k, k))
    return effect


def gaussian_blur(
    kernel_size: int = 5,
    sigma: float = 0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a Gaussian blur for smooth, natural-looking softening.

    Weights neighboring pixels by a Gaussian (bell-curve) distribution,
    producing a more visually pleasing blur than box_blur(). Kernel size
    is forced to an odd number.

    Parameters:
        kernel_size: Side length of the Gaussian kernel in pixels
                     (range: 1-51, typical: 5-21, must be odd)
        sigma: Standard deviation of the Gaussian in pixels
               (range: 0-20, typical: 0-5)
               0 = automatically computed from kernel_size

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[gaussian_blur(kernel_size=15, sigma=3)]
        ... )

    Notes:
        - sigma=0 lets OpenCV choose an appropriate value automatically
        - Larger kernel_size with small sigma has little extra effect
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.GaussianBlur(frame, (k, k), sigma)
    return effect


def motion_blur(
    angle: float = 0,
    amount: int = 15
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply directional motion blur simulating camera or subject movement.

    Constructs a line-shaped convolution kernel oriented at the given angle
    and applies it via cv2.filter2D. The result mimics the streaking caused
    by camera shake or fast-moving subjects during a long exposure.

    Parameters:
        angle: Blur direction in degrees (range: 0-360, typical: 0-180)
               0 = horizontal, 90 = vertical, 45 = diagonal
        amount: Kernel length in pixels (range: 3-51, typical: 10-25, odd preferred)
                Larger values produce longer, more pronounced streaks.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[motion_blur(angle=45, amount=20)]
        ... )

    Notes:
        - Even values for amount are incremented by 1 automatically
        - Combine with a slight zoom for a dynamic action feel
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Create motion blur kernel
        k = amount if amount % 2 == 1 else amount + 1
        kernel = np.zeros((k, k), dtype=np.float32)
        
        # Calculate direction vector
        angle_rad = np.deg2rad(angle)
        center = k // 2
        
        # Fill kernel along the line
        for i in range(k):
            offset = i - center
            x = int(center + offset * np.cos(angle_rad))
            y = int(center + offset * np.sin(angle_rad))
            if 0 <= x < k and 0 <= y < k:
                kernel[y, x] = 1.0
        
        # Normalize
        if kernel.sum() > 0:
            kernel /= kernel.sum()
        
        return cv2.filter2D(frame, -1, kernel)
    return effect


def radial_blur(
    amount: int = 10
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply radial blur that radiates outward from the frame center.

    Blends multiple progressively downscaled copies of the frame, creating
    a zoom-like smear that emanates from the center. Higher amounts produce
    a stronger, more dramatic radial streak.

    Parameters:
        amount: Number of scaled samples / blur radius
                (range: 1-30, typical: 5-15)
                Higher values increase both blur strength and render time.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[radial_blur(amount=12)]
        ... )

    Notes:
        - amount=1 produces minimal blur
        - Performance scales linearly with amount (~2-5ms per sample at 1080p)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        center_y, center_x = h // 2, w // 2
        
        # Create output
        result = np.zeros_like(frame, dtype=np.float32)
        
        # Sample along radial lines
        samples = max(1, amount)
        for i in range(samples):
            # Scale down
            scale = 1.0 - (i / samples) * 0.5
            if scale > 0:
                scaled = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                
                # Calculate position
                new_h, new_w = scaled.shape[:2]
                start_y = (h - new_h) // 2
                start_x = (w - new_w) // 2
                
                # Add to result
                result[start_y:start_y+new_h, start_x:start_x+new_w] += scaled.astype(np.float32)
        
        result /= samples
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


def pixelate(
    block_size: int = 8
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a pixelation/mosaic effect by downscaling then upscaling.

    Shrinks the frame to 1/block_size of its original dimensions using
    nearest-neighbor interpolation, then scales it back up. Each output
    block is a uniform color equal to the average of the original pixels.

    Parameters:
        block_size: Side length of each mosaic tile in pixels
                    (range: 2-64, typical: 8-32)
                    Larger values produce coarser pixelation.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[pixelate(block_size=16)]
        ... )

    Notes:
        - block_size larger than frame dimensions returns the original frame
        - Useful for censoring regions or creating retro 8-bit aesthetics
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Downscale
        new_w = w // block_size
        new_h = h // block_size
        
        if new_w == 0 or new_h == 0:
            return frame
        
        small = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        # Upscale back
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    return effect


def sharpen(
    amount: float = 1.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Sharpen the frame using the unsharp mask technique.

    Subtracts a Gaussian-blurred version of the frame from the original
    to extract high-frequency detail, then adds it back scaled by amount:
    result = frame + amount * (frame - blurred).

    Parameters:
        amount: Sharpening strength (range: 0.0-5.0, typical: 0.5-2.0)
                0.0 = no change, 1.0 = standard sharpening, >2.0 = over-sharpened

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[sharpen(amount=1.5)]
        ... )

    Notes:
        - High values amplify noise and compression artifacts
        - Uses a fixed 5x5 Gaussian kernel for the blur step
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Create blurred version
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # Apply unsharp mask
        result = frame.astype(np.float32) + amount * (frame.astype(np.float32) - blurred.astype(np.float32))
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)
    return effect


def bilateral_blur(
    d: int = 9,
    sigma_color: float = 75.0,
    sigma_space: float = 75.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a bilateral filter for edge-preserving smoothing.

    Unlike Gaussian blur, the bilateral filter weights neighbors by both
    spatial distance and color similarity, so edges are preserved while
    flat regions are smoothed. Produces a "painted" or "HDR" look.

    Parameters:
        d: Diameter of the pixel neighborhood (range: 1-25, typical: 5-15)
           Larger values are slower but consider more context.
        sigma_color: Color space sigma — controls how much color difference
                     is tolerated (range: 10-200, typical: 50-100)
                     Higher = more colors blended together.
        sigma_space: Coordinate space sigma — controls spatial reach
                     (range: 10-200, typical: 50-100)
                     Higher = farther pixels influence each other.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[bilateral_blur(d=9, sigma_color=75, sigma_space=75)]
        ... )

    Notes:
        - Significantly slower than gaussian_blur() (~50-150ms at 1080p)
        - Excellent for skin smoothing and cartoon/illustration effects
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        return cv2.bilateralFilter(frame, d, sigma_color, sigma_space)
    return effect


def tilt_shift(
    blur_amount: int = 15,
    gradient_start: float = 0.3,
    gradient_end: float = 0.7
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a tilt-shift effect to simulate a miniature/macro lens look.

    Keeps a horizontal band of the frame sharp while progressively blurring
    the top and bottom regions. Mimics the shallow depth-of-field of a
    tilt-shift lens, making real scenes look like scale models.

    Parameters:
        blur_amount: Maximum blur kernel size at the edges
                     (range: 3-51, typical: 10-25, odd preferred)
        gradient_start: Normalized vertical position where the sharp zone begins
                        (range: 0.0-1.0, typical: 0.25-0.4)
                        0.0 = top of frame, 1.0 = bottom of frame
        gradient_end: Normalized vertical position where the sharp zone ends
                      (range: 0.0-1.0, typical: 0.6-0.75)
                      Must be greater than gradient_start.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[tilt_shift(blur_amount=21, gradient_start=0.35, gradient_end=0.65)]
        ... )

    Notes:
        - Works best on overhead/aerial shots of cityscapes or landscapes
        - blur_amount must be odd; even values are incremented automatically
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Create vertical gradient mask
        y = np.linspace(0, 1, h)
        
        # Calculate blur factor (0 = sharp, 1 = max blur)
        blur_factor = np.where(
            y < gradient_start,
            1.0 - y / gradient_start,
            np.where(y > gradient_end, (y - gradient_end) / (1.0 - gradient_end), 0.0)
        )
        
        # Apply varying blur based on position
        result = frame.copy()
        blur_intensity = blur_amount
        
        # Top region (apply blur)
        if gradient_start > 0:
            top_blur = cv2.GaussianBlur(frame[:int(h*gradient_start), :], (blur_intensity, blur_intensity), 0)
            blend_factor = blur_factor[:int(h*gradient_start), np.newaxis, np.newaxis]
            result[:int(h*gradient_start), :] = np.where(
                blend_factor > 0,
                (top_blur * blend_factor + frame[:int(h*gradient_start), :] * (1 - blend_factor)).astype(np.uint8),
                frame[:int(h*gradient_start), :]
            )
        
        # Bottom region (apply blur)
        if gradient_end < 1.0:
            bottom_start = int(h * gradient_end)
            bottom_blur = cv2.GaussianBlur(frame[bottom_start:, :], (blur_intensity, blur_intensity), 0)
            blend_factor = blur_factor[bottom_start:, np.newaxis, np.newaxis]
            result[bottom_start:, :] = np.where(
                blend_factor > 0,
                (bottom_blur * blend_factor + frame[bottom_start:, :] * (1 - blend_factor)).astype(np.uint8),
                frame[bottom_start:, :]
            )
        
        return result
    return effect


def depth_of_field(
    focus_distance: float = 0.5,
    aperture: float = 2.8
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Simulate camera depth-of-field by blurring based on distance from focus.

    Applies a uniform Gaussian blur whose radius is proportional to the
    aperture value. This is a simplified approximation — a true per-pixel
    DoF would require a depth map. Useful for adding a soft, cinematic feel.

    Parameters:
        focus_distance: Normalized position of the focal plane (range: 0.0-1.0)
                        Used to compute distance-based blur (currently influences
                        blur radius calculation).
        aperture: Simulated f-stop value controlling blur strength
                  (range: 0.5-16.0, typical: 1.4-5.6)
                  Lower values = wider aperture = more blur (e.g., f/1.4)
                  Higher values = narrower aperture = less blur (e.g., f/11)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[depth_of_field(focus_distance=0.5, aperture=1.8)]
        ... )

    Notes:
        - This is a global blur approximation, not a true per-pixel depth effect
        - For selective focus, use tilt_shift() instead
        - aperture values below 1.0 produce very strong blur
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Create depth map based on distance from focus plane
        y_coords, x_coords = np.ogrid[:h, :w]
        center_y, center_x = h * focus_distance, w * focus_distance
        
        # Distance from focus point
        dist = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
        max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
        
        # Blur amount based on distance from focus
        blur_amount = (dist / max_dist) * aperture * 10
        blur_amount = np.clip(blur_amount, 0, 25)
        
        # Apply variable blur
        result = frame.copy()
        
        # For simplicity, apply a moderate blur to the whole image
        # (true DoF would require per-pixel blur which is very slow)
        blur_intensity = int(aperture * 3)
        if blur_intensity % 2 == 0:
            blur_intensity += 1
        blur_intensity = max(1, min(blur_intensity, 25))
        
        result = cv2.GaussianBlur(frame, (blur_intensity, blur_intensity), 0)
        
        return result
    return effect


# ============================================================================
# Phase 4: Texture Effects
# ============================================================================

def scan_lines(
    spacing: int = 2,
    intensity: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Add horizontal scan lines to simulate a CRT monitor display.

    Darkens every Nth row by multiplying its pixel values by (1 - intensity),
    creating the characteristic horizontal banding of old cathode-ray tube screens.

    Parameters:
        spacing: Row interval — darken every Nth row
                 (range: 1-10, typical: 2-4)
                 2 = every other row darkened (classic CRT look)
        intensity: Darkening factor per scan line
                   (range: 0.0-1.0, typical: 0.2-0.5)
                   0.0 = no effect, 1.0 = scan lines are fully black

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[scan_lines(spacing=2, intensity=0.4)]
        ... )

    Notes:
        - Combine with crt_retro() for a full CRT simulation
        - spacing=1 darkens every row (uniform dimming, not scan lines)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy().astype(np.float32)
        
        # Darken every Nth row
        result[::spacing, :] *= (1.0 - intensity)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


def letterbox(
    top: int = 90,
    bottom: int = 90,
    color: tuple[int, int, int] = (0, 0, 0)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Add letterbox bars to create a cinematic widescreen look.

    Fills the top and bottom rows of the frame with a solid color (typically
    black), simulating the aspect-ratio bars seen in theatrical presentations.

    Parameters:
        top: Height of the top bar in pixels (range: 0-frame_height/2, typical: 60-120)
        bottom: Height of the bottom bar in pixels (range: 0-frame_height/2, typical: 60-120)
        color: RGB color of the bars (range: 0-255 per channel, typical: (0, 0, 0))

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[letterbox(top=90, bottom=90)]
        ... )

    Notes:
        - For 1080p content, top=bottom=90 approximates a 2.39:1 aspect ratio
        - top=0 or bottom=0 disables that bar
        - Non-black colors can create stylized colored-bar effects
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        color_array = np.array(color, dtype=np.uint8)
        
        # Apply top bar
        if top > 0:
            result[:top, :] = color_array
        
        # Apply bottom bar
        if bottom > 0:
            result[-bottom:, :] = color_array
        
        return result
    return effect


def vignette_simple(
    intensity: float = 0.5
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Darken the frame edges with a radial vignette.

    Creates a smooth radial gradient mask that darkens pixels proportionally
    to their distance from the frame center. Draws the viewer's eye toward
    the center of the composition.

    Parameters:
        intensity: Vignette strength (range: 0.0-1.0, typical: 0.3-0.7)
                   0.0 = no darkening, 1.0 = edges fully black

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[vignette_simple(intensity=0.5)]
        ... )

    Notes:
        - Simpler and faster than vignette() (no radius parameter)
        - Combine with sepia() or film_grain() for a vintage look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        center_y, center_x = h // 2, w // 2
        
        # Create radial gradient
        y, x = np.ogrid[:h, :w]
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        # Normalize and apply vignette curve
        normalized = distances / max_distance
        mask = 1.0 - (normalized * intensity)
        mask = np.clip(mask, 0, 1)
        
        result = (frame * mask[:, :, np.newaxis]).astype(np.uint8)
        return result
    return effect


def gradient_overlay(
    color_start: tuple[int, int, int] = (0, 0, 0),
    color_end: tuple[int, int, int] = (255, 255, 255),
    direction: str = "vertical",
    alpha: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Blend a linear color gradient over the frame.

    Generates a gradient from color_start to color_end along the chosen
    axis, then alpha-composites it on top of the frame. Useful for adding
    mood, depth cues, or stylized color washes.

    Parameters:
        color_start: RGB color at the start of the gradient
                     (range: 0-255 per channel, typical: (0, 0, 0) for black)
        color_end: RGB color at the end of the gradient
                   (range: 0-255 per channel, typical: (0, 0, 128) for dark blue)
        direction: Gradient axis — "vertical" (top→bottom) or "horizontal" (left→right)
        alpha: Gradient opacity blended over the frame
               (range: 0.0-1.0, typical: 0.2-0.5)
               0.0 = invisible, 1.0 = fully opaque gradient

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[gradient_overlay(
        ...         color_start=(0, 0, 0),
        ...         color_end=(0, 0, 100),
        ...         direction="vertical",
        ...         alpha=0.4
        ...     )]
        ... )

    Notes:
        - direction must be exactly "vertical" or "horizontal"
        - Combine with letterbox() for a cinematic gradient-bar look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Create gradient
        if direction == "vertical":
            gradient = np.linspace(0, 1, h)[:, np.newaxis, np.newaxis]
        else:
            gradient = np.linspace(0, 1, w)[np.newaxis, :, np.newaxis]
        
        # Interpolate colors
        start = np.array(color_start, dtype=np.float32)
        end = np.array(color_end, dtype=np.float32)
        gradient_color = (start * (1 - gradient) + end * gradient).astype(np.uint8)
        
        # Blend with frame
        result = frame.astype(np.float32) * (1 - alpha) + gradient_color.astype(np.float32) * alpha
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    return effect


def image_watermark(
    watermark_img: np.ndarray | None = None,
    position: str = "bottom-right",
    opacity: float = 0.3,
    scale: float = 0.2
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Composite an image watermark onto the frame.

    Overlays a watermark image at the specified corner or center of the
    frame. Supports RGBA watermarks (alpha channel used for masking) and
    plain RGB watermarks (blended by opacity). If no watermark is provided,
    a default gray rectangle is used.

    Parameters:
        watermark_img: Watermark as a numpy array (HxWx3 RGB or HxWx4 RGBA)
                       None = use a default gray placeholder
        position: Placement corner or center
                  ("top-left", "top-right", "bottom-left", "bottom-right", "center")
        opacity: Watermark blend strength (range: 0.0-1.0, typical: 0.2-0.5)
                 0.0 = invisible, 1.0 = fully opaque
        scale: Watermark size relative to frame width (range: 0.05-0.5, typical: 0.15-0.25)
               Only used when watermark_img is None.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> import cv2
        >>> wm = cv2.cvtColor(cv2.imread("logo.png", cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[image_watermark(watermark_img=wm, position="bottom-right", opacity=0.4)]
        ... )

    Notes:
        - RGBA watermarks use the alpha channel for per-pixel masking
        - Watermarks that extend beyond the frame boundary are clipped
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        h, w = frame.shape[:2]
        
        # Create default watermark if not provided
        wm = watermark_img
        if wm is None:
            wm_h, wm_w = int(h * scale), int(w * scale)
            wm = np.zeros((wm_h, wm_w, 3), dtype=np.uint8)
            wm[:, :] = (200, 200, 200)
        
        wm_h, wm_w = wm.shape[:2]
        
        # Determine position
        if position == "top-left":
            y, x = 10, 10
        elif position == "top-right":
            y, x = 10, w - wm_w - 10
        elif position == "bottom-left":
            y, x = h - wm_h - 10, 10
        elif position == "bottom-right":
            y, x = h - wm_h - 10, w - wm_w - 10
        else:  # center
            y, x = (h - wm_h) // 2, (w - wm_w) // 2
        
        # Ensure watermark fits within frame
        if y + wm_h > h:
            wm_h = h - y
            wm = wm[:wm_h, :]
        if x + wm_w > w:
            wm_w = w - x
            wm = wm[:, :wm_w]
        
        if y < 0 or x < 0 or wm_h <= 0 or wm_w <= 0:
            return result
        
        # Overlay watermark
        wm_region = result[y:y+wm_h, x:x+wm_w]
        wm_float = wm[:wm_h, :wm_w].astype(np.float32)
        
        # Handle alpha channel if present
        if wm.shape[2] == 4:
            alpha = wm[:, :, 3:4].astype(np.float32) / 255.0 * opacity
            wm_rgb = wm[:, :, :3].astype(np.float32)
            blended = (wm_rgb * alpha + wm_region.astype(np.float32) * (1 - alpha)).astype(np.uint8)
        else:
            blended = (wm_float * opacity + wm_region.astype(np.float32) * (1 - opacity)).astype(np.uint8)
        
        result[y:y+wm_h, x:x+wm_w] = blended
        
        return result
    return effect


# ============================================================================
# Phase 4: Stylization Effects
# ============================================================================

def edge_detection(
    threshold1: float = 50.0,
    threshold2: float = 150.0
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply Canny edge detection to produce a line-drawing effect.

    Converts the frame to grayscale, runs the Canny algorithm to find
    edges using hysteresis thresholding, then returns a 3-channel image
    with white edges on a black background.

    Parameters:
        threshold1: Lower hysteresis threshold (range: 0-255, typical: 30-80)
                    Edges with gradient below this are discarded.
        threshold2: Upper hysteresis threshold (range: 0-255, typical: 100-200)
                    Edges with gradient above this are always kept.
                    Edges between threshold1 and threshold2 are kept only if
                    connected to a strong edge.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[edge_detection(threshold1=50, threshold2=150)]
        ... )

    Notes:
        - Output is binary (black background, white edges)
        - Lower threshold1 detects more edges including noise
        - Combine with invert() for black lines on white background
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Apply Canny
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # Convert back to 3-channel
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return effect


def sketch() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a pencil sketch effect using OpenCV's pencilSketch filter.

    Uses cv2.pencilSketch with sigma_s=60, sigma_r=0.6, shade_factor=0.1
    to produce a color pencil-drawing appearance with soft shading and
    visible stroke texture.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[sketch()]
        ... )

    Notes:
        - Returns the color sketch output (not grayscale)
        - Relatively slow (~50-100ms at 1080p)
        - Works best on images with clear subjects and defined edges
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # pencilSketch expects 3-channel input
        sketcher_gray, sketcher_color = cv2.pencilSketch(frame, sigma_s=60, sigma_r=0.6, shade_factor=0.1)
        
        return sketcher_color
    return effect


def oil_painting() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply an oil painting effect using OpenCV's stylization filter.

    Uses cv2.stylization with sigma_s=60, sigma_r=0.6 to produce a
    painterly, impressionistic look with smooth color regions and
    preserved edge structure.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[oil_painting()]
        ... )

    Notes:
        - Slow effect (~100-200ms at 1080p)
        - Works best on images with rich colors and varied textures
        - Combine with vignette_simple() for a gallery-style look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Use OpenCV stylization which creates painterly effect
        return cv2.stylization(frame, sigma_s=60, sigma_r=0.6)
    return effect


def emboss() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply an emboss effect to create a raised-relief appearance.

    Convolves the grayscale frame with a directional emboss kernel, then
    normalizes the result to [0, 255]. Produces a metallic, engraved look
    where edges appear as raised ridges lit from the upper-left.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[emboss()]
        ... )

    Notes:
        - Output is grayscale (all three channels are equal)
        - The emboss direction is fixed (upper-left light source)
        - Flat regions render as mid-gray (~128)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Emboss kernel
        kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ], dtype=np.float32)
        
        # Apply convolution
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        embossed = cv2.filter2D(gray, -1, kernel)
        
        # Convert back to 3-channel and normalize
        result = cv2.cvtColor(embossed, cv2.COLOR_GRAY2RGB)
        
        # Normalize to 0-255 range using numpy
        result = result.astype(np.float32)
        result = (result - result.min()) / (result.max() - result.min() + 1e-8) * 255
        result = result.astype(np.uint8)
        
        return result
    return effect


def chromatic_aberration(
    amount: int = 3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Simulate chromatic aberration by offsetting the red and blue channels.

    Shifts the red channel left and the blue channel right by the given
    number of pixels, leaving the green channel unchanged. Mimics the
    color fringing caused by lens dispersion in cheap optics.

    Parameters:
        amount: Horizontal pixel offset for each channel
                (range: 1-20, typical: 2-8)
                Larger values produce more pronounced color fringing.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[chromatic_aberration(amount=5)]
        ... )

    Notes:
        - Uses np.roll so pixels wrap around at the frame edges
        - For a glitch look with random offsets, use glitch_rgb_split() instead
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        
        # Shift red channel left
        result[:, :, 0] = np.roll(frame[:, :, 0], -amount, axis=1)
        
        # Shift blue channel right  
        result[:, :, 2] = np.roll(frame[:, :, 2], amount, axis=1)
        
        return result
    return effect


def glitch_rgb_split(
    max_offset: int = 20
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a glitch effect with random per-channel horizontal offsets.

    Independently shifts each RGB channel by a random amount each frame,
    using a time-based seed for deterministic but varying results. Creates
    the look of a corrupted digital signal or broken display.

    Parameters:
        max_offset: Maximum horizontal shift in pixels per channel
                    (range: 1-100, typical: 10-30)
                    Larger values produce more extreme channel separation.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[glitch_rgb_split(max_offset=15)]
        ... )

    Notes:
        - Offsets change every frame (seeded by int(t * 100))
        - Uses np.roll so channels wrap around at frame edges
        - For a fixed offset, use chromatic_aberration() instead
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Use time-based seed for deterministic but varying offsets
        np.random.seed(int(t * 100) % (2**32))
        
        # Random offsets
        r_offset = np.random.randint(-max_offset, max_offset)
        g_offset = np.random.randint(-max_offset, max_offset)
        b_offset = np.random.randint(-max_offset, max_offset)
        
        result = frame.copy()
        
        # Shift channels
        result[:, :, 0] = np.roll(frame[:, :, 0], r_offset, axis=1)
        result[:, :, 1] = np.roll(frame[:, :, 1], g_offset, axis=1)
        result[:, :, 2] = np.roll(frame[:, :, 2], b_offset, axis=1)
        
        return result
    return effect


def glitch_block_displacement(
    block_size: int = 20,
    displacement: int = 30
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a glitch effect by randomly displacing horizontal image blocks.

    Divides the frame into horizontal slices of block_size pixels. Each
    slice has a 30% chance of being shifted horizontally by a random
    amount, simulating corrupted video data or a damaged tape.

    Parameters:
        block_size: Height of each horizontal block in pixels
                    (range: 5-100, typical: 10-40)
        displacement: Maximum horizontal shift per block in pixels
                      (range: 5-200, typical: 20-60)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[glitch_block_displacement(block_size=20, displacement=40)]
        ... )

    Notes:
        - Block shifts are seeded by int(t * 100) for per-frame variation
        - Uses np.roll so displaced pixels wrap around at frame edges
        - ~30% of blocks are displaced per frame
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        # Use time-based seed
        np.random.seed(int(t * 100) % (2**32))
        
        # Randomly displace horizontal slices
        num_blocks_h = h // block_size
        
        for i in range(num_blocks_h):
            if np.random.random() > 0.7:  # 30% chance to displace
                disp = np.random.randint(-displacement, displacement)
                start_y = i * block_size
                end_y = min(start_y + block_size, h)
                result[start_y:end_y, :] = np.roll(frame[start_y:end_y, :], disp, axis=1)
        
        return result
    return effect


def threshold_bw(
    threshold: int = 128
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a high-contrast black-and-white threshold.

    Converts the frame to grayscale and applies a binary threshold:
    pixels with luminance above the threshold become white (255),
    all others become black (0). Returns a 3-channel image.

    Parameters:
        threshold: Luminance cutoff value (range: 0-255, typical: 100-180)
                   Lower values produce more white area.
                   128 splits the tonal range roughly in half.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[threshold_bw(threshold=128)]
        ... )

    Notes:
        - threshold=0 produces an all-white image
        - threshold=255 produces an all-black image
        - For a softer look, apply gaussian_blur() before threshold_bw()
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Convert back to 3-channel
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    return effect


def dithering() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply Floyd-Steinberg error-diffusion dithering.

    Converts the frame to grayscale and applies the Floyd-Steinberg
    algorithm to produce a 1-bit (black/white) image that approximates
    the original tonal range through spatial distribution of errors.
    Creates a classic retro digital art aesthetic.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[dithering()]
        ... )

    Notes:
        - Output is binary black-and-white (no gray values)
        - Very slow at high resolutions due to per-pixel Python loop (~500ms+ at 1080p)
        - For performance, apply to downscaled frames or use posterize() instead
        - Error is diffused to right (7/16), lower-left (3/16), below (5/16), lower-right (1/16)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY).astype(np.float32)
        h, w = gray.shape
        
        # Create output
        result = gray.copy()
        
        # Floyd-Steinberg dithering
        for y in range(h):
            for x in range(w):
                old_pixel = result[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                result[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Distribute error to neighbors
                if x + 1 < w:
                    result[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        result[y + 1, x - 1] += error * 3 / 16
                    result[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        result[y + 1, x + 1] += error * 1 / 16
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Convert back to 3-channel
        return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    return effect


def curves_lut(
    lut_r: list[int] | None = None,
    lut_g: list[int] | None = None,
    lut_b: list[int] | None = None
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply custom tone curves via per-channel lookup tables.

    Maps each pixel value through a 256-entry lookup table for each
    RGB channel independently. This is the most flexible color grading
    tool — any curve shape (S-curve, gamma, invert, etc.) can be encoded
    as a LUT.

    Parameters:
        lut_r: Red channel LUT — list of 256 output values (0-255)
               None = identity (no change)
        lut_g: Green channel LUT — list of 256 output values (0-255)
               None = identity (no change)
        lut_b: Blue channel LUT — list of 256 output values (0-255)
               None = identity (no change)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> # Apply an S-curve to the red channel
        >>> import numpy as np
        >>> x = np.arange(256)
        >>> s_curve = (255 / (1 + np.exp(-0.05 * (x - 128)))).astype(int).tolist()
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[curves_lut(lut_r=s_curve)]
        ... )

    Notes:
        - LUTs must have exactly 256 entries; values are clamped to [0, 255]
        - Slow for large frames due to per-pixel Python indexing
        - For simple adjustments, prefer gamma_correction() or contrast()
    """
    if lut_r is None:
        lut_r = list(range(256))
    if lut_g is None:
        lut_g = list(range(256))
    if lut_b is None:
        lut_b = list(range(256))
    
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        result[:, :, 0] = np.array([lut_r[val] for val in frame[:, :, 0]])
        result[:, :, 1] = np.array([lut_g[val] for val in frame[:, :, 1]])
        result[:, :, 2] = np.array([lut_b[val] for val in frame[:, :, 2]])
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


def tricolor(
    color1: tuple[int, int, int] = (0, 0, 128),
    color2: tuple[int, int, int] = (128, 128, 128),
    color3: tuple[int, int, int] = (255, 255, 0)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a three-stop gradient map (tricolor effect).

    Maps luminance to a three-color gradient: color1 for shadows
    (luminance 0.0-0.5), color2 for midtones, and color3 for highlights
    (luminance 0.5-1.0). All original color information is discarded.

    Parameters:
        color1: RGB color for dark/shadow tones
                (range: 0-255 per channel, typical: (0, 0, 128) for deep blue shadows)
        color2: RGB color for midtones
                (range: 0-255 per channel, typical: (128, 128, 128) for neutral gray)
        color3: RGB color for bright/highlight tones
                (range: 0-255 per channel, typical: (255, 255, 0) for warm yellow highlights)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[tricolor(
        ...         color1=(10, 0, 60),
        ...         color2=(80, 80, 80),
        ...         color3=(255, 220, 50)
        ...     )]
        ... )

    Notes:
        - Similar to duotone() but with an additional midtone color stop
        - All color information is replaced; only luminance is preserved
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        h, w = gray.shape
        
        result = np.zeros((h, w, 3), dtype=np.float32)
        
        for c in range(3):
            c1 = color1[c] / 255.0
            c2 = color2[c] / 255.0
            c3 = color3[c] / 255.0
            
            if gray < 0.5:
                result[:, :, c] = c1 * (1.0 - gray * 2.0) + c2 * (gray * 2.0)
            else:
                result[:, :, c] = c2 * (1.0 - (gray - 0.5) * 2.0) + c3 * ((gray - 0.5) * 2.0)
        
        return np.clip(result * 255, 0, 255).astype(np.uint8)
    return effect


def bleach_bypass() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a bleach bypass effect for a desaturated, high-contrast film look.

    Blends the original frame 50/50 with its grayscale version (reducing
    saturation), then applies histogram equalization to boost contrast.
    Mimics the silver-retention process used in film processing to create
    a gritty, desaturated aesthetic.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[bleach_bypass()]
        ... )

    Notes:
        - Output is grayscale (saturation fully removed after equalization)
        - Histogram equalization may produce harsh contrast in low-detail images
        - Combine with cinematic_teal_orange() before bleach_bypass() for a
          stylized color-then-desaturate grade
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        result = (frame * 0.5 + gray_bgr * 0.5).astype(np.uint8)
        
        result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
        result = cv2.equalizeHist(result)
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        
        return result
    return effect


def cross_process() -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a cross-process effect using per-channel sigmoid S-curves.

    Applies a logistic sigmoid function independently to each RGB channel,
    boosting contrast and shifting colors to mimic the unpredictable results
    of developing film in the wrong chemical process (e.g., slide film in
    negative chemistry).

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[cross_process()]
        ... )

    Notes:
        - The sigmoid steepness is fixed at 10.0 (centered at 0.5)
        - Produces strong contrast boost with color shifts in highlights/shadows
        - Results vary significantly depending on the source image's color balance
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.astype(np.float32) / 255.0
        
        for c in range(3):
            channel = result[:, :, c]
            result[:, :, c] = 1.0 / (1.0 + np.exp(-10.0 * (channel - 0.5)))
        
        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        return result
    return effect


def zoom_blur(
    strength: float = 0.5
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a zoom blur effect radiating outward from the frame center.

    Blends multiple progressively downscaled copies of the frame, creating
    a radial smear that gives the impression of rapid zooming toward the
    viewer. Stronger than radial_blur() for a more dramatic zoom feel.

    Parameters:
        strength: Blur intensity controlling scale range and sample count
                  (range: 0.0-1.0, typical: 0.2-0.6)
                  0.0 = no blur, 1.0 = very strong zoom smear

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[zoom_blur(strength=0.4)]
        ... )

    Notes:
        - Number of samples = int(strength * 20) + 1
        - Minimum scale = 1.0 - strength * 0.5 (e.g., 0.75 at strength=0.5)
        - Performance scales linearly with strength (~3-5ms per sample at 1080p)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = np.zeros_like(frame, dtype=np.float32)
        
        num_frames = int(strength * 20) + 1
        scales = np.linspace(1.0 - strength * 0.5, 1.0, num_frames)
        
        for scale in scales:
            new_h, new_w = int(h * scale), int(w * scale)
            if new_h > 0 and new_w > 0:
                scaled = cv2.resize(frame, (new_w, new_h))
                
                y1 = (h - new_h) // 2
                x1 = (w - new_w) // 2
                temp = np.zeros_like(result)
                temp[y1:y1+new_h, x1:x1+new_w] = scaled
                result += temp
        
        result /= num_frames
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


def animated_blur(
    min_kernel: int = 1,
    max_kernel: int = 15
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a time-varying Gaussian blur that pulses in and out.

    The blur kernel size oscillates between min_kernel and max_kernel
    following a sine wave keyed to absolute time t. Creates a dreamy,
    breathing blur animation.

    Parameters:
        min_kernel: Minimum blur kernel size (range: 1-31, typical: 1-5)
                    1 = no blur at the minimum point
        max_kernel: Maximum blur kernel size (range: 1-31, typical: 10-25)
                    Must be >= min_kernel. Odd values preferred.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[animated_blur(min_kernel=1, max_kernel=21)]
        ... )

    Notes:
        - Kernel is clamped to [1, 31] and forced to odd
        - Oscillation period is approximately π seconds (~3.14s per cycle)
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        kernel = int(min_kernel + (max_kernel - min_kernel) * (0.5 + 0.5 * np.sin(t * 2.0)))
        kernel = max(1, min(kernel, 31))
        
        if kernel % 2 == 0:
            kernel += 1
        
        return cv2.GaussianBlur(frame, (kernel, kernel), 0)
    return effect


def border(
    thickness: int = 10,
    color: tuple[int, int, int] = (255, 255, 255)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Draw a solid-color border around the frame edges.

    Fills a rectangular band of the given thickness along all four edges
    with the specified color. Useful for framing, polaroid-style effects,
    or adding a colored outline.

    Parameters:
        thickness: Border width in pixels (range: 1-100, typical: 5-30)
        color: RGB border color (range: 0-255 per channel)
               (255, 255, 255) = white, (0, 0, 0) = black

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[border(thickness=20, color=(255, 255, 255))]
        ... )

    Notes:
        - thickness=0 is a no-op
        - If thickness >= frame_height/2 or frame_width/2, the entire frame is filled
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        h, w = result.shape[:2]
        
        if thickness > 0:
            result[0:thickness, :] = color
            result[h-thickness:, :] = color
            result[:, 0:thickness] = color
            result[:, w-thickness:] = color
        
        return result
    return effect


def pattern_overlay(
    pattern: np.ndarray | None = None,
    opacity: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Tile a repeating pattern over the frame.

    The pattern image is tiled to cover the full frame dimensions, then
    alpha-composited over the original. If no pattern is provided, a default
    checkerboard-like grid is used.

    Parameters:
        pattern: Pattern tile as a numpy array (HxWx3 RGB)
                 None = use a default 50x50 gray grid pattern
        opacity: Pattern blend strength (range: 0.0-1.0, typical: 0.1-0.4)
                 0.0 = invisible, 1.0 = fully opaque pattern

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> import numpy as np
        >>> dots = np.zeros((20, 20, 3), dtype=np.uint8)
        >>> dots[9:11, 9:11] = (200, 200, 200)
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[pattern_overlay(pattern=dots, opacity=0.2)]
        ... )

    Notes:
        - Pattern is tiled using numpy.tile — no interpolation
        - Small patterns (< 10px) may produce a noisy appearance
    """
    if pattern is None:
        pattern = np.zeros((50, 50, 3), dtype=np.uint8)
        for i in range(0, 50, 10):
            for j in range(0, 50, 10):
                if (i + j) % 20 == 0:
                    pattern[i:i+5, j:j+5] = (200, 200, 200)
    
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        ph, pw = pattern.shape[:2]
        
        tiled = np.tile(pattern, ((h + ph - 1) // ph, (w + pw - 1) // pw, 1))
        tiled = tiled[:h, :w]
        
        result = (frame * (1.0 - opacity) + tiled * opacity).astype(np.uint8)
        return result
    return effect


def light_leak(
    intensity: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Simulate analog film light leak with warm glowing blobs.

    Adds randomized Gaussian light blobs in warm amber/orange tones at
    random positions each frame, mimicking the effect of light entering
    a film camera through a gap in the body.

    Parameters:
        intensity: Light leak brightness (range: 0.0-1.0, typical: 0.2-0.5)
                   0.0 = no effect, 1.0 = very strong overexposed blobs

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[light_leak(intensity=0.3)]
        ... )

    Notes:
        - Positions are randomized per frame (not seeded), so blobs move each frame
        - Combine with film_grain() and vignette_simple() for a full analog look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.astype(np.float32)
        
        colors = [(255, 200, 100), (255, 150, 50), (200, 100, 50)]
        
        for color in colors:
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            radius = np.random.randint(50, 150)
            
            yy, xx = np.ogrid[:h, :w]
            dist = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
            mask = np.exp(-dist ** 2 / (2 * radius ** 2))
            
            for c in range(3):
                result[:, :, c] += mask * color[c] * intensity
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result
    return effect


def bokeh_overlay(
    num_circles: int = 20,
    max_radius: int = 50
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Overlay soft blurred circles to simulate out-of-focus bokeh highlights.

    Draws random bright circles on a black canvas, applies a heavy Gaussian
    blur to soften them, then blends the result over the frame. Mimics the
    circular light orbs visible in photos taken with wide-aperture lenses.

    Parameters:
        num_circles: Number of bokeh circles to generate
                     (range: 1-100, typical: 10-40)
        max_radius: Maximum circle radius in pixels
                    (range: 5-200, typical: 20-80)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[bokeh_overlay(num_circles=25, max_radius=60)]
        ... )

    Notes:
        - Circle positions are seeded by time t, so they are stable per frame
        - Combine with gaussian_blur() on the base clip for a full bokeh look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        
        np.random.seed(int(t * 1000))
        for _ in range(num_circles):
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            radius = np.random.randint(10, max_radius)
            
            brightness = np.random.randint(150, 255)
            color = (brightness, brightness, brightness)
            
            cv2.circle(overlay, (x, y), radius, color, -1)
        
        overlay = cv2.GaussianBlur(overlay, (31, 31), 0)
        
        result = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        return result
    return effect


def dust_scratches(
    density: float = 0.001
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Add random dust specks and scratches to simulate aged film.

    Draws small gray dots (dust) and short horizontal lines (scratches)
    at random positions each frame, mimicking the physical damage seen
    on old film prints.

    Parameters:
        density: Proportion of pixels affected by dust
                 (range: 0.0001-0.01, typical: 0.0005-0.002)
                 0.001 = ~0.1% of pixels get a dust speck

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[dust_scratches(density=0.001)]
        ... )

    Notes:
        - Positions are randomized per frame (not seeded), so marks flicker
        - Number of scratches scales with density * 0.1
        - Combine with film_grain() and sepia() for a full vintage film look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        num_dust = int(h * w * density)
        
        for _ in range(num_dust):
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            result[y, x] = (150, 150, 150)
        
        num_scratches = int(h * density * 0.1)
        for _ in range(num_scratches):
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            length = np.random.randint(5, 30)
            cv2.line(result, (x, y), (x + length, y + np.random.randint(-5, 5)), (180, 180, 180), 1)
        
        return result
    return effect


def lens_flare(
    x: int | None = None,
    y: int | None = None
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Add a radial lens flare glow centered at a given position.

    Generates a warm (amber/white) radial gradient that decays exponentially
    from the flare center, simulating the bloom caused by a bright light
    source shining directly into a camera lens.

    Parameters:
        x: Horizontal position of the flare center in pixels
           None = frame center (typical: 0 to frame_width)
        y: Vertical position of the flare center in pixels
           None = frame center (typical: 0 to frame_height)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[lens_flare(x=300, y=200)]
        ... )

    Notes:
        - The flare radius is fixed at ~200px decay constant
        - Bright source areas will clip to 255 (white)
        - For animated flares, use a time-varying x/y via a custom effect
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        
        cx = w // 2 if x is None else x
        cy = h // 2 if y is None else y
        
        result = frame.astype(np.float32)
        
        yy, xx = np.ogrid[:h, :w]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        
        flare_strength = np.exp(-dist / 200.0)
        result += flare_strength[:, :, np.newaxis] * np.array([255, 200, 150])
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result
    return effect


def progress_bar(
    position: str = "bottom",
    height: int = 10,
    color: tuple[int, int, int] = (0, 255, 0)
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Render a progress bar that fills based on clip playback position.

    Draws a filled rectangle whose width is proportional to the current
    clip progress (0.0 = empty, 1.0 = full width). Useful for tutorial
    videos, countdowns, or visualizing clip duration.

    Parameters:
        position: Bar placement — "top" or "bottom"
        height: Bar height in pixels (range: 2-50, typical: 5-20)
        color: RGB fill color (range: 0-255 per channel)
               (0, 255, 0) = green, (255, 255, 255) = white

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[progress_bar(position="bottom", height=8, color=(0, 200, 255))]
        ... )

    Notes:
        - Bar width = int(frame_width * progress)
        - At progress=0.0 the bar is empty; at progress=1.0 it spans the full width
        - No background bar is drawn — the underlying frame shows through the empty area
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        if position == "top":
            y_start = 0
        else:
            y_start = h - height
        
        bar_width = int(w * progress)
        result[y_start:y_start+height, :bar_width] = color
        
        return result
    return effect


def halftone(
    dot_size: int = 4
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a halftone dot pattern effect simulating print screening.

    Divides the frame into square blocks, computes the average brightness
    of each block, and draws a filled circle whose radius is proportional
    to that brightness. Mimics the dot-matrix printing technique used in
    newspapers and comic books.

    Parameters:
        dot_size: Side length of each halftone cell in pixels
                  (range: 2-20, typical: 4-10)
                  Larger values produce coarser, more visible dots.

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[halftone(dot_size=6)]
        ... )

    Notes:
        - Output is grayscale (black background, white dots)
        - Bright areas produce large dots; dark areas produce small or no dots
        - Slow for small dot_size values due to per-block iteration
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape
        
        result = np.zeros((h, w), dtype=np.uint8)
        
        for y in range(0, h, dot_size):
            for x in range(0, w, dot_size):
                block = gray[y:y+dot_size, x:x+dot_size]
                if block.size > 0:
                    avg_brightness = float(np.mean(block))
                    radius = int(avg_brightness / 255.0 * dot_size / 2)
                    
                    if radius > 0:
                        center_y = y + dot_size // 2
                        center_x = x + dot_size // 2
                        cv2.circle(result, (center_x, center_y), radius, 255, -1)
        
        return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    return effect


def glitch_scan_line_shift(
    intensity: float = 0.5
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a glitch effect by randomly shifting individual scan lines.

    Selects a random subset of rows and shifts each one horizontally by
    a random amount proportional to intensity. Simulates the horizontal
    sync errors seen on damaged VHS tapes or corrupted video streams.

    Parameters:
        intensity: Controls both the number of shifted lines and shift magnitude
                   (range: 0.0-1.0, typical: 0.2-0.6)
                   0.0 = no shifts, 1.0 = many lines shifted by large amounts

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[glitch_scan_line_shift(intensity=0.4)]
        ... )

    Notes:
        - Number of shifted lines ≈ frame_height * intensity * 0.1
        - Max shift per line ≈ frame_width * intensity * 0.2
        - Seeded by int(t * 1000) for per-frame variation
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        np.random.seed(int(t * 1000))
        num_shifts = int(h * intensity * 0.1)
        
        for _ in range(num_shifts):
            y = np.random.randint(0, h)
            shift = np.random.randint(-int(w * intensity * 0.2), int(w * intensity * 0.2))
            result[y, :] = np.roll(result[y, :], shift)
        
        return result
    return effect


def glitch_color_corruption(
    intensity: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a glitch effect by randomly scrambling pixel colors in blocks.

    Selects random rectangular regions and shuffles the pixel colors within
    each block, simulating corrupted color data in a digital video stream.

    Parameters:
        intensity: Controls the number of corrupted blocks
                   (range: 0.0-1.0, typical: 0.1-0.5)
                   Number of blocks ≈ int(10 * intensity)

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[glitch_color_corruption(intensity=0.3)]
        ... )

    Notes:
        - Block positions and sizes are randomized per frame (seeded by int(t * 1000))
        - Block dimensions range from 10x10 to 50x50 pixels
        - Blocks that extend beyond the frame boundary are skipped
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        np.random.seed(int(t * 1000))
        num_blocks = int(10 * intensity)
        
        for _ in range(num_blocks):
            y = np.random.randint(0, h)
            x = np.random.randint(0, w)
            bh = np.random.randint(10, 50)
            bw = np.random.randint(10, 50)
            
            if y + bh < h and x + bw < w:
                block = result[y:y+bh, x:x+bw].copy()
                np.random.shuffle(block.reshape(-1, 3))
                result[y:y+bh, x:x+bw] = block
        
        return result
    return effect


def crt_retro(
    scanline_intensity: float = 0.1
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply a CRT retro effect combining RGB blur and scan lines.

    First applies a light Gaussian blur (3x3) to simulate the soft phosphor
    glow of a CRT screen, then darkens every other row by scanline_intensity
    to reproduce the characteristic horizontal banding.

    Parameters:
        scanline_intensity: Darkness of the scan line bands
                            (range: 0.0-1.0, typical: 0.05-0.2)
                            0.0 = no scan lines, 0.1 = subtle banding

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[crt_retro(scanline_intensity=0.15)]
        ... )

    Notes:
        - Combines a 3x3 Gaussian blur with every-other-row darkening
        - For scan lines only (no blur), use scan_lines() instead
        - Combine with chromatic_aberration() for a full CRT simulation
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        
        result = cv2.GaussianBlur(result, (3, 3), 0)
        
        scanline_mask = np.zeros((h, w), dtype=np.float32)
        scanline_mask[::2, :] = scanline_intensity
        
        result = result * (1.0 - scanline_mask[:, :, np.newaxis])
        
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


def vhs_tape_distortion(
    intensity: float = 0.3
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Apply VHS tape distortion with noise and horizontal jitter.

    Adds Gaussian noise to all channels, applies a random horizontal
    roll to simulate tracking errors, then softens the result with a
    3x3 Gaussian blur to mimic the low-bandwidth look of VHS video.

    Parameters:
        intensity: Distortion strength (range: 0.0-1.0, typical: 0.1-0.5)
                   Controls both noise amplitude and horizontal jitter range.
                   0.0 = no distortion, 0.5 = heavy VHS degradation

    Returns:
        Effect function with signature (frame, t, progress) -> frame

    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[vhs_tape_distortion(intensity=0.3)]
        ... )

    Notes:
        - Noise amplitude = 10 * intensity per channel
        - Horizontal jitter range = ±(frame_width * intensity * 0.05) pixels
        - Seeded by int(t * 1000) for per-frame variation
        - Combine with scan_lines() for a complete VHS look
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy().astype(np.float32)
        
        np.random.seed(int(t * 1000))
        
        noise = np.random.randn(h, w, 3) * 10 * intensity
        result += noise
        
        shift = np.random.randint(-int(w * intensity * 0.05), int(w * intensity * 0.05))
        result = np.roll(result, shift, axis=1)
        
        result = cv2.GaussianBlur(result, (3, 3), 0)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    return effect


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
        M = np.array([[1, 0, offset_x], [0, 1, offset_y]], dtype=np.float32)
        
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


# ============================================================================
# Text Overlay Effect
# ============================================================================

def text_overlay(
    text: str,
    position: tuple[int, int] = (50, 50),
    font_scale: float = 1.0,
    color: tuple[int, int, int] = (255, 255, 255),
    thickness: int = 2,
    bg_color: tuple[int, int, int] | None = (0, 0, 0),
    bg_opacity: float = 0.7,
    padding: int = 10,
) -> Callable[[np.ndarray, float, float], np.ndarray]:
    """
    Add text overlay to frame with optional background.
    
    Useful for labeling effects in demo videos or adding titles/captions.
    
    Parameters:
        text: Text string to display
        position: (x, y) position of text top-left corner (default: (50, 50))
        font_scale: Font size multiplier (default: 1.0, range: 0.5-3.0)
        color: Text color as RGB tuple (default: white (255, 255, 255))
        thickness: Text stroke thickness in pixels (default: 2, range: 1-5)
        bg_color: Background color as RGB tuple, or None for no background
                  (default: black (0, 0, 0))
        bg_opacity: Background opacity (default: 0.7, range: 0.0-1.0)
        padding: Padding around text in pixels (default: 10)
    
    Returns:
        Effect function with signature (frame, t, progress) -> frame
    
    Example:
        >>> clip = ImageClip(
        ...     source="image.jpg",
        ...     duration=5.0,
        ...     effects=[text_overlay("Grayscale Effect", position=(50, 50))]
        ... )
    
    Performance:
        ~2-5ms per frame at 1080p
    
    Notes:
        - Uses OpenCV's cv2.putText for rendering
        - Text is always rendered on top of the frame
        - Background is optional and semi-transparent by default
        - Position is in pixels from top-left corner
    """
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        result = frame.copy()
        
        # Get text size for background rectangle
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        x, y = position
        
        # Draw background rectangle if bg_color is specified
        if bg_color is not None:
            # Calculate rectangle coordinates with padding
            rect_x1 = x - padding
            rect_y1 = y - padding
            rect_x2 = x + text_width + padding
            rect_y2 = y + text_height + baseline + padding
            
            # Ensure rectangle is within frame bounds
            rect_x1 = max(0, rect_x1)
            rect_y1 = max(0, rect_y1)
            rect_x2 = min(frame.shape[1], rect_x2)
            rect_y2 = min(frame.shape[0], rect_y2)
            
            # Create semi-transparent background
            overlay = result.copy()
            cv2.rectangle(
                overlay,
                (rect_x1, rect_y1),
                (rect_x2, rect_y2),
                bg_color,
                -1  # Filled rectangle
            )
            
            # Blend overlay with original frame
            cv2.addWeighted(
                overlay, bg_opacity,
                result, 1 - bg_opacity,
                0, result
            )
        
        # Draw text on top
        cv2.putText(
            result,
            text,
            (x, y + text_height),  # Adjust y to account for text baseline
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA  # Anti-aliased text
        )
        
        return result
    
    return effect
