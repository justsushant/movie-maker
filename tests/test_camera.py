"""Property-based and unit tests for virtual camera system."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.camera import Rect, VirtualCamera
from engine.easing import (
    ease_in_cubic,
    ease_in_out_cubic,
    ease_out_cubic,
    linear,
)


# Property-Based Tests


# Feature: video-engine-phase-1, Property 9: Viewport Clamping Safety
# Validates: Requirements 10.1
@settings(max_examples=100)
@given(
    # Generate viewport rectangle with potentially invalid coordinates
    viewport_x=st.floats(min_value=-1000.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    viewport_y=st.floats(min_value=-1000.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    viewport_width=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    viewport_height=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    # Generate image dimensions
    image_width=st.integers(min_value=100, max_value=4000),
    image_height=st.integers(min_value=100, max_value=4000),
)
def test_viewport_clamping_safety(
    viewport_x: float,
    viewport_y: float,
    viewport_width: float,
    viewport_height: float,
    image_width: int,
    image_height: int,
) -> None:
    """
    Property: For any viewport rectangle and source image dimensions, clamping the
    viewport should produce a rectangle where:
    - x >= 0 and x + width <= image_width
    - y >= 0 and y + height <= image_height
    - width > 0 and height > 0
    
    **Validates: Requirements 10.1**
    """
    # Create viewport rectangle (potentially with invalid coordinates)
    viewport = Rect(x=viewport_x, y=viewport_y, width=viewport_width, height=viewport_height)
    
    # Clamp to image boundaries
    clamped = viewport.clamp_to(image_width, image_height)
    
    # Verify x coordinate is within bounds
    assert clamped.x >= 0, (
        f"Clamped x={clamped.x} is negative. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )
    
    # Verify y coordinate is within bounds
    assert clamped.y >= 0, (
        f"Clamped y={clamped.y} is negative. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )
    
    # Verify width is positive
    assert clamped.width > 0, (
        f"Clamped width={clamped.width} is not positive. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )
    
    # Verify height is positive
    assert clamped.height > 0, (
        f"Clamped height={clamped.height} is not positive. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )
    
    # Verify right edge doesn't exceed image width
    assert clamped.x + clamped.width <= image_width, (
        f"Clamped rectangle extends beyond image width: "
        f"x + width = {clamped.x} + {clamped.width} = {clamped.x + clamped.width} > {image_width}. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )
    
    # Verify bottom edge doesn't exceed image height
    assert clamped.y + clamped.height <= image_height, (
        f"Clamped rectangle extends beyond image height: "
        f"y + height = {clamped.y} + {clamped.height} = {clamped.y + clamped.height} > {image_height}. "
        f"Original viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Image: {image_width}x{image_height}"
    )


# Feature: video-engine-phase-1, Property 8: Camera Transform Output Dimensions
# Validates: Requirements 3.2, 3.3, 6.6
@settings(max_examples=100)
@given(
    # Generate source image dimensions
    source_width=st.integers(min_value=100, max_value=4000),
    source_height=st.integers(min_value=100, max_value=4000),
    # Generate viewport rectangle
    viewport_x=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    viewport_y=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    viewport_width=st.floats(min_value=10.0, max_value=2000.0, allow_nan=False, allow_infinity=False),
    viewport_height=st.floats(min_value=10.0, max_value=2000.0, allow_nan=False, allow_infinity=False),
    # Generate output resolution
    output_width=st.integers(min_value=100, max_value=4000),
    output_height=st.integers(min_value=100, max_value=4000),
)
def test_camera_transform_output_dimensions(
    source_width: int,
    source_height: int,
    viewport_x: float,
    viewport_y: float,
    viewport_width: float,
    viewport_height: float,
    output_width: int,
    output_height: int,
) -> None:
    """
    Property: For any source image, viewport rectangle, and output resolution,
    applying the camera transform should produce a numpy array with shape
    (output_height, output_width, 3).
    
    **Validates: Requirements 3.2, 3.3, 6.6**
    """
    import numpy as np
    
    # Create a source image with random pixel values
    source_image = np.random.randint(0, 256, (source_height, source_width, 3), dtype=np.uint8)
    
    # Create viewport rectangle
    viewport = Rect(x=viewport_x, y=viewport_y, width=viewport_width, height=viewport_height)
    
    # Create camera and apply transform
    camera = VirtualCamera(viewport)
    output_size = (output_width, output_height)
    result = camera.apply_transform(source_image, output_size)
    
    # Verify output dimensions
    assert result.shape == (output_height, output_width, 3), (
        f"Camera transform produced incorrect shape: {result.shape}, "
        f"expected ({output_height}, {output_width}, 3). "
        f"Source: {source_width}x{source_height}, "
        f"Viewport: ({viewport_x}, {viewport_y}, {viewport_width}, {viewport_height}), "
        f"Output: {output_width}x{output_height}"
    )
    
    # Verify output is a numpy array with correct dtype
    assert isinstance(result, np.ndarray), "Result should be a numpy array"
    assert result.dtype == np.uint8, f"Result dtype should be uint8, got {result.dtype}"


# Feature: video-engine-phase-1, Property 3: Rectangle Interpolation Correctness
# Validates: Requirements 3.5
@settings(max_examples=100)
@given(
    # Generate two arbitrary rectangles
    start_x=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    start_y=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    start_width=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    start_height=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    end_x=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    end_y=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    end_width=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    end_height=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    # Generate progress value
    progress=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    # Generate easing function
    easing_fn=st.sampled_from([linear, ease_in_cubic, ease_out_cubic, ease_in_out_cubic]),
)
def test_rectangle_interpolation_correctness(
    start_x: float,
    start_y: float,
    start_width: float,
    start_height: float,
    end_x: float,
    end_y: float,
    end_width: float,
    end_height: float,
    progress: float,
    easing_fn,
) -> None:
    """
    Property: For any two rectangles (start and end), any progress value t in [0.0, 1.0],
    and any easing function, interpolating between them should produce a rectangle where
    each component (x, y, width, height) equals:
        start_component + (end_component - start_component) * easing(t)
    
    **Validates: Requirements 3.5**
    """
    rect_start = Rect(x=start_x, y=start_y, width=start_width, height=start_height)
    rect_end = Rect(x=end_x, y=end_y, width=end_width, height=end_height)
    
    # Perform interpolation
    result = VirtualCamera.interpolate(rect_start, rect_end, progress, easing_fn)
    
    # Compute expected values
    t = easing_fn(progress)
    expected_x = start_x + (end_x - start_x) * t
    expected_y = start_y + (end_y - start_y) * t
    expected_width = start_width + (end_width - start_width) * t
    expected_height = start_height + (end_height - start_height) * t
    
    # Verify each component
    tolerance = 1e-9
    assert abs(result.x - expected_x) < tolerance, (
        f"Interpolated x={result.x} does not match expected {expected_x} "
        f"(start={start_x}, end={end_x}, progress={progress}, easing={easing_fn.__name__})"
    )
    assert abs(result.y - expected_y) < tolerance, (
        f"Interpolated y={result.y} does not match expected {expected_y} "
        f"(start={start_y}, end={end_y}, progress={progress}, easing={easing_fn.__name__})"
    )
    assert abs(result.width - expected_width) < tolerance, (
        f"Interpolated width={result.width} does not match expected {expected_width} "
        f"(start={start_width}, end={end_width}, progress={progress}, easing={easing_fn.__name__})"
    )
    assert abs(result.height - expected_height) < tolerance, (
        f"Interpolated height={result.height} does not match expected {expected_height} "
        f"(start={start_height}, end={end_height}, progress={progress}, easing={easing_fn.__name__})"
    )


# Unit Tests


class TestRectangleInterpolationBoundaries:
    """Test rectangle interpolation at boundary values (t=0, t=1).
    
    **Validates: Requirements 3.5**
    """
    
    def test_interpolation_at_zero_returns_start_rect(self) -> None:
        """Interpolation at t=0 should return the start rectangle."""
        start = Rect(x=10.0, y=20.0, width=100.0, height=200.0)
        end = Rect(x=50.0, y=80.0, width=300.0, height=400.0)
        
        result = VirtualCamera.interpolate(start, end, 0.0, linear)
        
        assert result.x == start.x
        assert result.y == start.y
        assert result.width == start.width
        assert result.height == start.height
    
    def test_interpolation_at_one_returns_end_rect(self) -> None:
        """Interpolation at t=1 should return the end rectangle."""
        start = Rect(x=10.0, y=20.0, width=100.0, height=200.0)
        end = Rect(x=50.0, y=80.0, width=300.0, height=400.0)
        
        result = VirtualCamera.interpolate(start, end, 1.0, linear)
        
        assert result.x == end.x
        assert result.y == end.y
        assert result.width == end.width
        assert result.height == end.height


class TestRectangleInterpolationMidpoint:
    """Test rectangle interpolation at midpoint (t=0.5) with linear easing.
    
    **Validates: Requirements 3.5**
    """
    
    def test_interpolation_at_midpoint_with_linear(self) -> None:
        """Interpolation at t=0.5 with linear easing should return midpoint values."""
        start = Rect(x=0.0, y=0.0, width=100.0, height=200.0)
        end = Rect(x=100.0, y=200.0, width=300.0, height=400.0)
        
        result = VirtualCamera.interpolate(start, end, 0.5, linear)
        
        # At t=0.5 with linear easing, should be exactly halfway
        assert result.x == 50.0
        assert result.y == 100.0
        assert result.width == 200.0
        assert result.height == 300.0


class TestRectangleInterpolationWithDifferentEasings:
    """Test rectangle interpolation with different easing functions.
    
    **Validates: Requirements 3.5**
    """
    
    def test_interpolation_with_ease_in_cubic(self) -> None:
        """Interpolation with ease_in_cubic should apply cubic easing to all components."""
        start = Rect(x=0.0, y=0.0, width=100.0, height=100.0)
        end = Rect(x=100.0, y=100.0, width=200.0, height=200.0)
        
        progress = 0.5
        result = VirtualCamera.interpolate(start, end, progress, ease_in_cubic)
        
        # ease_in_cubic(0.5) = 0.5^3 = 0.125
        t = 0.125
        expected_x = 0.0 + (100.0 - 0.0) * t
        expected_y = 0.0 + (100.0 - 0.0) * t
        expected_width = 100.0 + (200.0 - 100.0) * t
        expected_height = 100.0 + (200.0 - 100.0) * t
        
        assert abs(result.x - expected_x) < 1e-9
        assert abs(result.y - expected_y) < 1e-9
        assert abs(result.width - expected_width) < 1e-9
        assert abs(result.height - expected_height) < 1e-9
    
    def test_interpolation_with_ease_out_cubic(self) -> None:
        """Interpolation with ease_out_cubic should apply cubic easing to all components."""
        start = Rect(x=0.0, y=0.0, width=100.0, height=100.0)
        end = Rect(x=100.0, y=100.0, width=200.0, height=200.0)
        
        progress = 0.5
        result = VirtualCamera.interpolate(start, end, progress, ease_out_cubic)
        
        # ease_out_cubic(0.5) = 1 - 0.5^3 = 0.875
        t = 0.875
        expected_x = 0.0 + (100.0 - 0.0) * t
        expected_y = 0.0 + (100.0 - 0.0) * t
        expected_width = 100.0 + (200.0 - 100.0) * t
        expected_height = 100.0 + (200.0 - 100.0) * t
        
        assert abs(result.x - expected_x) < 1e-9
        assert abs(result.y - expected_y) < 1e-9
        assert abs(result.width - expected_width) < 1e-9
        assert abs(result.height - expected_height) < 1e-9
    
    def test_interpolation_with_ease_in_out_cubic(self) -> None:
        """Interpolation with ease_in_out_cubic should apply cubic easing to all components."""
        start = Rect(x=0.0, y=0.0, width=100.0, height=100.0)
        end = Rect(x=100.0, y=100.0, width=200.0, height=200.0)
        
        progress = 0.5
        result = VirtualCamera.interpolate(start, end, progress, ease_in_out_cubic)
        
        # ease_in_out_cubic(0.5) = 4 * 0.5^3 = 0.5
        t = 0.5
        expected_x = 0.0 + (100.0 - 0.0) * t
        expected_y = 0.0 + (100.0 - 0.0) * t
        expected_width = 100.0 + (200.0 - 100.0) * t
        expected_height = 100.0 + (200.0 - 100.0) * t
        
        assert abs(result.x - expected_x) < 1e-9
        assert abs(result.y - expected_y) < 1e-9
        assert abs(result.width - expected_width) < 1e-9
        assert abs(result.height - expected_height) < 1e-9


class TestRectangleInterpolationEdgeCases:
    """Test rectangle interpolation edge cases.
    
    **Validates: Requirements 3.5**
    """
    
    def test_interpolation_with_identical_rectangles(self) -> None:
        """Interpolation between identical rectangles should return the same rectangle."""
        rect = Rect(x=50.0, y=50.0, width=100.0, height=100.0)
        
        for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = VirtualCamera.interpolate(rect, rect, progress, linear)
            assert result.x == rect.x
            assert result.y == rect.y
            assert result.width == rect.width
            assert result.height == rect.height
    
    def test_interpolation_with_negative_to_positive_coordinates(self) -> None:
        """Interpolation should work with negative start coordinates."""
        start = Rect(x=-50.0, y=-50.0, width=100.0, height=100.0)
        end = Rect(x=50.0, y=50.0, width=200.0, height=200.0)
        
        result = VirtualCamera.interpolate(start, end, 0.5, linear)
        
        assert result.x == 0.0
        assert result.y == 0.0
        assert result.width == 150.0
        assert result.height == 150.0
    
    def test_interpolation_with_shrinking_rectangle(self) -> None:
        """Interpolation should handle rectangles that shrink."""
        start = Rect(x=0.0, y=0.0, width=1000.0, height=1000.0)
        end = Rect(x=250.0, y=250.0, width=500.0, height=500.0)
        
        result = VirtualCamera.interpolate(start, end, 0.5, linear)
        
        # Midpoint should be halfway between start and end
        assert result.x == 125.0
        assert result.y == 125.0
        assert result.width == 750.0
        assert result.height == 750.0
    
    def test_interpolation_with_growing_rectangle(self) -> None:
        """Interpolation should handle rectangles that grow."""
        start = Rect(x=250.0, y=250.0, width=500.0, height=500.0)
        end = Rect(x=0.0, y=0.0, width=1000.0, height=1000.0)
        
        result = VirtualCamera.interpolate(start, end, 0.5, linear)
        
        # Midpoint should be halfway between start and end
        assert result.x == 125.0
        assert result.y == 125.0
        assert result.width == 750.0
        assert result.height == 750.0


class TestVirtualCameraCreation:
    """Test VirtualCamera initialization.
    
    **Validates: Requirements 3.1**
    """
    
    def test_camera_creation_with_viewport(self) -> None:
        """VirtualCamera should store the provided viewport rectangle."""
        viewport = Rect(x=10.0, y=20.0, width=100.0, height=200.0)
        camera = VirtualCamera(viewport)
        
        assert camera.viewport == viewport
        assert camera.viewport.x == 10.0
        assert camera.viewport.y == 20.0
        assert camera.viewport.width == 100.0
        assert camera.viewport.height == 200.0
    
    def test_camera_creation_with_zero_origin(self) -> None:
        """VirtualCamera should work with viewport at origin."""
        viewport = Rect(x=0.0, y=0.0, width=1920.0, height=1080.0)
        camera = VirtualCamera(viewport)
        
        assert camera.viewport.x == 0.0
        assert camera.viewport.y == 0.0
        assert camera.viewport.width == 1920.0
        assert camera.viewport.height == 1080.0
    
    def test_camera_creation_with_fractional_coordinates(self) -> None:
        """VirtualCamera should handle fractional viewport coordinates."""
        viewport = Rect(x=10.5, y=20.75, width=100.25, height=200.5)
        camera = VirtualCamera(viewport)
        
        assert camera.viewport.x == 10.5
        assert camera.viewport.y == 20.75
        assert camera.viewport.width == 100.25
        assert camera.viewport.height == 200.5


class TestRectClamping:
    """Test Rect clamping to image boundaries.
    
    **Validates: Requirements 10.1**
    """
    
    def test_clamp_viewport_within_bounds(self) -> None:
        """Viewport already within bounds should remain unchanged."""
        viewport = Rect(x=100.0, y=100.0, width=500.0, height=500.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        assert clamped.x == 100.0
        assert clamped.y == 100.0
        assert clamped.width == 500.0
        assert clamped.height == 500.0
    
    def test_clamp_viewport_exceeds_right_edge(self) -> None:
        """Viewport extending beyond right edge should be clamped."""
        viewport = Rect(x=1500.0, y=100.0, width=800.0, height=500.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        # x should be adjusted so x + width = 1920
        assert clamped.x == 1120.0  # 1920 - 800
        assert clamped.y == 100.0
        assert clamped.width == 800.0
        assert clamped.height == 500.0
    
    def test_clamp_viewport_exceeds_bottom_edge(self) -> None:
        """Viewport extending beyond bottom edge should be clamped."""
        viewport = Rect(x=100.0, y=800.0, width=500.0, height=600.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        # y should be adjusted so y + height = 1080
        assert clamped.x == 100.0
        assert clamped.y == 480.0  # 1080 - 600
        assert clamped.width == 500.0
        assert clamped.height == 600.0
    
    def test_clamp_viewport_with_negative_coordinates(self) -> None:
        """Viewport with negative coordinates should be clamped to zero."""
        viewport = Rect(x=-50.0, y=-100.0, width=500.0, height=500.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        assert clamped.x == 0.0
        assert clamped.y == 0.0
        assert clamped.width == 500.0
        assert clamped.height == 500.0
    
    def test_clamp_viewport_larger_than_image(self) -> None:
        """Viewport larger than image should be clamped to image size."""
        viewport = Rect(x=0.0, y=0.0, width=3000.0, height=2000.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        assert clamped.x == 0.0
        assert clamped.y == 0.0
        assert clamped.width == 1920.0
        assert clamped.height == 1080.0
    
    def test_clamp_viewport_at_exact_boundaries(self) -> None:
        """Viewport at exact image boundaries should remain unchanged."""
        viewport = Rect(x=0.0, y=0.0, width=1920.0, height=1080.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        assert clamped.x == 0.0
        assert clamped.y == 0.0
        assert clamped.width == 1920.0
        assert clamped.height == 1080.0
    
    def test_clamp_small_viewport_in_large_image(self) -> None:
        """Small viewport in large image should remain unchanged."""
        viewport = Rect(x=1000.0, y=500.0, width=100.0, height=100.0)
        clamped = viewport.clamp_to(3840, 2160)
        
        assert clamped.x == 1000.0
        assert clamped.y == 500.0
        assert clamped.width == 100.0
        assert clamped.height == 100.0
    
    def test_clamp_viewport_exceeds_both_edges(self) -> None:
        """Viewport exceeding both right and bottom edges should be clamped."""
        viewport = Rect(x=1500.0, y=800.0, width=800.0, height=600.0)
        clamped = viewport.clamp_to(1920, 1080)
        
        assert clamped.x == 1120.0  # 1920 - 800
        assert clamped.y == 480.0   # 1080 - 600
        assert clamped.width == 800.0
        assert clamped.height == 600.0


class TestCameraTransform:
    """Test camera transform with different viewport sizes.
    
    **Validates: Requirements 3.2, 3.3, 10.2, 10.3**
    """
    
    def test_transform_with_exact_fit_viewport(self) -> None:
        """Transform with viewport matching output size should not resize."""
        import numpy as np
        
        # Create 1920x1080 source image
        source = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        
        # Viewport covers entire image
        viewport = Rect(x=0.0, y=0.0, width=1920.0, height=1080.0)
        camera = VirtualCamera(viewport)
        
        # Transform to same size
        result = camera.apply_transform(source, (1920, 1080))
        
        assert result.shape == (1080, 1920, 3)
        assert result.dtype == np.uint8
    
    def test_transform_with_smaller_viewport_upscale(self) -> None:
        """Transform with viewport smaller than output should upscale."""
        import numpy as np
        
        # Create 1920x1080 source image
        source = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        
        # Small viewport in center
        viewport = Rect(x=460.0, y=290.0, width=1000.0, height=500.0)
        camera = VirtualCamera(viewport)
        
        # Transform to larger size
        result = camera.apply_transform(source, (1920, 1080))
        
        assert result.shape == (1080, 1920, 3)
        assert result.dtype == np.uint8
    
    def test_transform_with_larger_viewport_downscale(self) -> None:
        """Transform with viewport larger than output should downscale."""
        import numpy as np
        
        # Create 3840x2160 source image (4K)
        source = np.random.randint(0, 256, (2160, 3840, 3), dtype=np.uint8)
        
        # Large viewport
        viewport = Rect(x=0.0, y=0.0, width=3840.0, height=2160.0)
        camera = VirtualCamera(viewport)
        
        # Transform to smaller size (1080p)
        result = camera.apply_transform(source, (1920, 1080))
        
        assert result.shape == (1080, 1920, 3)
        assert result.dtype == np.uint8
    
    def test_transform_with_partial_viewport(self) -> None:
        """Transform should crop to viewport before resizing."""
        import numpy as np
        
        # Create source image with distinct regions
        source = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # Fill top-left quadrant with white
        source[0:540, 0:960] = 255
        
        # Viewport covers only top-left quadrant
        viewport = Rect(x=0.0, y=0.0, width=960.0, height=540.0)
        camera = VirtualCamera(viewport)
        
        # Transform to output size
        result = camera.apply_transform(source, (1920, 1080))
        
        assert result.shape == (1080, 1920, 3)
        # Result should be mostly white (from the white quadrant)
        assert np.mean(result) > 200
    
    def test_transform_with_different_aspect_ratios(self) -> None:
        """Transform should handle different aspect ratios."""
        import numpy as np
        
        # Create 1920x1080 source (16:9)
        source = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        
        # Square viewport
        viewport = Rect(x=420.0, y=0.0, width=1080.0, height=1080.0)
        camera = VirtualCamera(viewport)
        
        # Transform to square output
        result = camera.apply_transform(source, (1080, 1080))
        
        assert result.shape == (1080, 1080, 3)
        assert result.dtype == np.uint8
    
    def test_transform_with_portrait_orientation(self) -> None:
        """Transform should handle portrait orientation."""
        import numpy as np
        
        # Create portrait source (9:16)
        source = np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)
        
        # Portrait viewport
        viewport = Rect(x=0.0, y=0.0, width=1080.0, height=1920.0)
        camera = VirtualCamera(viewport)
        
        # Transform to portrait output
        result = camera.apply_transform(source, (1080, 1920))
        
        assert result.shape == (1920, 1080, 3)
        assert result.dtype == np.uint8
    
    def test_transform_preserves_color_channels(self) -> None:
        """Transform should preserve RGB color channels."""
        import numpy as np
        
        # Create source with specific color pattern
        source = np.zeros((1080, 1920, 3), dtype=np.uint8)
        source[:, :, 0] = 255  # Red channel
        source[:, :, 1] = 128  # Green channel
        source[:, :, 2] = 64   # Blue channel
        
        viewport = Rect(x=0.0, y=0.0, width=1920.0, height=1080.0)
        camera = VirtualCamera(viewport)
        
        result = camera.apply_transform(source, (1920, 1080))
        
        # Check that color channels are preserved (with some tolerance for interpolation)
        assert np.mean(result[:, :, 0]) > 250  # Red
        assert 120 < np.mean(result[:, :, 1]) < 135  # Green
        assert 60 < np.mean(result[:, :, 2]) < 70   # Blue
