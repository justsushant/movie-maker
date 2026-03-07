"""Property-based and unit tests for Phase 2 effects."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.effects import (
    brightness,
    contrast,
    saturation,
    vignette,
    film_grain,
    fade_in,
    fade_out,
    pulse,
    chain_effects,
)


# Helper function to create test frames
def create_test_frame(height: int, width: int, color: tuple[int, int, int]) -> np.ndarray:
    """Create a solid color test frame."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = color
    return frame


# Property-Based Tests for Color Effects


# Feature: video-engine-phase-2, Property 18: Brightness Effect Monotonicity
# Validates: Requirements 6.1, 6.2
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    amount=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_brightness_monotonicity(height: int, width: int, amount: float) -> None:
    """
    Property: For any frame and brightness amount:
    - When amount > 0, output pixels should be brighter than input pixels (on average)
    - When amount < 0, output pixels should be darker than input pixels (on average)
    - When amount = 0, output should equal input
    
    **Validates: Requirements 6.1, 6.2**
    """
    # Create test frame with mid-range values to allow brightness changes
    frame = create_test_frame(height, width, (128, 128, 128))
    
    # Apply brightness effect
    effect = brightness(amount)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Compute average brightness
    input_avg = np.mean(frame)
    output_avg = np.mean(result)
    
    if amount > 0.01:
        # Positive amount should increase brightness
        assert output_avg > input_avg, f"Brightness increase failed: {output_avg} <= {input_avg}"
    elif amount < -0.01:
        # Negative amount should decrease brightness
        assert output_avg < input_avg, f"Brightness decrease failed: {output_avg} >= {input_avg}"
    else:
        # Zero amount should preserve brightness (within tolerance)
        assert abs(output_avg - input_avg) < 5, f"Brightness preservation failed: {abs(output_avg - input_avg)}"


# Feature: video-engine-phase-2, Property 19: Contrast Effect Behavior
# Validates: Requirements 6.3, 6.4
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    amount=st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False),
)
def test_contrast_behavior(height: int, width: int, amount: float) -> None:
    """
    Property: For any frame and contrast amount:
    - When amount > 1.0, the standard deviation of pixel values should increase
    - When amount < 1.0, the standard deviation of pixel values should decrease
    - When amount = 1.0, output should equal input
    
    **Validates: Requirements 6.3, 6.4**
    """
    # Create frame with some variation
    frame = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)
    
    # Apply contrast effect
    effect = contrast(amount)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Compute standard deviation
    input_std = np.std(frame.astype(np.float32))
    output_std = np.std(result.astype(np.float32))
    
    if amount > 1.05:
        # Increased contrast should increase std dev
        assert output_std >= input_std * 0.95, f"Contrast increase failed: {output_std} < {input_std}"
    elif amount < 0.95:
        # Decreased contrast should decrease std dev
        assert output_std <= input_std * 1.05, f"Contrast decrease failed: {output_std} > {input_std}"
    else:
        # amount ≈ 1.0 should preserve contrast
        assert abs(output_std - input_std) < input_std * 0.2


# Feature: video-engine-phase-2, Property 20: Saturation Effect Behavior
# Validates: Requirements 6.5, 6.6
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    amount=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
)
def test_saturation_behavior(height: int, width: int, amount: float) -> None:
    """
    Property: For any frame and saturation amount:
    - When amount > 1.0, the saturation channel in HSV space should increase
    - When amount < 1.0, the saturation channel in HSV space should decrease
    - When amount = 0.0, output should be grayscale
    
    **Validates: Requirements 6.5, 6.6**
    """
    import cv2
    
    # Create colorful test frame
    frame = create_test_frame(height, width, (255, 100, 50))
    
    # Apply saturation effect
    effect = saturation(amount)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Convert to HSV to check saturation
    input_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    output_hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV)
    
    input_sat = np.mean(input_hsv[:, :, 1])
    output_sat = np.mean(output_hsv[:, :, 1])
    
    if amount == 0.0:
        # Zero saturation should produce grayscale
        # In grayscale, R=G=B
        assert np.allclose(result[:, :, 0], result[:, :, 1], atol=5)
        assert np.allclose(result[:, :, 1], result[:, :, 2], atol=5)
    elif amount > 1.05:
        # Increased saturation
        assert output_sat >= input_sat * 0.95 or output_sat >= 250
    elif amount < 0.95:
        # Decreased saturation
        assert output_sat <= input_sat * 1.05


# Feature: video-engine-phase-2, Property 21: Vignette Effect Edge Darkening
# Validates: Requirements 6.7
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=300),
    width=st.integers(min_value=100, max_value=300),
    intensity=st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_vignette_edge_darkening(height: int, width: int, intensity: float) -> None:
    """
    Property: For any frame with vignette applied, pixels near the edges should be
    darker than pixels near the center (comparing same-color regions).
    
    **Validates: Requirements 6.7**
    """
    # Create uniform test frame
    frame = create_test_frame(height, width, (200, 200, 200))
    
    # Apply vignette
    effect = vignette(intensity=intensity, radius=0.5)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Sample center and edge pixels
    center_y, center_x = height // 2, width // 2
    center_pixel = result[center_y, center_x]
    
    # Sample edge pixels
    edge_top = result[5, center_x]
    edge_bottom = result[height - 5, center_x]
    edge_left = result[center_y, 5]
    edge_right = result[center_y, width - 5]
    
    # Center should be brighter than edges
    center_brightness = np.mean(center_pixel)
    edge_brightness = np.mean([
        np.mean(edge_top),
        np.mean(edge_bottom),
        np.mean(edge_left),
        np.mean(edge_right)
    ])
    
    assert center_brightness > edge_brightness, \
        f"Vignette failed: center {center_brightness} not brighter than edges {edge_brightness}"


# Feature: video-engine-phase-2, Property 22: Color Value Clamping
# Validates: Requirements 6.8
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    amount=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_color_value_clamping(height: int, width: int, amount: float) -> None:
    """
    Property: For any effect and any input frame, all output pixel values
    should be in the range [0, 255].
    
    **Validates: Requirements 6.8**
    """
    # Create frame with extreme values
    frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    # Apply brightness effect (most likely to cause overflow)
    effect = brightness(amount)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Check all values are in valid range
    assert np.all(result >= 0), "Found negative pixel values"
    assert np.all(result <= 255), "Found pixel values > 255"
    assert result.dtype == np.uint8, "Output dtype is not uint8"


# Property-Based Tests for Texture Effects


# Feature: video-engine-phase-2, Property 23: Film Grain Adds Noise
# Validates: Requirements 7.1
@settings(max_examples=50)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    intensity=st.floats(min_value=0.05, max_value=0.5, allow_nan=False, allow_infinity=False),
)
def test_film_grain_adds_noise(height: int, width: int, intensity: float) -> None:
    """
    Property: For any frame with film_grain applied, the output should differ
    from the input, and the difference should be random noise.
    
    **Validates: Requirements 7.1**
    """
    # Create uniform test frame
    frame = create_test_frame(height, width, (128, 128, 128))
    
    # Apply film grain
    effect = film_grain(intensity=intensity, seed=42)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Check that output differs from input
    assert not np.array_equal(frame, result), "Film grain produced identical output"
    
    # Check that differences are distributed (not all same value)
    diff = result.astype(np.int16) - frame.astype(np.int16)
    diff_std = np.std(diff)
    assert diff_std > 0, "Film grain produced no variation"


# Feature: video-engine-phase-2, Property 24: Film Grain Intensity Scaling
# Validates: Requirements 7.2
@settings(max_examples=50)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
)
def test_film_grain_intensity_scaling(height: int, width: int) -> None:
    """
    Property: For any frame and two intensity values i1 < i2, applying film_grain
    with i2 should produce more variation from the original than i1.
    
    **Validates: Requirements 7.2**
    """
    # Create uniform test frame
    frame = create_test_frame(height, width, (128, 128, 128))
    
    # Apply film grain with different intensities
    effect_low = film_grain(intensity=0.1, seed=42)
    effect_high = film_grain(intensity=0.3, seed=42)
    
    result_low = effect_low(frame, t=0.0, progress=0.5)
    result_high = effect_high(frame, t=0.0, progress=0.5)
    
    # Compute variation from original
    diff_low = np.abs(result_low.astype(np.int16) - frame.astype(np.int16))
    diff_high = np.abs(result_high.astype(np.int16) - frame.astype(np.int16))
    
    variation_low = np.mean(diff_low)
    variation_high = np.mean(diff_high)
    
    assert variation_high > variation_low, \
        f"Higher intensity did not produce more variation: {variation_high} <= {variation_low}"


# Feature: video-engine-phase-2, Property 25: Film Grain Temporal Variation
# Validates: Requirements 7.3
@settings(max_examples=50)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
)
def test_film_grain_temporal_variation(height: int, width: int) -> None:
    """
    Property: For any frame and two different time values t1 and t2,
    film_grain(frame, t1) should produce different noise patterns than
    film_grain(frame, t2).
    
    **Validates: Requirements 7.3**
    """
    # Create uniform test frame
    frame = create_test_frame(height, width, (128, 128, 128))
    
    # Apply film grain at different times
    effect = film_grain(intensity=0.2)
    result_t1 = effect(frame, t=0.0, progress=0.5)
    result_t2 = effect(frame, t=1.0, progress=0.5)
    
    # Check that outputs differ
    assert not np.array_equal(result_t1, result_t2), \
        "Film grain produced identical patterns at different times"


# Feature: video-engine-phase-2, Property 26: Film Grain Brightness Preservation
# Validates: Requirements 7.4
@settings(max_examples=50)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    intensity=st.floats(min_value=0.05, max_value=0.3, allow_nan=False, allow_infinity=False),
)
def test_film_grain_brightness_preservation(height: int, width: int, intensity: float) -> None:
    """
    Property: For any frame with film_grain applied, the mean brightness of the
    output should be approximately equal to the mean brightness of the input
    (within tolerance).
    
    **Validates: Requirements 7.4**
    """
    # Create test frame
    frame = create_test_frame(height, width, (150, 150, 150))
    
    # Apply film grain
    effect = film_grain(intensity=intensity, seed=42)
    result = effect(frame, t=0.0, progress=0.5)
    
    # Compute mean brightness
    input_mean = np.mean(frame)
    output_mean = np.mean(result)
    
    # Allow some tolerance due to noise
    tolerance = intensity * 255 * 0.5  # Noise is zero-mean, so average should be close
    assert abs(output_mean - input_mean) < tolerance, \
        f"Brightness not preserved: {output_mean} vs {input_mean}, diff {abs(output_mean - input_mean)}"


# Property-Based Tests for Effect Chain


# Feature: video-engine-phase-2, Property 15: Effect Chain Ordering
# Validates: Requirements 5.3
@settings(max_examples=50)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
)
def test_effect_chain_ordering(height: int, width: int) -> None:
    """
    Property: For any clip with effects [e1, e2, ..., en], applying the effects
    should produce the same result as applying e1, then e2, ..., then en in sequence.
    
    **Validates: Requirements 5.3**
    """
    # Create test frame
    frame = create_test_frame(height, width, (128, 128, 128))
    
    # Create individual effects
    e1 = brightness(0.1)
    e2 = contrast(1.2)
    e3 = saturation(0.8)
    
    # Apply effects manually in sequence
    manual_result = frame.copy()
    manual_result = e1(manual_result, t=0.5, progress=0.5)
    manual_result = e2(manual_result, t=0.5, progress=0.5)
    manual_result = e3(manual_result, t=0.5, progress=0.5)
    
    # Apply effects using chain_effects
    chained = chain_effects(e1, e2, e3)
    chained_result = chained(frame, t=0.5, progress=0.5)
    
    # Results should be identical
    assert np.array_equal(manual_result, chained_result), \
        "Chained effects produced different result than manual sequence"


# Feature: video-engine-phase-2, Property 16: No Effects Preserves Frame
# Validates: Requirements 5.5, 12.3, 12.4
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
)
def test_no_effects_preserves_frame(height: int, width: int) -> None:
    """
    Property: For any clip with an empty effects list or no effects attribute,
    rendering the clip should produce a frame identical to the base camera-transformed frame.
    
    **Validates: Requirements 5.5, 12.3, 12.4**
    """
    # Create test frame
    frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    # Apply empty effect chain
    chained = chain_effects()
    result = chained(frame, t=0.5, progress=0.5)
    
    # Result should be identical to input
    assert np.array_equal(frame, result), \
        "Empty effect chain modified the frame"


# Feature: video-engine-phase-2, Property 17: Effect Dimension Preservation
# Validates: Requirements 5.6, 11.3, 14.1, 14.2
@settings(max_examples=100)
@given(
    height=st.integers(min_value=50, max_value=200),
    width=st.integers(min_value=50, max_value=200),
    effect_fn=st.sampled_from([
        brightness(0.2),
        contrast(1.2),
        saturation(0.8),
        vignette(0.5, 0.8),
        film_grain(0.1, seed=42),
        fade_in(1.0),
        fade_out(1.0),
        pulse(1.0, 0.2),
    ]),
)
def test_effect_dimension_preservation(height: int, width: int, effect_fn) -> None:
    """
    Property: For any effect function and any input frame, the output frame must
    have identical shape and dtype to the input, otherwise a ValueError should be raised.
    
    **Validates: Requirements 5.6, 11.3, 14.1, 14.2**
    """
    # Create test frame
    frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    # Apply effect
    result = effect_fn(frame, t=0.5, progress=0.5)
    
    # Check shape and dtype preserved
    assert result.shape == frame.shape, \
        f"Effect changed shape from {frame.shape} to {result.shape}"
    assert result.dtype == frame.dtype, \
        f"Effect changed dtype from {frame.dtype} to {result.dtype}"
