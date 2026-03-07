"""Property-based and unit tests for motion preset implementations."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.camera import Rect, compute_motion_path
from engine.scene import MotionPreset


# Property-Based Tests


# Feature: video-engine-phase-1, Property 5: Static Motion Invariance
# Validates: Requirements 4.1
@settings(max_examples=100)
@given(
    # Generate image dimensions
    image_width=st.integers(min_value=100, max_value=4000),
    image_height=st.integers(min_value=100, max_value=4000),
    # Generate output dimensions
    output_width=st.integers(min_value=100, max_value=4000),
    output_height=st.integers(min_value=100, max_value=4000),
    # Generate clip duration
    duration=st.floats(min_value=0.1, max_value=60.0, allow_nan=False, allow_infinity=False),
    # Generate two time values within the clip duration
    t1_fraction=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    t2_fraction=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_static_motion_invariance(
    image_width: int,
    image_height: int,
    output_width: int,
    output_height: int,
    duration: float,
    t1_fraction: float,
    t2_fraction: float,
) -> None:
    """
    Property: For any image clip with STATIC motion preset and any two time values
    t1 and t2 within the clip duration, the camera viewport at t1 should equal the
    viewport at t2.
    
    **Validates: Requirements 4.1**
    """
    # Compute motion path for STATIC preset
    camera_path = compute_motion_path(
        preset=MotionPreset.STATIC,
        image_size=(image_width, image_height),
        output_size=(output_width, output_height),
        duration=duration
    )
    
    # Compute two time values within the clip duration
    t1 = t1_fraction * duration
    t2 = t2_fraction * duration
    
    # Get viewport at both times
    viewport_t1 = camera_path(t1)
    viewport_t2 = camera_path(t2)
    
    # Verify that viewports are identical
    tolerance = 1e-9
    assert abs(viewport_t1.x - viewport_t2.x) < tolerance, (
        f"STATIC motion viewport x changed: t1={t1:.3f}s -> x={viewport_t1.x:.3f}, "
        f"t2={t2:.3f}s -> x={viewport_t2.x:.3f}. "
        f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
        f"Duration: {duration:.3f}s"
    )
    
    assert abs(viewport_t1.y - viewport_t2.y) < tolerance, (
        f"STATIC motion viewport y changed: t1={t1:.3f}s -> y={viewport_t1.y:.3f}, "
        f"t2={t2:.3f}s -> y={viewport_t2.y:.3f}. "
        f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
        f"Duration: {duration:.3f}s"
    )
    
    assert abs(viewport_t1.width - viewport_t2.width) < tolerance, (
        f"STATIC motion viewport width changed: t1={t1:.3f}s -> width={viewport_t1.width:.3f}, "
        f"t2={t2:.3f}s -> width={viewport_t2.width:.3f}. "
        f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
        f"Duration: {duration:.3f}s"
    )
    
    assert abs(viewport_t1.height - viewport_t2.height) < tolerance, (
        f"STATIC motion viewport height changed: t1={t1:.3f}s -> height={viewport_t1.height:.3f}, "
        f"t2={t2:.3f}s -> height={viewport_t2.height:.3f}. "
        f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
        f"Duration: {duration:.3f}s"
    )


# Feature: video-engine-phase-1, Property 6: Pan Motion Monotonicity
# Validates: Requirements 4.4, 4.5, 4.6, 4.7
@settings(max_examples=100)
@given(
    # Generate pan preset
    pan_preset=st.sampled_from([
        MotionPreset.PAN_LEFT,
        MotionPreset.PAN_RIGHT,
        MotionPreset.PAN_UP,
        MotionPreset.PAN_DOWN,
    ]),
    # Generate image dimensions (must be larger than output for panning to work)
    image_width=st.integers(min_value=2000, max_value=4000),
    image_height=st.integers(min_value=2000, max_value=4000),
    # Generate output dimensions (smaller than image)
    output_width=st.integers(min_value=1000, max_value=1999),
    output_height=st.integers(min_value=1000, max_value=1999),
    # Generate clip duration
    duration=st.floats(min_value=0.1, max_value=60.0, allow_nan=False, allow_infinity=False),
    # Generate two time fractions where t1 < t2
    t1_fraction=st.floats(min_value=0.0, max_value=0.99, allow_nan=False, allow_infinity=False),
    t2_fraction=st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_pan_motion_monotonicity(
    pan_preset: MotionPreset,
    image_width: int,
    image_height: int,
    output_width: int,
    output_height: int,
    duration: float,
    t1_fraction: float,
    t2_fraction: float,
) -> None:
    """
    Property: For any image clip with a pan motion preset (PAN_LEFT, PAN_RIGHT, PAN_UP, PAN_DOWN)
    and any two time values t1 < t2 within the clip duration:
    - For PAN_LEFT/PAN_RIGHT: viewport x-coordinate should change monotonically
    - For PAN_UP/PAN_DOWN: viewport y-coordinate should change monotonically
    
    **Validates: Requirements 4.4, 4.5, 4.6, 4.7**
    """
    # Ensure t1 < t2
    if t1_fraction >= t2_fraction:
        t1_fraction, t2_fraction = t2_fraction, t1_fraction
    
    # Compute motion path for pan preset
    camera_path = compute_motion_path(
        preset=pan_preset,
        image_size=(image_width, image_height),
        output_size=(output_width, output_height),
        duration=duration
    )
    
    # Compute two time values within the clip duration
    t1 = t1_fraction * duration
    t2 = t2_fraction * duration
    
    # Get viewport at both times
    viewport_t1 = camera_path(t1)
    viewport_t2 = camera_path(t2)
    
    # Verify monotonicity based on pan direction
    tolerance = 1e-9
    
    if pan_preset == MotionPreset.PAN_LEFT:
        # PAN_LEFT: viewport moves right (x increases)
        assert viewport_t2.x >= viewport_t1.x - tolerance, (
            f"PAN_LEFT motion x-coordinate not monotonically increasing: "
            f"t1={t1:.3f}s -> x={viewport_t1.x:.3f}, t2={t2:.3f}s -> x={viewport_t2.x:.3f}. "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )
    
    elif pan_preset == MotionPreset.PAN_RIGHT:
        # PAN_RIGHT: viewport moves left (x decreases)
        assert viewport_t2.x <= viewport_t1.x + tolerance, (
            f"PAN_RIGHT motion x-coordinate not monotonically decreasing: "
            f"t1={t1:.3f}s -> x={viewport_t1.x:.3f}, t2={t2:.3f}s -> x={viewport_t2.x:.3f}. "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )
    
    elif pan_preset == MotionPreset.PAN_UP:
        # PAN_UP: viewport moves down (y increases)
        assert viewport_t2.y >= viewport_t1.y - tolerance, (
            f"PAN_UP motion y-coordinate not monotonically increasing: "
            f"t1={t1:.3f}s -> y={viewport_t1.y:.3f}, t2={t2:.3f}s -> y={viewport_t2.y:.3f}. "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )
    
    elif pan_preset == MotionPreset.PAN_DOWN:
        # PAN_DOWN: viewport moves up (y decreases)
        assert viewport_t2.y <= viewport_t1.y + tolerance, (
            f"PAN_DOWN motion y-coordinate not monotonically decreasing: "
            f"t1={t1:.3f}s -> y={viewport_t1.y:.3f}, t2={t2:.3f}s -> y={viewport_t2.y:.3f}. "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )


# Feature: video-engine-phase-1, Property 7: Zoom Motion Monotonicity
# Validates: Requirements 4.2, 4.3, 4.8, 4.9
@settings(max_examples=100)
@given(
    # Generate zoom preset
    zoom_preset=st.sampled_from([
        MotionPreset.ZOOM_IN,
        MotionPreset.ZOOM_OUT,
        MotionPreset.KEN_BURNS_ZOOM_IN,
        MotionPreset.KEN_BURNS_ZOOM_OUT,
    ]),
    # Generate image dimensions
    image_width=st.integers(min_value=1000, max_value=4000),
    image_height=st.integers(min_value=1000, max_value=4000),
    # Generate output dimensions
    output_width=st.integers(min_value=500, max_value=2000),
    output_height=st.integers(min_value=500, max_value=2000),
    # Generate clip duration
    duration=st.floats(min_value=0.1, max_value=60.0, allow_nan=False, allow_infinity=False),
    # Generate two time fractions where t1 < t2
    t1_fraction=st.floats(min_value=0.0, max_value=0.99, allow_nan=False, allow_infinity=False),
    t2_fraction=st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_zoom_motion_monotonicity(
    zoom_preset: MotionPreset,
    image_width: int,
    image_height: int,
    output_width: int,
    output_height: int,
    duration: float,
    t1_fraction: float,
    t2_fraction: float,
) -> None:
    """
    Property: For any image clip with zoom motion (ZOOM_IN, ZOOM_OUT, KEN_BURNS_ZOOM_IN,
    KEN_BURNS_ZOOM_OUT) and any two time values t1 < t2 within the clip duration:
    - For zoom in: viewport area at t2 should be less than or equal to viewport area at t1
    - For zoom out: viewport area at t2 should be greater than or equal to viewport area at t1
    
    **Validates: Requirements 4.2, 4.3, 4.8, 4.9**
    """
    # Ensure t1 < t2
    if t1_fraction >= t2_fraction:
        t1_fraction, t2_fraction = t2_fraction, t1_fraction
    
    # Compute motion path for zoom preset
    camera_path = compute_motion_path(
        preset=zoom_preset,
        image_size=(image_width, image_height),
        output_size=(output_width, output_height),
        duration=duration
    )
    
    # Compute two time values within the clip duration
    t1 = t1_fraction * duration
    t2 = t2_fraction * duration
    
    # Get viewport at both times
    viewport_t1 = camera_path(t1)
    viewport_t2 = camera_path(t2)
    
    # Calculate viewport areas
    area_t1 = viewport_t1.width * viewport_t1.height
    area_t2 = viewport_t2.width * viewport_t2.height
    
    # Verify monotonicity based on zoom direction
    tolerance = 1e-6  # Relative tolerance for floating-point comparison
    
    if zoom_preset in (MotionPreset.ZOOM_IN, MotionPreset.KEN_BURNS_ZOOM_IN):
        # Zoom in: viewport area should decrease (or stay the same)
        assert area_t2 <= area_t1 + tolerance, (
            f"{zoom_preset.value} motion viewport area not monotonically decreasing: "
            f"t1={t1:.3f}s -> area={area_t1:.3f}, t2={t2:.3f}s -> area={area_t2:.3f}. "
            f"Viewport t1: ({viewport_t1.x:.3f}, {viewport_t1.y:.3f}, "
            f"{viewport_t1.width:.3f}x{viewport_t1.height:.3f}), "
            f"Viewport t2: ({viewport_t2.x:.3f}, {viewport_t2.y:.3f}, "
            f"{viewport_t2.width:.3f}x{viewport_t2.height:.3f}). "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )
    
    elif zoom_preset in (MotionPreset.ZOOM_OUT, MotionPreset.KEN_BURNS_ZOOM_OUT):
        # Zoom out: viewport area should increase (or stay the same)
        assert area_t2 >= area_t1 - tolerance, (
            f"{zoom_preset.value} motion viewport area not monotonically increasing: "
            f"t1={t1:.3f}s -> area={area_t1:.3f}, t2={t2:.3f}s -> area={area_t2:.3f}. "
            f"Viewport t1: ({viewport_t1.x:.3f}, {viewport_t1.y:.3f}, "
            f"{viewport_t1.width:.3f}x{viewport_t1.height:.3f}), "
            f"Viewport t2: ({viewport_t2.x:.3f}, {viewport_t2.y:.3f}, "
            f"{viewport_t2.width:.3f}x{viewport_t2.height:.3f}). "
            f"Image: {image_width}x{image_height}, Output: {output_width}x{output_height}, "
            f"Duration: {duration:.3f}s"
        )


# Unit Tests


class TestStaticMotionPreset:
    """Unit tests for STATIC motion preset.
    
    **Validates: Requirements 4.1**
    """
    
    def test_static_motion_returns_same_viewport_at_start_and_end(self) -> None:
        """STATIC motion should return the same viewport at t=0 and t=duration."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(5.0)
        
        assert viewport_start.x == viewport_end.x
        assert viewport_start.y == viewport_end.y
        assert viewport_start.width == viewport_end.width
        assert viewport_start.height == viewport_end.height
    
    def test_static_motion_returns_same_viewport_at_midpoint(self) -> None:
        """STATIC motion should return the same viewport at any time."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=10.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(5.0)
        viewport_end = camera_path(10.0)
        
        # All viewports should be identical
        assert viewport_start.x == viewport_mid.x == viewport_end.x
        assert viewport_start.y == viewport_mid.y == viewport_end.y
        assert viewport_start.width == viewport_mid.width == viewport_end.width
        assert viewport_start.height == viewport_mid.height == viewport_end.height
    
    def test_static_motion_with_landscape_image(self) -> None:
        """STATIC motion should center crop landscape images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport = camera_path(0.0)
        
        # For matching aspect ratios, should cover entire image
        assert viewport.x == 0.0
        assert viewport.y == 0.0
        assert viewport.width == 1920.0
        assert viewport.height == 1080.0
    
    def test_static_motion_with_portrait_image(self) -> None:
        """STATIC motion should center crop portrait images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1080, 1920),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport = camera_path(0.0)
        
        # For portrait image with landscape output, should fit width
        assert viewport.x == 0.0
        assert viewport.width == 1080.0
        # Height should be cropped to maintain aspect ratio
        expected_height = 1080.0 / (1920.0 / 1080.0)  # width / aspect
        assert abs(viewport.height - expected_height) < 1e-9
        # Should be centered vertically
        expected_y = (1920.0 - expected_height) / 2
        assert abs(viewport.y - expected_y) < 1e-9
    
    def test_static_motion_with_square_image(self) -> None:
        """STATIC motion should center crop square images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1080, 1080),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport = camera_path(0.0)
        
        # For square image with landscape output, should fit width
        assert viewport.x == 0.0
        assert viewport.width == 1080.0
        # Height should be cropped to maintain aspect ratio
        expected_height = 1080.0 / (1920.0 / 1080.0)  # width / aspect
        assert abs(viewport.height - expected_height) < 1e-9
        # Should be centered vertically
        expected_y = (1080.0 - expected_height) / 2
        assert abs(viewport.y - expected_y) < 1e-9
    
    def test_static_motion_with_wide_panorama(self) -> None:
        """STATIC motion should center crop wide panoramic images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport = camera_path(0.0)
        
        # For wide image with landscape output, should fit height
        assert viewport.y == 0.0
        assert viewport.height == 1080.0
        # Width should be cropped to maintain aspect ratio
        expected_width = 1080.0 * (1920.0 / 1080.0)  # height * aspect
        assert abs(viewport.width - expected_width) < 1e-9
        # Should be centered horizontally
        expected_x = (3840.0 - expected_width) / 2
        assert abs(viewport.x - expected_x) < 1e-9
    
    def test_static_motion_viewport_consistency_across_multiple_times(self) -> None:
        """STATIC motion should return identical viewport at multiple time points."""
        camera_path = compute_motion_path(
            preset=MotionPreset.STATIC,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=10.0
        )
        
        # Sample at multiple time points
        times = [0.0, 1.0, 2.5, 5.0, 7.5, 9.0, 10.0]
        viewports = [camera_path(t) for t in times]
        
        # All viewports should be identical
        first_viewport = viewports[0]
        for i, viewport in enumerate(viewports[1:], start=1):
            assert viewport.x == first_viewport.x, f"x differs at t={times[i]}"
            assert viewport.y == first_viewport.y, f"y differs at t={times[i]}"
            assert viewport.width == first_viewport.width, f"width differs at t={times[i]}"
            assert viewport.height == first_viewport.height, f"height differs at t={times[i]}"



class TestKenBurnsZoomPresets:
    """Unit tests for Ken Burns zoom motion presets.
    
    **Validates: Requirements 4.2, 4.3, 10.5**
    """
    
    def test_ken_burns_zoom_in_starts_larger_than_ends(self) -> None:
        """KEN_BURNS_ZOOM_IN should start with larger viewport than it ends."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(5.0)
        
        # Start viewport should be larger (more area)
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        
        assert area_start > area_end, (
            f"KEN_BURNS_ZOOM_IN should start larger: "
            f"start_area={area_start:.2f}, end_area={area_end:.2f}"
        )
    
    def test_ken_burns_zoom_in_ends_at_50_percent(self) -> None:
        """KEN_BURNS_ZOOM_IN should end at approximately 50% of image size."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # End viewport should be approximately 50% of image dimensions
        expected_width = 1920.0 * 0.5
        expected_height = 1080.0 * 0.5
        
        assert abs(viewport_end.width - expected_width) < 1.0
        assert abs(viewport_end.height - expected_height) < 1.0
    
    def test_ken_burns_zoom_in_ends_centered(self) -> None:
        """KEN_BURNS_ZOOM_IN should end with viewport centered on image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # End viewport should be centered
        expected_x = (1920.0 - viewport_end.width) / 2
        expected_y = (1080.0 - viewport_end.height) / 2
        
        assert abs(viewport_end.x - expected_x) < 1.0
        assert abs(viewport_end.y - expected_y) < 1.0
    
    def test_ken_burns_zoom_out_starts_smaller_than_ends(self) -> None:
        """KEN_BURNS_ZOOM_OUT should start with smaller viewport than it ends."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(5.0)
        
        # Start viewport should be smaller (less area)
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        
        assert area_start < area_end, (
            f"KEN_BURNS_ZOOM_OUT should start smaller: "
            f"start_area={area_start:.2f}, end_area={area_end:.2f}"
        )
    
    def test_ken_burns_zoom_out_starts_at_50_percent(self) -> None:
        """KEN_BURNS_ZOOM_OUT should start at approximately 50% of image size."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Start viewport should be approximately 50% of image dimensions
        expected_width = 1920.0 * 0.5
        expected_height = 1080.0 * 0.5
        
        assert abs(viewport_start.width - expected_width) < 1.0
        assert abs(viewport_start.height - expected_height) < 1.0
    
    def test_ken_burns_zoom_out_starts_centered(self) -> None:
        """KEN_BURNS_ZOOM_OUT should start with viewport centered on image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Start viewport should be centered
        expected_x = (1920.0 - viewport_start.width) / 2
        expected_y = (1080.0 - viewport_start.height) / 2
        
        assert abs(viewport_start.x - expected_x) < 1.0
        assert abs(viewport_start.y - expected_y) < 1.0
    
    def test_ken_burns_zoom_in_with_landscape_image(self) -> None:
        """KEN_BURNS_ZOOM_IN should work correctly with landscape images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_IN,
            image_size=(3840, 2160),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify zoom in behavior
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        assert area_start > area_end
    
    def test_ken_burns_zoom_out_with_portrait_image(self) -> None:
        """KEN_BURNS_ZOOM_OUT should work correctly with portrait images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.KEN_BURNS_ZOOM_OUT,
            image_size=(1080, 1920),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify zoom out behavior
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        assert area_start < area_end


class TestPanMotionPresets:
    """Unit tests for pan motion presets.
    
    **Validates: Requirements 4.4, 4.5, 4.6, 4.7**
    """
    
    def test_pan_left_viewport_moves_right(self) -> None:
        """PAN_LEFT should move viewport from left to right (x increases)."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_LEFT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # x should increase over time
        assert viewport_start.x < viewport_mid.x < viewport_end.x, (
            f"PAN_LEFT x should increase: "
            f"start={viewport_start.x:.2f}, mid={viewport_mid.x:.2f}, end={viewport_end.x:.2f}"
        )
    
    def test_pan_left_starts_at_left_edge(self) -> None:
        """PAN_LEFT should start with viewport at left edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_LEFT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Should start at x=0
        assert abs(viewport_start.x) < 1.0
    
    def test_pan_left_ends_at_right_edge(self) -> None:
        """PAN_LEFT should end with viewport at right edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_LEFT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # Should end at x = image_width - viewport_width
        expected_x = 3840.0 - viewport_end.width
        assert abs(viewport_end.x - expected_x) < 1.0
    
    def test_pan_right_viewport_moves_left(self) -> None:
        """PAN_RIGHT should move viewport from right to left (x decreases)."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_RIGHT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # x should decrease over time
        assert viewport_start.x > viewport_mid.x > viewport_end.x, (
            f"PAN_RIGHT x should decrease: "
            f"start={viewport_start.x:.2f}, mid={viewport_mid.x:.2f}, end={viewport_end.x:.2f}"
        )
    
    def test_pan_right_starts_at_right_edge(self) -> None:
        """PAN_RIGHT should start with viewport at right edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_RIGHT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Should start at x = image_width - viewport_width
        expected_x = 3840.0 - viewport_start.width
        assert abs(viewport_start.x - expected_x) < 1.0
    
    def test_pan_right_ends_at_left_edge(self) -> None:
        """PAN_RIGHT should end with viewport at left edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_RIGHT,
            image_size=(3840, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # Should end at x=0
        assert abs(viewport_end.x) < 1.0
    
    def test_pan_up_viewport_moves_down(self) -> None:
        """PAN_UP should move viewport from top to bottom (y increases)."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_UP,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # y should increase over time
        assert viewport_start.y < viewport_mid.y < viewport_end.y, (
            f"PAN_UP y should increase: "
            f"start={viewport_start.y:.2f}, mid={viewport_mid.y:.2f}, end={viewport_end.y:.2f}"
        )
    
    def test_pan_up_starts_at_top_edge(self) -> None:
        """PAN_UP should start with viewport at top edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_UP,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Should start at y=0
        assert abs(viewport_start.y) < 1.0
    
    def test_pan_up_ends_at_bottom_edge(self) -> None:
        """PAN_UP should end with viewport at bottom edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_UP,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # Should end at y = image_height - viewport_height
        expected_y = 3840.0 - viewport_end.height
        assert abs(viewport_end.y - expected_y) < 1.0
    
    def test_pan_down_viewport_moves_up(self) -> None:
        """PAN_DOWN should move viewport from bottom to top (y decreases)."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_DOWN,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # y should decrease over time
        assert viewport_start.y > viewport_mid.y > viewport_end.y, (
            f"PAN_DOWN y should decrease: "
            f"start={viewport_start.y:.2f}, mid={viewport_mid.y:.2f}, end={viewport_end.y:.2f}"
        )
    
    def test_pan_down_starts_at_bottom_edge(self) -> None:
        """PAN_DOWN should start with viewport at bottom edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_DOWN,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Should start at y = image_height - viewport_height
        expected_y = 3840.0 - viewport_start.height
        assert abs(viewport_start.y - expected_y) < 1.0
    
    def test_pan_down_ends_at_top_edge(self) -> None:
        """PAN_DOWN should end with viewport at top edge of image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_DOWN,
            image_size=(1920, 3840),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # Should end at y=0
        assert abs(viewport_end.y) < 1.0
    
    def test_pan_left_with_landscape_image(self) -> None:
        """PAN_LEFT should work correctly with landscape images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_LEFT,
            image_size=(3840, 2160),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify pan left behavior
        assert viewport_end.x > viewport_start.x
    
    def test_pan_up_with_portrait_image(self) -> None:
        """PAN_UP should work correctly with portrait images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.PAN_UP,
            image_size=(1080, 1920),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify pan up behavior
        assert viewport_end.y > viewport_start.y


class TestZoomMotionPresets:
    """Unit tests for zoom motion presets.
    
    **Validates: Requirements 4.8, 4.9**
    """
    
    def test_zoom_in_viewport_shrinks(self) -> None:
        """ZOOM_IN should shrink viewport toward center over time."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # Viewport area should decrease over time
        area_start = viewport_start.width * viewport_start.height
        area_mid = viewport_mid.width * viewport_mid.height
        area_end = viewport_end.width * viewport_end.height
        
        assert area_start > area_mid > area_end, (
            f"ZOOM_IN area should decrease: "
            f"start={area_start:.2f}, mid={area_mid:.2f}, end={area_end:.2f}"
        )
    
    def test_zoom_in_starts_at_full_image(self) -> None:
        """ZOOM_IN should start with viewport covering full image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Should start at full image size
        assert abs(viewport_start.x) < 1.0
        assert abs(viewport_start.y) < 1.0
        assert abs(viewport_start.width - 1920.0) < 1.0
        assert abs(viewport_start.height - 1080.0) < 1.0
    
    def test_zoom_in_ends_at_50_percent(self) -> None:
        """ZOOM_IN should end at approximately 50% of image size."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # End viewport should be approximately 50% of image dimensions
        expected_width = 1920.0 * 0.5
        expected_height = 1080.0 * 0.5
        
        assert abs(viewport_end.width - expected_width) < 1.0
        assert abs(viewport_end.height - expected_height) < 1.0
    
    def test_zoom_in_stays_centered(self) -> None:
        """ZOOM_IN should keep viewport centered throughout motion."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        # Check centering at multiple time points
        for t in [0.0, 1.0, 2.5, 4.0, 5.0]:
            viewport = camera_path(t)
            
            # Viewport should be centered
            expected_x = (1920.0 - viewport.width) / 2
            expected_y = (1080.0 - viewport.height) / 2
            
            assert abs(viewport.x - expected_x) < 1.0, f"Not centered at t={t}"
            assert abs(viewport.y - expected_y) < 1.0, f"Not centered at t={t}"
    
    def test_zoom_out_viewport_expands(self) -> None:
        """ZOOM_OUT should expand viewport from center over time."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_mid = camera_path(2.5)
        viewport_end = camera_path(5.0)
        
        # Viewport area should increase over time
        area_start = viewport_start.width * viewport_start.height
        area_mid = viewport_mid.width * viewport_mid.height
        area_end = viewport_end.width * viewport_end.height
        
        assert area_start < area_mid < area_end, (
            f"ZOOM_OUT area should increase: "
            f"start={area_start:.2f}, mid={area_mid:.2f}, end={area_end:.2f}"
        )
    
    def test_zoom_out_starts_at_50_percent(self) -> None:
        """ZOOM_OUT should start at approximately 50% of image size."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_start = camera_path(0.0)
        
        # Start viewport should be approximately 50% of image dimensions
        expected_width = 1920.0 * 0.5
        expected_height = 1080.0 * 0.5
        
        assert abs(viewport_start.width - expected_width) < 1.0
        assert abs(viewport_start.height - expected_height) < 1.0
    
    def test_zoom_out_ends_at_full_image(self) -> None:
        """ZOOM_OUT should end with viewport covering full image."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        viewport_end = camera_path(5.0)
        
        # Should end at full image size
        assert abs(viewport_end.x) < 1.0
        assert abs(viewport_end.y) < 1.0
        assert abs(viewport_end.width - 1920.0) < 1.0
        assert abs(viewport_end.height - 1080.0) < 1.0
    
    def test_zoom_out_stays_centered(self) -> None:
        """ZOOM_OUT should keep viewport centered throughout motion."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_OUT,
            image_size=(1920, 1080),
            output_size=(1920, 1080),
            duration=5.0
        )
        
        # Check centering at multiple time points
        for t in [0.0, 1.0, 2.5, 4.0, 5.0]:
            viewport = camera_path(t)
            
            # Viewport should be centered
            expected_x = (1920.0 - viewport.width) / 2
            expected_y = (1080.0 - viewport.height) / 2
            
            assert abs(viewport.x - expected_x) < 1.0, f"Not centered at t={t}"
            assert abs(viewport.y - expected_y) < 1.0, f"Not centered at t={t}"
    
    def test_zoom_in_with_landscape_image(self) -> None:
        """ZOOM_IN should work correctly with landscape images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(3840, 2160),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify zoom in behavior
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        assert area_start > area_end
    
    def test_zoom_out_with_portrait_image(self) -> None:
        """ZOOM_OUT should work correctly with portrait images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_OUT,
            image_size=(1080, 1920),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify zoom out behavior
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        assert area_start < area_end
    
    def test_zoom_in_with_square_image(self) -> None:
        """ZOOM_IN should work correctly with square images."""
        camera_path = compute_motion_path(
            preset=MotionPreset.ZOOM_IN,
            image_size=(2048, 2048),
            output_size=(1920, 1080),
            duration=3.0
        )
        
        viewport_start = camera_path(0.0)
        viewport_end = camera_path(3.0)
        
        # Verify zoom in behavior
        area_start = viewport_start.width * viewport_start.height
        area_end = viewport_end.width * viewport_end.height
        assert area_start > area_end
        
        # Should stay centered
        center_x_start = viewport_start.x + viewport_start.width / 2
        center_x_end = viewport_end.x + viewport_end.width / 2
        assert abs(center_x_start - center_x_end) < 1.0
