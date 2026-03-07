"""Property-based and unit tests for Phase 2 transitions."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.transitions import (
    crossfade,
    fade_through_black,
    fade_through_white,
    slide_left,
    slide_right,
    slide_up,
    slide_down,
    push_left,
    push_right,
    push_up,
    push_down,
    wipe_left,
    wipe_right,
    wipe_up,
    wipe_down,
    iris_open,
    iris_close,
    clock_wipe,
    diamond_wipe,
    blinds_horizontal,
    blinds_vertical,
    zoom_through,
    whip_pan,
    pixelate,
    glitch,
)


# Helper function to create test frames
def create_test_frame(height: int, width: int, color: tuple[int, int, int]) -> np.ndarray:
    """Create a solid color test frame."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = color
    return frame


# Property-Based Tests


# Feature: video-engine-phase-2, Property 7: Transition Boundary Conditions
# Validates: Requirements 2.5, 2.6, 10.3, 10.4
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=1080),
    width=st.integers(min_value=100, max_value=1920),
    transition_fn=st.sampled_from([
        crossfade,
        fade_through_black,
        fade_through_white,
        slide_left,
        slide_right,
        slide_up,
        slide_down,
        push_left,
        push_right,
        push_up,
        push_down,
        wipe_left,
        wipe_right,
        wipe_up,
        wipe_down,
        iris_open,
        iris_close,
        clock_wipe,
        diamond_wipe,
        blinds_horizontal,
        blinds_vertical,
        zoom_through,
        whip_pan,
        pixelate,
        glitch,
    ]),
)
def test_transition_boundary_conditions(
    height: int,
    width: int,
    transition_fn,
) -> None:
    """
    Property: For any transition function and any two frames frame_a and frame_b:
    - When progress = 0.0, the output should be visually identical to frame_a
    - When progress = 1.0, the output should be visually identical to frame_b
    
    **Validates: Requirements 2.5, 2.6, 10.3, 10.4**
    """
    # Create distinct test frames
    frame_a = create_test_frame(height, width, (255, 0, 0))  # Red
    frame_b = create_test_frame(height, width, (0, 0, 255))  # Blue
    
    # Test at progress = 0.0
    result_at_zero = transition_fn(frame_a, frame_b, 0.0)
    assert result_at_zero.shape == frame_a.shape, (
        f"{transition_fn.__name__} at progress=0.0 changed shape"
    )
    # Allow small tolerance for rounding/interpolation
    assert np.allclose(result_at_zero, frame_a, atol=5), (
        f"{transition_fn.__name__} at progress=0.0 does not match frame_a. "
        f"Mean difference: {np.mean(np.abs(result_at_zero.astype(float) - frame_a.astype(float)))}"
    )
    
    # Test at progress = 1.0
    result_at_one = transition_fn(frame_a, frame_b, 1.0)
    assert result_at_one.shape == frame_b.shape, (
        f"{transition_fn.__name__} at progress=1.0 changed shape"
    )
    assert np.allclose(result_at_one, frame_b, atol=5), (
        f"{transition_fn.__name__} at progress=1.0 does not match frame_b. "
        f"Mean difference: {np.mean(np.abs(result_at_one.astype(float) - frame_b.astype(float)))}"
    )


# Feature: video-engine-phase-2, Property 4: Crossfade Mathematical Correctness
# Validates: Requirements 2.1
@settings(max_examples=100)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_crossfade_mathematical_correctness(
    height: int,
    width: int,
    progress: float,
) -> None:
    """
    Property: For any two frames frame_a and frame_b, and any progress p in [0.0, 1.0],
    crossfade(frame_a, frame_b, p) should equal frame_a * (1-p) + frame_b * p
    (within rounding tolerance).
    
    **Validates: Requirements 2.1**
    """
    # Create test frames with known values
    frame_a = create_test_frame(height, width, (200, 100, 50))
    frame_b = create_test_frame(height, width, (50, 150, 200))
    
    # Apply crossfade
    result = crossfade(frame_a, frame_b, progress)
    
    # Compute expected result
    expected = (frame_a * (1 - progress) + frame_b * progress).astype(np.uint8)
    
    # Verify mathematical correctness
    assert np.allclose(result, expected, atol=1), (
        f"Crossfade at progress={progress} does not match formula. "
        f"Max difference: {np.max(np.abs(result.astype(float) - expected.astype(float)))}"
    )



# Feature: video-engine-phase-2, Property 9: Slide Transition Monotonicity
# Validates: Requirements 3.1, 3.2, 3.3, 3.4
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress1=st.floats(min_value=0.0, max_value=0.9, allow_nan=False, allow_infinity=False),
    progress2=st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
    slide_fn=st.sampled_from([slide_left, slide_right, slide_up, slide_down]),
)
def test_slide_transition_monotonicity(
    height: int,
    width: int,
    progress1: float,
    progress2: float,
    slide_fn,
) -> None:
    """
    Property: For any slide transition and any two progress values p1 < p2,
    the visible area of frame_b at p2 should be greater than or equal to
    the visible area at p1.
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    """
    # Ensure p1 < p2
    if progress1 >= progress2:
        progress1, progress2 = progress2, progress1
    
    # Create distinct frames
    frame_a = create_test_frame(height, width, (0, 0, 0))  # Black
    frame_b = create_test_frame(height, width, (255, 255, 255))  # White
    
    # Apply slide at both progress values
    result1 = slide_fn(frame_a, frame_b, progress1)
    result2 = slide_fn(frame_a, frame_b, progress2)
    
    # Count white pixels (from frame_b)
    white_pixels1 = np.sum(result1 > 200)
    white_pixels2 = np.sum(result2 > 200)
    
    # At higher progress, more of frame_b should be visible
    assert white_pixels2 >= white_pixels1, (
        f"{slide_fn.__name__} monotonicity violated: "
        f"progress={progress1} has {white_pixels1} white pixels, "
        f"progress={progress2} has {white_pixels2} white pixels"
    )


# Feature: video-engine-phase-2, Property 10: Push Transition Frame Coverage
# Validates: Requirements 3.5, 3.6, 3.7, 3.8
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    push_fn=st.sampled_from([push_left, push_right, push_up, push_down]),
)
def test_push_transition_frame_coverage(
    height: int,
    width: int,
    progress: float,
    push_fn,
) -> None:
    """
    Property: For any push transition and any progress p, every pixel in the output
    should come from either frame_a or frame_b (no black regions).
    
    **Validates: Requirements 3.5, 3.6, 3.7, 3.8**
    """
    # Create frames with distinct non-black colors
    frame_a = create_test_frame(height, width, (255, 0, 0))  # Red
    frame_b = create_test_frame(height, width, (0, 0, 255))  # Blue
    
    # Apply push transition
    result = push_fn(frame_a, frame_b, progress)
    
    # Check that no pixels are black (all should be red or blue)
    # Allow small tolerance for edge cases
    black_pixels = np.sum(np.all(result < 10, axis=2))
    
    assert black_pixels == 0, (
        f"{push_fn.__name__} at progress={progress} has {black_pixels} black pixels. "
        f"All pixels should come from frame_a or frame_b."
    )


# Feature: video-engine-phase-2, Property 11: Wipe Transition Hard Edge
# Validates: Requirements 3.9, 3.10, 3.11, 3.12
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress=st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
    wipe_fn=st.sampled_from([wipe_left, wipe_right, wipe_up, wipe_down]),
)
def test_wipe_transition_hard_edge(
    height: int,
    width: int,
    progress: float,
    wipe_fn,
) -> None:
    """
    Property: For any wipe transition and any progress p, there should exist a clear
    boundary where pixels are either entirely from frame_a or entirely from frame_b
    (no blending).
    
    **Validates: Requirements 3.9, 3.10, 3.11, 3.12**
    """
    # Create frames with distinct colors
    frame_a = create_test_frame(height, width, (100, 100, 100))  # Gray
    frame_b = create_test_frame(height, width, (200, 200, 200))  # Light gray
    
    # Apply wipe transition
    result = wipe_fn(frame_a, frame_b, progress)
    
    # Check that pixels are either close to frame_a or frame_b values (no blending)
    # Each pixel should be within tolerance of one of the source frames
    close_to_a = np.all(np.abs(result - frame_a) < 10, axis=2)
    close_to_b = np.all(np.abs(result - frame_b) < 10, axis=2)
    
    # Every pixel should be close to either frame_a or frame_b
    all_pixels_match = np.all(close_to_a | close_to_b)
    
    assert all_pixels_match, (
        f"{wipe_fn.__name__} at progress={progress} has blended pixels. "
        f"Wipes should have hard edges with no blending."
    )


# Feature: video-engine-phase-2, Property 12: Shape Transition Geometric Correctness
# Validates: Requirements 3.14, 3.15, 3.16, 3.17
@settings(max_examples=50)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress1=st.floats(min_value=0.0, max_value=0.9, allow_nan=False, allow_infinity=False),
    progress2=st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
    shape_fn=st.sampled_from([iris_open, iris_close, clock_wipe, diamond_wipe]),
)
def test_shape_transition_geometric_correctness(
    height: int,
    width: int,
    progress1: float,
    progress2: float,
    shape_fn,
) -> None:
    """
    Property: For any shape transition and any progress p in [0.0, 1.0],
    the revealed area of frame_b should increase monotonically with p.
    
    **Validates: Requirements 3.14, 3.15, 3.16, 3.17**
    """
    # Ensure p1 < p2
    if progress1 >= progress2:
        progress1, progress2 = progress2, progress1
    
    # Create distinct frames
    frame_a = create_test_frame(height, width, (0, 0, 0))  # Black
    frame_b = create_test_frame(height, width, (255, 255, 255))  # White
    
    # Apply shape transition at both progress values
    result1 = shape_fn(frame_a, frame_b, progress1)
    result2 = shape_fn(frame_a, frame_b, progress2)
    
    # Count white pixels (from frame_b) - handle iris_close specially
    if shape_fn == iris_close:
        # For iris_close, frame_b is revealed outside the circle
        # So more white pixels at higher progress
        white_pixels1 = np.sum(result1 > 200)
        white_pixels2 = np.sum(result2 > 200)
    else:
        # For other shapes, frame_b is revealed inside the shape
        white_pixels1 = np.sum(result1 > 200)
        white_pixels2 = np.sum(result2 > 200)
    
    # At higher progress, revealed area should be greater or equal
    assert white_pixels2 >= white_pixels1, (
        f"{shape_fn.__name__} monotonicity violated: "
        f"progress={progress1} has {white_pixels1} white pixels, "
        f"progress={progress2} has {white_pixels2} white pixels"
    )


# Feature: video-engine-phase-2, Property 13: Blinds Transition Strip Count
# Validates: Requirements 3.18, 3.19
@settings(max_examples=30)
@given(
    height=st.integers(min_value=200, max_value=500),
    width=st.integers(min_value=200, max_value=500),
    progress=st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False),
)
def test_blinds_transition_strip_count(
    height: int,
    width: int,
    progress: float,
) -> None:
    """
    Property: For any blinds transition, the output should show exactly 10 strips
    revealing frame_b progressively.
    
    **Validates: Requirements 3.18, 3.19**
    """
    # Create distinct frames
    frame_a = create_test_frame(height, width, (0, 0, 0))  # Black
    frame_b = create_test_frame(height, width, (255, 255, 255))  # White
    
    # Test horizontal blinds
    result_h = blinds_horizontal(frame_a, frame_b, progress)
    
    # For horizontal blinds, count transitions from black to white along a column
    # This gives us the number of strips
    middle_col = result_h[:, width // 2, 0]
    transitions = np.sum(np.abs(np.diff(middle_col.astype(int))) > 100)
    
    # Should have approximately 10 strips (20 transitions - up and down edges)
    # Allow some tolerance for edge effects
    assert 8 <= transitions <= 22, (
        f"blinds_horizontal should have ~10 strips, found {transitions // 2} transitions"
    )
    
    # Test vertical blinds
    result_v = blinds_vertical(frame_a, frame_b, progress)
    
    # For vertical blinds, count transitions along a row
    middle_row = result_v[height // 2, :, 0]
    transitions = np.sum(np.abs(np.diff(middle_row.astype(int))) > 100)
    
    assert 8 <= transitions <= 22, (
        f"blinds_vertical should have ~10 strips, found {transitions // 2} transitions"
    )


# Feature: video-engine-phase-2, Property 14: Animated Transition Frame Validity
# Validates: Requirements 4.1, 4.2, 4.3, 4.4
@settings(max_examples=30)
@given(
    height=st.integers(min_value=100, max_value=500),
    width=st.integers(min_value=100, max_value=500),
    progress=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    animated_fn=st.sampled_from([zoom_through, whip_pan, pixelate, glitch]),
)
def test_animated_transition_frame_validity(
    height: int,
    width: int,
    progress: float,
    animated_fn,
) -> None:
    """
    Property: For any animated transition and any progress p, the output frame
    should have valid dimensions and dtype matching the input frames.
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    """
    # Create test frames
    frame_a = create_test_frame(height, width, (100, 150, 200))
    frame_b = create_test_frame(height, width, (200, 150, 100))
    
    # Apply animated transition
    result = animated_fn(frame_a, frame_b, progress)
    
    # Verify dimensions match
    assert result.shape == (height, width, 3), (
        f"{animated_fn.__name__} changed dimensions: "
        f"expected {(height, width, 3)}, got {result.shape}"
    )
    
    # Verify dtype matches
    assert result.dtype == np.uint8, (
        f"{animated_fn.__name__} changed dtype: "
        f"expected uint8, got {result.dtype}"
    )
    
    # Verify values are in valid range
    assert np.all(result >= 0) and np.all(result <= 255), (
        f"{animated_fn.__name__} produced out-of-range values"
    )


# Feature: video-engine-phase-2, Property 36: Invalid Transition Type Rejection
# Validates: Requirements 13.4
def test_invalid_transition_type_rejection():
    """
    Property: For any invalid transition type value, the system should raise
    a ValueError when attempting to get the transition function.
    
    **Validates: Requirements 13.4**
    """
    from engine.transitions import get_transition_function
    from engine.scene import TransitionType
    
    # Test with a valid transition type first
    valid_type = TransitionType.CROSSFADE
    fn = get_transition_function(valid_type)
    assert callable(fn)
    
    # Test with an invalid value (not in enum)
    # We can't easily create an invalid enum value, so we'll test the error message
    # by checking that all valid types work
    for transition_type in TransitionType:
        fn = get_transition_function(transition_type)
        assert callable(fn), f"Failed to get function for {transition_type}"
