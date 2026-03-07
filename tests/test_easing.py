"""Property-based and unit tests for easing functions."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.easing import (
    EasingFunction,
    ease_in_cubic,
    ease_in_out_cubic,
    ease_out_cubic,
    linear,
)


# Property-Based Tests


# Feature: video-engine-phase-1, Property 1: Easing Function Bounds
# Validates: Requirements 2.5
@settings(max_examples=100)
@given(
    easing_fn=st.sampled_from([linear, ease_in_cubic, ease_out_cubic, ease_in_out_cubic]),
    t=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_easing_function_bounds(easing_fn: EasingFunction, t: float) -> None:
    """
    Property: For any easing function and any progress value t in [0.0, 1.0],
    the output value should be in [0.0, 1.0].
    
    **Validates: Requirements 2.5**
    """
    result = easing_fn(t)
    assert 0.0 <= result <= 1.0, (
        f"{easing_fn.__name__}({t}) = {result} is outside bounds [0.0, 1.0]"
    )


# Feature: video-engine-phase-1, Property 2: Easing Function Mathematical Correctness
# Validates: Requirements 2.1, 2.2, 2.3, 2.4
@settings(max_examples=100)
@given(t=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_linear_mathematical_correctness(t: float) -> None:
    """
    Property: For any progress value t in [0.0, 1.0], linear(t) should equal t.
    
    **Validates: Requirements 2.1**
    """
    result = linear(t)
    assert abs(result - t) < 1e-10, (
        f"linear({t}) = {result}, expected {t}"
    )


@settings(max_examples=100)
@given(t=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_ease_in_cubic_mathematical_correctness(t: float) -> None:
    """
    Property: For any progress value t in [0.0, 1.0], ease_in_cubic(t) should equal t³.
    
    **Validates: Requirements 2.2**
    """
    result = ease_in_cubic(t)
    expected = t * t * t
    assert abs(result - expected) < 1e-10, (
        f"ease_in_cubic({t}) = {result}, expected {expected}"
    )


@settings(max_examples=100)
@given(t=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_ease_out_cubic_mathematical_correctness(t: float) -> None:
    """
    Property: For any progress value t in [0.0, 1.0], ease_out_cubic(t) should equal 1 - (1-t)³.
    
    **Validates: Requirements 2.3**
    """
    result = ease_out_cubic(t)
    expected = 1 - pow(1 - t, 3)
    assert abs(result - expected) < 1e-10, (
        f"ease_out_cubic({t}) = {result}, expected {expected}"
    )


@settings(max_examples=100)
@given(t=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_ease_in_out_cubic_mathematical_correctness(t: float) -> None:
    """
    Property: For any progress value t in [0.0, 1.0], ease_in_out_cubic(t) should follow
    the piecewise cubic formula:
    - For t < 0.5: f(t) = 4t³
    - For t >= 0.5: f(t) = 1 - (-2t + 2)³ / 2
    
    **Validates: Requirements 2.4**
    """
    result = ease_in_out_cubic(t)
    
    if t < 0.5:
        expected = 4 * t * t * t
    else:
        expected = 1 - pow(-2 * t + 2, 3) / 2
    
    assert abs(result - expected) < 1e-10, (
        f"ease_in_out_cubic({t}) = {result}, expected {expected}"
    )


# Unit Tests


class TestEasingBoundaryValues:
    """Test boundary values (0.0, 1.0) for each easing function.
    
    **Validates: Requirements 2.6, 2.7**
    """
    
    def test_linear_at_zero(self) -> None:
        """Linear easing at t=0.0 should return 0.0."""
        assert linear(0.0) == 0.0
    
    def test_linear_at_one(self) -> None:
        """Linear easing at t=1.0 should return 1.0."""
        assert linear(1.0) == 1.0
    
    def test_ease_in_cubic_at_zero(self) -> None:
        """Ease-in cubic at t=0.0 should return 0.0."""
        assert ease_in_cubic(0.0) == 0.0
    
    def test_ease_in_cubic_at_one(self) -> None:
        """Ease-in cubic at t=1.0 should return 1.0."""
        assert ease_in_cubic(1.0) == 1.0
    
    def test_ease_out_cubic_at_zero(self) -> None:
        """Ease-out cubic at t=0.0 should return 0.0."""
        assert ease_out_cubic(0.0) == 0.0
    
    def test_ease_out_cubic_at_one(self) -> None:
        """Ease-out cubic at t=1.0 should return 1.0."""
        assert ease_out_cubic(1.0) == 1.0
    
    def test_ease_in_out_cubic_at_zero(self) -> None:
        """Ease-in-out cubic at t=0.0 should return 0.0."""
        assert ease_in_out_cubic(0.0) == 0.0
    
    def test_ease_in_out_cubic_at_one(self) -> None:
        """Ease-in-out cubic at t=1.0 should return 1.0."""
        assert ease_in_out_cubic(1.0) == 1.0


class TestEasingMidpoint:
    """Test midpoint (0.5) for each easing function.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    
    def test_linear_at_midpoint(self) -> None:
        """Linear easing at t=0.5 should return 0.5."""
        assert linear(0.5) == 0.5
    
    def test_ease_in_cubic_at_midpoint(self) -> None:
        """Ease-in cubic at t=0.5 should return 0.125 (0.5³)."""
        result = ease_in_cubic(0.5)
        expected = 0.5 ** 3
        assert abs(result - expected) < 1e-10
    
    def test_ease_out_cubic_at_midpoint(self) -> None:
        """Ease-out cubic at t=0.5 should return 0.875 (1 - 0.5³)."""
        result = ease_out_cubic(0.5)
        expected = 1 - (0.5 ** 3)
        assert abs(result - expected) < 1e-10
    
    def test_ease_in_out_cubic_at_midpoint(self) -> None:
        """Ease-in-out cubic at t=0.5 should return 0.5 (4 * 0.5³)."""
        result = ease_in_out_cubic(0.5)
        expected = 4 * (0.5 ** 3)
        assert abs(result - expected) < 1e-10


class TestLinearBehavior:
    """Test that linear easing returns input unchanged.
    
    **Validates: Requirements 2.1**
    """
    
    def test_linear_returns_input_unchanged(self) -> None:
        """Linear easing should return the input value unchanged for any t."""
        test_values = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
        for t in test_values:
            assert linear(t) == t, f"linear({t}) should equal {t}"


class TestEaseInStartsSlow:
    """Test that ease-in functions start slow (low derivative at t=0).
    
    **Validates: Requirements 2.2**
    """
    
    def test_ease_in_cubic_starts_slow(self) -> None:
        """Ease-in cubic should have a small output near t=0 (starts slow)."""
        # At t=0.1, ease_in_cubic should be much less than linear (0.1)
        result = ease_in_cubic(0.1)
        linear_result = linear(0.1)
        assert result < linear_result, (
            f"ease_in_cubic(0.1) = {result} should be less than linear(0.1) = {linear_result}"
        )
        
        # At t=0.2, ease_in_cubic should still be less than linear
        result = ease_in_cubic(0.2)
        linear_result = linear(0.2)
        assert result < linear_result, (
            f"ease_in_cubic(0.2) = {result} should be less than linear(0.2) = {linear_result}"
        )


class TestEaseOutEndsSlow:
    """Test that ease-out functions end slow (low derivative at t=1).
    
    **Validates: Requirements 2.3**
    """
    
    def test_ease_out_cubic_ends_slow(self) -> None:
        """Ease-out cubic should have a large output near t=1 (ends slow)."""
        # At t=0.9, ease_out_cubic should be much greater than linear (0.9)
        result = ease_out_cubic(0.9)
        linear_result = linear(0.9)
        assert result > linear_result, (
            f"ease_out_cubic(0.9) = {result} should be greater than linear(0.9) = {linear_result}"
        )
        
        # At t=0.8, ease_out_cubic should still be greater than linear
        result = ease_out_cubic(0.8)
        linear_result = linear(0.8)
        assert result > linear_result, (
            f"ease_out_cubic(0.8) = {result} should be greater than linear(0.8) = {linear_result}"
        )
