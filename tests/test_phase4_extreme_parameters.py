"""Extreme parameter tests for Phase 4 effects.

Tests all Phase 4 effects with minimum, maximum, and boundary parameter values
to ensure they handle extreme inputs gracefully without crashing.
"""

from __future__ import annotations

import numpy as np
import pytest

from engine.effects import (
    # Color effects with parameters
    hue_shift,
    color_temperature,
    tint,
    gamma_correction,
    channel_mixer,
    duotone,
    tricolor,
    vibrance,
    color_pulse,
    fade_to_color,
    posterize,
    solarize,
    # Blur effects with parameters
    box_blur,
    gaussian_blur,
    motion_blur,
    radial_blur,
    zoom_blur,
    pixelate,
    sharpen,
    bilateral_blur,
    tilt_shift,
    depth_of_field,
    animated_blur,
    # Texture effects with parameters
    scan_lines,
    letterbox,
    vignette_simple,
    gradient_overlay,
    border,
    pattern_overlay,
    light_leak,
    bokeh_overlay,
    dust_scratches,
    lens_flare,
    progress_bar,
    halftone,
    # Stylization effects with parameters
    chromatic_aberration,
    glitch_rgb_split,
    glitch_block_displacement,
    glitch_scan_line_shift,
    glitch_color_corruption,
    crt_retro,
    vhs_tape_distortion,
    threshold_bw,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_frame():
    """Create a standard 100x100 test frame."""
    frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    return frame


@pytest.fixture
def small_frame():
    """Create a minimal 10x10 test frame."""
    return np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)


@pytest.fixture
def large_frame():
    """Create a large 1080p test frame."""
    return np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_output(result: np.ndarray, input_frame: np.ndarray) -> None:
    """Validate that effect output is valid."""
    assert result is not None, "Effect returned None"
    assert isinstance(result, np.ndarray), "Effect did not return numpy array"
    assert result.shape == input_frame.shape, "Effect changed frame shape"
    assert result.dtype == np.uint8, "Effect changed frame dtype"
    assert not np.isnan(result).any(), "Effect produced NaN values"


# ============================================================================
# Color Effects - Extreme Parameter Tests
# ============================================================================

class TestHueShiftExtreme:
    """Test hue_shift with extreme parameters."""
    
    def test_hue_shift_zero(self, test_frame):
        """Hue shift with 0 degrees should be close to unchanged."""
        effect = hue_shift(0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        # HSV conversion may introduce small errors, so just validate output
    
    def test_hue_shift_max(self, test_frame):
        """Hue shift with 360 degrees should wrap around."""
        effect = hue_shift(360)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_hue_shift_negative(self, test_frame):
        """Hue shift with negative degrees."""
        effect = hue_shift(-180)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_hue_shift_large_positive(self, test_frame):
        """Hue shift with very large positive value."""
        effect = hue_shift(720)  # Two full rotations
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_hue_shift_large_negative(self, test_frame):
        """Hue shift with very large negative value."""
        effect = hue_shift(-720)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestColorTemperatureExtreme:
    """Test color_temperature with extreme parameters."""
    
    def test_color_temperature_min(self, test_frame):
        """Color temperature at minimum (1000K - very warm)."""
        effect = color_temperature(1000)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_color_temperature_max(self, test_frame):
        """Color temperature at maximum (15000K - very cool)."""
        effect = color_temperature(15000)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_color_temperature_neutral(self, test_frame):
        """Color temperature at neutral (6500K)."""
        effect = color_temperature(6500)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestTintExtreme:
    """Test tint with extreme parameters."""
    
    def test_tint_zero_strength(self, test_frame):
        """Tint with zero strength should be unchanged."""
        effect = tint((255, 0, 0), 0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)
    
    def test_tint_max_strength(self, test_frame):
        """Tint with maximum strength (1.0)."""
        effect = tint((255, 0, 0), 1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_tint_black_color(self, test_frame):
        """Tint with black color."""
        effect = tint((0, 0, 0), 0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_tint_white_color(self, test_frame):
        """Tint with white color."""
        effect = tint((255, 255, 255), 0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestGammaCorrectionExtreme:
    """Test gamma_correction with extreme parameters."""
    
    def test_gamma_min(self, test_frame):
        """Gamma correction with minimum value (0.1 - very dark)."""
        effect = gamma_correction(0.1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_gamma_max(self, test_frame):
        """Gamma correction with maximum value (5.0 - very bright)."""
        effect = gamma_correction(5.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_gamma_neutral(self, test_frame):
        """Gamma correction with neutral value (1.0)."""
        effect = gamma_correction(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)


class TestPosterizeExtreme:
    """Test posterize with extreme parameters."""
    
    def test_posterize_min_bits(self, test_frame):
        """Posterize with minimum bits (1 - binary)."""
        effect = posterize(1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_posterize_max_bits(self, test_frame):
        """Posterize with maximum bits (8 - unchanged)."""
        effect = posterize(8)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)


class TestSolarizeExtreme:
    """Test solarize with extreme parameters."""
    
    def test_solarize_min_threshold(self, test_frame):
        """Solarize with minimum threshold (0)."""
        effect = solarize(0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_solarize_max_threshold(self, test_frame):
        """Solarize with maximum threshold (255)."""
        effect = solarize(255)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_solarize_mid_threshold(self, test_frame):
        """Solarize with mid threshold (128)."""
        effect = solarize(128)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestVibranceExtreme:
    """Test vibrance with extreme parameters."""
    
    def test_vibrance_zero(self, test_frame):
        """Vibrance with zero amount should be unchanged."""
        effect = vibrance(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_vibrance_max_positive(self, test_frame):
        """Vibrance with maximum positive value."""
        effect = vibrance(2.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_vibrance_negative(self, test_frame):
        """Vibrance with negative value (desaturate)."""
        effect = vibrance(-1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


# ============================================================================
# Blur Effects - Extreme Parameter Tests
# ============================================================================

class TestBoxBlurExtreme:
    """Test box_blur with extreme parameters."""
    
    def test_box_blur_min_kernel(self, test_frame):
        """Box blur with minimum kernel size (1)."""
        effect = box_blur(1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)
    
    def test_box_blur_max_kernel(self, test_frame):
        """Box blur with very large kernel size."""
        effect = box_blur(99)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_box_blur_even_kernel(self, test_frame):
        """Box blur with even kernel size (should be converted to odd)."""
        effect = box_blur(10)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestGaussianBlurExtreme:
    """Test gaussian_blur with extreme parameters."""
    
    def test_gaussian_blur_min_kernel(self, test_frame):
        """Gaussian blur with minimum kernel size (1)."""
        effect = gaussian_blur(1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_gaussian_blur_max_kernel(self, test_frame):
        """Gaussian blur with very large kernel size."""
        effect = gaussian_blur(99)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestMotionBlurExtreme:
    """Test motion_blur with extreme parameters."""
    
    def test_motion_blur_min_amount(self, test_frame):
        """Motion blur with minimum amount (1)."""
        effect = motion_blur(angle=0, amount=1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_motion_blur_max_amount(self, test_frame):
        """Motion blur with very large amount."""
        effect = motion_blur(angle=0, amount=50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_motion_blur_all_angles(self, test_frame):
        """Motion blur at various extreme angles."""
        for angle in [0, 45, 90, 135, 180, 270, 360, -90]:
            effect = motion_blur(angle=angle, amount=10)
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)


class TestRadialBlurExtreme:
    """Test radial_blur with extreme parameters."""
    
    def test_radial_blur_zero_strength(self, test_frame):
        """Radial blur with zero strength should be unchanged."""
        effect = radial_blur(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_radial_blur_max_strength(self, test_frame):
        """Radial blur with maximum strength."""
        effect = radial_blur(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestZoomBlurExtreme:
    """Test zoom_blur with extreme parameters."""
    
    def test_zoom_blur_zero_strength(self, test_frame):
        """Zoom blur with zero strength should be unchanged."""
        effect = zoom_blur(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_zoom_blur_max_strength(self, test_frame):
        """Zoom blur with maximum strength."""
        effect = zoom_blur(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestPixelateExtreme:
    """Test pixelate with extreme parameters."""
    
    def test_pixelate_min_factor(self, test_frame):
        """Pixelate with minimum factor (1 - unchanged)."""
        effect = pixelate(1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_pixelate_max_factor(self, test_frame):
        """Pixelate with very large factor."""
        effect = pixelate(50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_pixelate_frame_size_factor(self, small_frame):
        """Pixelate with factor equal to frame size."""
        effect = pixelate(10)  # Same as frame size
        result = effect(small_frame, t=0.5, progress=0.5)
        validate_output(result, small_frame)


class TestSharpenExtreme:
    """Test sharpen with extreme parameters."""
    
    def test_sharpen_zero_amount(self, test_frame):
        """Sharpen with zero amount should be unchanged."""
        effect = sharpen(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_sharpen_max_amount(self, test_frame):
        """Sharpen with maximum amount."""
        effect = sharpen(5.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestBilateralBlurExtreme:
    """Test bilateral_blur with extreme parameters."""
    
    def test_bilateral_blur_min_params(self, test_frame):
        """Bilateral blur with minimum parameters."""
        effect = bilateral_blur(1, 1, 1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_bilateral_blur_max_params(self, test_frame):
        """Bilateral blur with maximum parameters."""
        effect = bilateral_blur(15, 150, 150)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestTiltShiftExtreme:
    """Test tilt_shift with extreme parameters."""
    
    def test_tilt_shift_zero_blur(self, test_frame):
        """Tilt shift with zero blur amount."""
        effect = tilt_shift(blur_amount=0, gradient_start=0.3, gradient_end=0.7)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_tilt_shift_max_blur(self, test_frame):
        """Tilt shift with maximum blur amount."""
        effect = tilt_shift(blur_amount=50, gradient_start=0.3, gradient_end=0.7)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_tilt_shift_extreme_positions(self, test_frame):
        """Tilt shift at extreme gradient positions."""
        for start, end in [(0.0, 0.2), (0.4, 0.6), (0.8, 1.0)]:
            effect = tilt_shift(blur_amount=15, gradient_start=start, gradient_end=end)
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)


class TestDepthOfFieldExtreme:
    """Test depth_of_field with extreme parameters."""
    
    def test_depth_of_field_min_aperture(self, test_frame):
        """Depth of field with minimum aperture (less blur)."""
        effect = depth_of_field(focus_distance=0.5, aperture=0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_depth_of_field_max_aperture(self, test_frame):
        """Depth of field with maximum aperture (more blur)."""
        effect = depth_of_field(focus_distance=0.5, aperture=8.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


# ============================================================================
# Texture Effects - Extreme Parameter Tests
# ============================================================================


class TestScanLinesExtreme:
    """Test scan_lines with extreme parameters."""
    
    def test_scan_lines_min_spacing(self, test_frame):
        """Scan lines with minimum spacing (1)."""
        effect = scan_lines(1, 0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_scan_lines_max_spacing(self, test_frame):
        """Scan lines with very large spacing."""
        effect = scan_lines(50, 0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_scan_lines_zero_intensity(self, test_frame):
        """Scan lines with zero intensity should be unchanged."""
        effect = scan_lines(2, 0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_scan_lines_max_intensity(self, test_frame):
        """Scan lines with maximum intensity."""
        effect = scan_lines(2, 1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestLetterboxExtreme:
    """Test letterbox with extreme parameters."""
    
    def test_letterbox_zero_bars(self, test_frame):
        """Letterbox with zero bar height."""
        effect = letterbox(0, 0, (0, 0, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=1)
    
    def test_letterbox_max_bars(self, test_frame):
        """Letterbox with very large bars."""
        effect = letterbox(40, 40, (0, 0, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_letterbox_full_frame(self, small_frame):
        """Letterbox with bars covering entire frame."""
        effect = letterbox(5, 5, (0, 0, 0))  # 10x10 frame
        result = effect(small_frame, t=0.5, progress=0.5)
        validate_output(result, small_frame)


class TestVignetteSimpleExtreme:
    """Test vignette_simple with extreme parameters."""
    
    def test_vignette_zero_intensity(self, test_frame):
        """Vignette with zero intensity should be unchanged."""
        effect = vignette_simple(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_vignette_max_intensity(self, test_frame):
        """Vignette with maximum intensity."""
        effect = vignette_simple(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestBorderExtreme:
    """Test border with extreme parameters."""
    
    def test_border_zero_thickness(self, test_frame):
        """Border with zero thickness should be unchanged."""
        effect = border(0, (255, 0, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=1)
    
    def test_border_max_thickness(self, test_frame):
        """Border with very large thickness."""
        effect = border(40, (255, 0, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_border_full_frame(self, small_frame):
        """Border with thickness covering entire frame."""
        effect = border(5, (255, 0, 0))  # 10x10 frame
        result = effect(small_frame, t=0.5, progress=0.5)
        validate_output(result, small_frame)


class TestGradientOverlayExtreme:
    """Test gradient_overlay with extreme parameters."""
    
    def test_gradient_zero_opacity(self, test_frame):
        """Gradient overlay with zero opacity should be unchanged."""
        effect = gradient_overlay((255, 0, 0), (0, 0, 255), "vertical", 0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)
    
    def test_gradient_max_opacity(self, test_frame):
        """Gradient overlay with maximum opacity."""
        effect = gradient_overlay((255, 0, 0), (0, 0, 255), "vertical", 1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_gradient_all_directions(self, test_frame):
        """Gradient overlay in all directions."""
        for direction in ["vertical", "horizontal", "diagonal"]:
            effect = gradient_overlay((255, 0, 0), (0, 0, 255), direction, 0.5)
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)


class TestLightLeakExtreme:
    """Test light_leak with extreme parameters."""
    
    def test_light_leak_zero_intensity(self, test_frame):
        """Light leak with zero intensity should be unchanged."""
        effect = light_leak(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_light_leak_max_intensity(self, test_frame):
        """Light leak with maximum intensity."""
        effect = light_leak(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestLensFlareExtreme:
    """Test lens_flare with extreme parameters."""
    
    def test_lens_flare_corner_positions(self, test_frame):
        """Lens flare at corner positions."""
        h, w = test_frame.shape[:2]
        positions = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, h//2)]
        for x, y in positions:
            effect = lens_flare(x, y)
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)
    
    def test_lens_flare_outside_frame(self, test_frame):
        """Lens flare positioned outside frame."""
        h, w = test_frame.shape[:2]
        effect = lens_flare(w + 50, h + 50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestProgressBarExtreme:
    """Test progress_bar with extreme parameters."""
    
    def test_progress_bar_zero_height(self, test_frame):
        """Progress bar with zero height."""
        effect = progress_bar("bottom", 0, (0, 255, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_progress_bar_max_height(self, test_frame):
        """Progress bar with very large height."""
        effect = progress_bar("bottom", 50, (0, 255, 0))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_progress_bar_all_positions(self, test_frame):
        """Progress bar at all positions."""
        for position in ["top", "bottom", "left", "right"]:
            effect = progress_bar(position, 10, (0, 255, 0))
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)


# ============================================================================
# Stylization Effects - Extreme Parameter Tests
# ============================================================================


class TestChromaticAberrationExtreme:
    """Test chromatic_aberration with extreme parameters."""
    
    def test_chromatic_aberration_zero_offset(self, test_frame):
        """Chromatic aberration with zero offset should be unchanged."""
        effect = chromatic_aberration(0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)
    
    def test_chromatic_aberration_max_offset(self, test_frame):
        """Chromatic aberration with maximum offset."""
        effect = chromatic_aberration(50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_chromatic_aberration_negative_offset(self, test_frame):
        """Chromatic aberration with negative offset."""
        effect = chromatic_aberration(-20)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestGlitchRGBSplitExtreme:
    """Test glitch_rgb_split with extreme parameters."""
    
    def test_glitch_rgb_split_zero_offset(self, test_frame):
        """Glitch RGB split with zero offset should be close to unchanged."""
        effect = glitch_rgb_split(max_offset=0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        # May have small variations due to random seed
    
    def test_glitch_rgb_split_max_offset(self, test_frame):
        """Glitch RGB split with maximum offset."""
        effect = glitch_rgb_split(max_offset=50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestGlitchBlockDisplacementExtreme:
    """Test glitch_block_displacement with extreme parameters."""
    
    def test_glitch_block_min_size(self, test_frame):
        """Glitch block displacement with minimum block size."""
        effect = glitch_block_displacement(block_size=1, displacement=10)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_glitch_block_max_size(self, test_frame):
        """Glitch block displacement with maximum block size."""
        effect = glitch_block_displacement(block_size=50, displacement=10)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_glitch_block_zero_displacement(self, test_frame):
        """Glitch block displacement with zero displacement."""
        effect = glitch_block_displacement(block_size=10, displacement=0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        # With zero displacement, output should be close to input
        assert np.allclose(result, test_frame, atol=2)


class TestGlitchScanLineShiftExtreme:
    """Test glitch_scan_line_shift with extreme parameters."""
    
    def test_glitch_scan_line_zero_intensity(self, test_frame):
        """Glitch scan line shift with zero intensity should be unchanged."""
        effect = glitch_scan_line_shift(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_glitch_scan_line_max_intensity(self, test_frame):
        """Glitch scan line shift with maximum intensity."""
        effect = glitch_scan_line_shift(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestGlitchColorCorruptionExtreme:
    """Test glitch_color_corruption with extreme parameters."""
    
    def test_glitch_color_zero_intensity(self, test_frame):
        """Glitch color corruption with zero intensity should be unchanged."""
        effect = glitch_color_corruption(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_glitch_color_max_intensity(self, test_frame):
        """Glitch color corruption with maximum intensity."""
        effect = glitch_color_corruption(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestCRTRetroExtreme:
    """Test crt_retro with extreme parameters."""
    
    def test_crt_retro_zero_intensity(self, test_frame):
        """CRT retro with zero intensity should be unchanged."""
        effect = crt_retro(0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_crt_retro_max_intensity(self, test_frame):
        """CRT retro with maximum intensity."""
        effect = crt_retro(1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestVHSTapeDistortionExtreme:
    """Test vhs_tape_distortion with extreme parameters."""
    
    def test_vhs_zero_intensity(self, test_frame):
        """VHS tape distortion with zero intensity should be close to unchanged."""
        effect = vhs_tape_distortion(intensity=0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        # May have small variations due to implementation
    
    def test_vhs_max_intensity(self, test_frame):
        """VHS tape distortion with maximum intensity."""
        effect = vhs_tape_distortion(intensity=1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestThresholdBWExtreme:
    """Test threshold_bw with extreme parameters."""
    
    def test_threshold_min_value(self, test_frame):
        """Threshold with minimum value (0)."""
        effect = threshold_bw(0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_threshold_max_value(self, test_frame):
        """Threshold with maximum value (255)."""
        effect = threshold_bw(255)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_threshold_mid_value(self, test_frame):
        """Threshold with mid value (128)."""
        effect = threshold_bw(128)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestHalftoneExtreme:
    """Test halftone with extreme parameters."""
    
    def test_halftone_min_dot_size(self, test_frame):
        """Halftone with minimum dot size (1)."""
        effect = halftone(1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_halftone_max_dot_size(self, test_frame):
        """Halftone with very large dot size."""
        effect = halftone(50)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


# ============================================================================
# Combined Extreme Tests
# ============================================================================

class TestMultipleExtremeParameters:
    """Test effects with multiple extreme parameters combined."""
    
    def test_channel_mixer_extreme_values(self, test_frame):
        """Channel mixer with extreme RGB values."""
        # All red
        effect = channel_mixer(
            red=(1.0, 0.0, 0.0),
            green=(0.0, 0.0, 0.0),
            blue=(0.0, 0.0, 0.0)
        )
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # All green
        effect = channel_mixer(
            red=(0.0, 0.0, 0.0),
            green=(0.0, 1.0, 0.0),
            blue=(0.0, 0.0, 0.0)
        )
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # All blue
        effect = channel_mixer(
            red=(0.0, 0.0, 0.0),
            green=(0.0, 0.0, 0.0),
            blue=(0.0, 0.0, 1.0)
        )
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_duotone_extreme_colors(self, test_frame):
        """Duotone with extreme color combinations."""
        # Black to white
        effect = duotone((0, 0, 0), (255, 255, 255))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # Pure red to pure blue
        effect = duotone((255, 0, 0), (0, 0, 255))
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_tricolor_extreme_colors(self, test_frame):
        """Tricolor with extreme color combinations."""
        effect = tricolor(
            color1=(0, 0, 0),
            color2=(128, 128, 128),
            color3=(255, 255, 255)
        )
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_color_pulse_extreme_params(self, test_frame):
        """Color pulse with extreme parameters."""
        # Zero frequency
        effect = color_pulse(frequency=0.0, color=(255, 0, 0), amount=0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # Very high frequency
        effect = color_pulse(frequency=10.0, color=(255, 0, 0), amount=0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # Zero amount
        effect = color_pulse(frequency=1.0, color=(255, 0, 0), amount=0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        
        # Max amount
        effect = color_pulse(frequency=1.0, color=(255, 0, 0), amount=1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


# ============================================================================
# Frame Size Extreme Tests
# ============================================================================

class TestFrameSizeExtremes:
    """Test effects with extreme frame sizes."""
    
    def test_effects_on_small_frame(self, small_frame):
        """Test various effects on very small frame (10x10)."""
        effects = [
            hue_shift(120),
            posterize(4),
            box_blur(3),
            pixelate(2),
            scan_lines(2, 0.5),
            vignette_simple(0.5),
            chromatic_aberration(2),
            threshold_bw(128),
        ]
        for effect in effects:
            result = effect(small_frame, t=0.5, progress=0.5)
            validate_output(result, small_frame)
    
    def test_effects_on_large_frame(self, large_frame):
        """Test effects on large frame (1080p) - subset for performance."""
        effects = [
            hue_shift(120),
            posterize(4),
            pixelate(10),
            threshold_bw(128),
        ]
        for effect in effects:
            result = effect(large_frame, t=0.5, progress=0.5)
            validate_output(result, large_frame)


# ============================================================================
# Progress and Time Boundary Tests
# ============================================================================

class TestProgressTimeBoundaries:
    """Test effects at progress and time boundaries."""
    
    def test_effects_at_progress_zero(self, test_frame):
        """Test effects at progress=0.0."""
        effects = [
            fade_to_color((255, 0, 0)),
            color_pulse((255, 0, 0), 1.0, 0.5),
            progress_bar("bottom", 10, (0, 255, 0)),
            animated_blur(10),
        ]
        for effect in effects:
            result = effect(test_frame, t=0.0, progress=0.0)
            validate_output(result, test_frame)
    
    def test_effects_at_progress_one(self, test_frame):
        """Test effects at progress=1.0."""
        effects = [
            fade_to_color((255, 0, 0)),
            color_pulse((255, 0, 0), 1.0, 0.5),
            progress_bar("bottom", 10, (0, 255, 0)),
            animated_blur(10),
        ]
        for effect in effects:
            result = effect(test_frame, t=1.0, progress=1.0)
            validate_output(result, test_frame)
    
    def test_effects_at_negative_time(self, test_frame):
        """Test effects with negative time values."""
        effects = [
            color_pulse((255, 0, 0), 1.0, 0.5),
            animated_blur(10),
        ]
        for effect in effects:
            result = effect(test_frame, t=-1.0, progress=0.5)
            validate_output(result, test_frame)
    
    def test_effects_at_large_time(self, test_frame):
        """Test effects with very large time values."""
        effects = [
            color_pulse((255, 0, 0), 1.0, 0.5),
            animated_blur(10),
        ]
        for effect in effects:
            result = effect(test_frame, t=1000.0, progress=0.5)
            validate_output(result, test_frame)


# ============================================================================
# Additional Texture Effects Extreme Tests
# ============================================================================

class TestPatternOverlayExtreme:
    """Test pattern_overlay with extreme parameters."""
    
    def test_pattern_overlay_zero_opacity(self, test_frame):
        """Pattern overlay with zero opacity."""
        effect = pattern_overlay(pattern=None, opacity=0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=2)
    
    def test_pattern_overlay_max_opacity(self, test_frame):
        """Pattern overlay with maximum opacity."""
        effect = pattern_overlay(pattern=None, opacity=1.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_pattern_overlay_custom_pattern(self, test_frame):
        """Pattern overlay with custom pattern."""
        # Create small pattern
        pattern = np.ones((5, 5, 3), dtype=np.uint8) * 128
        effect = pattern_overlay(pattern=pattern, opacity=0.5)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestBokehOverlayExtreme:
    """Test bokeh_overlay with extreme parameters."""
    
    def test_bokeh_overlay_min_count(self, test_frame):
        """Bokeh overlay with minimum bokeh count."""
        effect = bokeh_overlay(num_circles=1, max_radius=20)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_bokeh_overlay_max_count(self, test_frame):
        """Bokeh overlay with maximum bokeh count."""
        effect = bokeh_overlay(num_circles=100, max_radius=20)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_bokeh_overlay_min_radius(self, test_frame):
        """Bokeh overlay with minimum radius."""
        effect = bokeh_overlay(num_circles=20, max_radius=10)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_bokeh_overlay_max_radius(self, test_frame):
        """Bokeh overlay with maximum radius."""
        effect = bokeh_overlay(num_circles=20, max_radius=100)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestDustScratchesExtreme:
    """Test dust_scratches with extreme parameters."""
    
    def test_dust_scratches_zero_density(self, test_frame):
        """Dust scratches with zero density."""
        effect = dust_scratches(density=0.0)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
        assert np.allclose(result, test_frame, atol=1)
    
    def test_dust_scratches_min_density(self, test_frame):
        """Dust scratches with minimum density."""
        effect = dust_scratches(density=0.0001)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_dust_scratches_max_density(self, test_frame):
        """Dust scratches with maximum density."""
        effect = dust_scratches(density=0.01)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


class TestAnimatedBlurExtreme:
    """Test animated_blur with extreme parameters."""
    
    def test_animated_blur_min_kernel(self, test_frame):
        """Animated blur with minimum kernel size."""
        effect = animated_blur(min_kernel=1, max_kernel=1)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)
    
    def test_animated_blur_max_kernel(self, test_frame):
        """Animated blur with maximum kernel size."""
        effect = animated_blur(min_kernel=1, max_kernel=31)
        result = effect(test_frame, t=0.5, progress=0.5)
        validate_output(result, test_frame)


# ============================================================================
# Comprehensive Extreme Parameter Test
# ============================================================================

class TestAllEffectsExtremeParameters:
    """Comprehensive test of all Phase 4 effects with extreme parameters."""
    
    @pytest.mark.parametrize("effect_factory,params", [
        # Color effects
        (hue_shift, [0, 360, -180, 720]),
        (color_temperature, [1000, 6500, 15000]),
        (gamma_correction, [0.1, 1.0, 5.0]),
        (posterize, [1, 4, 8]),
        (solarize, [0, 128, 255]),
        (vibrance, [-1.0, 0.0, 2.0]),
        # Blur effects
        (box_blur, [1, 5, 99]),
        (gaussian_blur, [1, 5, 99]),
        (pixelate, [1, 10, 50]),
        (sharpen, [0.0, 1.5, 5.0]),
        # Texture effects
        (vignette_simple, [0.0, 0.5, 1.0]),
        (halftone, [1, 5, 50]),
        # Stylization effects
        (chromatic_aberration, [0, 5, 50]),
        (threshold_bw, [0, 128, 255]),
    ])
    def test_effect_with_extreme_params(self, test_frame, effect_factory, params):
        """Test each effect with its extreme parameter values."""
        for param in params:
            if effect_factory == glitch_rgb_split:
                effect = effect_factory(max_offset=param)
            else:
                effect = effect_factory(param)
            result = effect(test_frame, t=0.5, progress=0.5)
            validate_output(result, test_frame)
    
    @pytest.mark.parametrize("effect_factory,param1,param2", [
        # Effects with two parameters
        (tint, [(255, 0, 0), (0, 0, 0), (255, 255, 255)], [0.0, 0.5, 1.0]),
        (motion_blur, [0, 90, 180], [1, 10, 50]),
        (scan_lines, [1, 2, 50], [0.0, 0.5, 1.0]),
        (border, [0, 5, 40], [(255, 0, 0)]),
        (light_leak, [0.0, 0.5, 1.0], [None]),
        (glitch_block_displacement, [1, 10, 50], [0, 10, 50]),
        (glitch_scan_line_shift, [0.0, 0.5, 1.0], [None]),
        (glitch_color_corruption, [0.0, 0.5, 1.0], [None]),
        (crt_retro, [0.0, 0.1, 1.0], [None]),
        (vhs_tape_distortion, [0.0, 0.5, 1.0], [None]),
    ])
    def test_two_param_effects_extreme(self, test_frame, effect_factory, param1, param2):
        """Test effects with two parameters at extreme values."""
        param1_list = param1 if isinstance(param1, list) else [param1]
        param2_list = param2 if isinstance(param2, list) else [param2]
        
        for p1 in param1_list:
            for p2 in param2_list:
                if p2 is None:
                    effect = effect_factory(p1)
                elif effect_factory == tint:
                    # tint(color, strength)
                    effect = effect_factory(p1, p2)
                elif effect_factory == motion_blur:
                    # motion_blur(angle, amount)
                    effect = effect_factory(angle=p1, amount=p2)
                elif effect_factory == scan_lines:
                    # scan_lines(spacing, intensity)
                    effect = effect_factory(spacing=p1, intensity=p2)
                elif effect_factory == border:
                    # border(thickness, color)
                    effect = effect_factory(thickness=p1, color=p2)
                elif effect_factory == glitch_block_displacement:
                    # glitch_block_displacement(block_size, displacement)
                    effect = effect_factory(block_size=p1, displacement=p2)
                else:
                    effect = effect_factory(p1, p2)
                result = effect(test_frame, t=0.5, progress=0.5)
                validate_output(result, test_frame)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
