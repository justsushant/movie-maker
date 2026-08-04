"""Aspect ratio tests for Phase 4 effects.

Tests all Phase 4 effects with various frame aspect ratios to ensure they handle
different dimensions correctly. Tests common aspect ratios including:
- 16:9 (1920x1080) - Standard HD landscape
- 4:3 (1024x768) - Classic landscape
- 1:1 (1080x1080) - Square
- 21:9 (2560x1080) - Ultra-wide landscape
- 9:16 (1080x1920) - Portrait (vertical video)
- 2.39:1 (2560x1070) - Cinematic widescreen
"""

from __future__ import annotations

import numpy as np
import pytest

from engine.effects import (
    # Color effects - representative samples
    grayscale,
    sepia,
    hue_shift,
    gamma_correction,
    posterize,
    vibrance,
    # Blur effects - representative samples
    box_blur,
    gaussian_blur,
    motion_blur,
    radial_blur,
    pixelate,
    sharpen,
    # Texture effects - representative samples
    scan_lines,
    letterbox,
    vignette_simple,
    gradient_overlay,
    border,
    light_leak,
    # Stylization effects - representative samples
    chromatic_aberration,
    glitch_rgb_split,
    glitch_block_displacement,
    threshold_bw,
    halftone,
    crt_retro,
)


# ============================================================================
# Test Fixtures - Various Aspect Ratios
# ============================================================================

@pytest.fixture
def frame_16_9_hd():
    """Standard HD 16:9 landscape frame (1920x1080)."""
    return np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)


@pytest.fixture
def frame_4_3():
    """Classic 4:3 landscape frame (1024x768)."""
    return np.random.randint(0, 256, (768, 1024, 3), dtype=np.uint8)


@pytest.fixture
def frame_1_1_square():
    """Square 1:1 frame (1080x1080)."""
    return np.random.randint(0, 256, (1080, 1080, 3), dtype=np.uint8)


@pytest.fixture
def frame_21_9_ultrawide():
    """Ultra-wide 21:9 landscape frame (2560x1080)."""
    return np.random.randint(0, 256, (1080, 2560, 3), dtype=np.uint8)


@pytest.fixture
def frame_9_16_portrait():
    """Portrait 9:16 frame (1080x1920) - vertical video."""
    return np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)


@pytest.fixture
def frame_cinematic():
    """Cinematic 2.39:1 widescreen frame (2560x1070)."""
    return np.random.randint(0, 256, (1070, 2560, 3), dtype=np.uint8)


@pytest.fixture
def frame_small_16_9():
    """Small 16:9 frame (320x180) - for faster tests."""
    return np.random.randint(0, 256, (180, 320, 3), dtype=np.uint8)


@pytest.fixture
def frame_small_portrait():
    """Small portrait frame (180x320) - for faster tests."""
    return np.random.randint(0, 256, (320, 180, 3), dtype=np.uint8)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_output(result: np.ndarray, input_frame: np.ndarray) -> None:
    """Validate that effect output is valid and preserves dimensions."""
    assert result is not None, "Effect returned None"
    assert isinstance(result, np.ndarray), "Effect did not return numpy array"
    assert result.shape == input_frame.shape, \
        f"Effect changed frame shape from {input_frame.shape} to {result.shape}"
    assert result.dtype == np.uint8, \
        f"Effect changed frame dtype from uint8 to {result.dtype}"
    assert not np.isnan(result).any(), "Effect produced NaN values"
    assert np.all((result >= 0) & (result <= 255)), \
        "Effect produced values outside [0, 255] range"


def get_aspect_ratio_name(frame: np.ndarray) -> str:
    """Get human-readable aspect ratio name for a frame."""
    h, w = frame.shape[:2]
    ratio = w / h
    
    if abs(ratio - 16/9) < 0.01:
        return "16:9"
    elif abs(ratio - 4/3) < 0.01:
        return "4:3"
    elif abs(ratio - 1.0) < 0.01:
        return "1:1"
    elif abs(ratio - 21/9) < 0.01:
        return "21:9"
    elif abs(ratio - 9/16) < 0.01:
        return "9:16"
    elif abs(ratio - 2.39) < 0.01:
        return "2.39:1"
    else:
        return f"{ratio:.2f}:1"


# ============================================================================
# Color Effects - Aspect Ratio Tests
# ============================================================================

class TestColorEffectsAspectRatios:
    """Test color effects with various aspect ratios."""
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_16_9_hd",
        "frame_4_3",
        "frame_1_1_square",
        "frame_21_9_ultrawide",
        "frame_9_16_portrait",
        "frame_cinematic",
    ])
    def test_grayscale_all_aspect_ratios(self, frame_fixture, request):
        """Test grayscale effect with all aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = grayscale()
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
        
        # Verify grayscale property: all channels equal
        assert np.allclose(result[:, :, 0], result[:, :, 1], atol=1)
        assert np.allclose(result[:, :, 1], result[:, :, 2], atol=1)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_16_9_hd",
        "frame_4_3",
        "frame_1_1_square",
        "frame_21_9_ultrawide",
        "frame_9_16_portrait",
        "frame_cinematic",
    ])
    def test_sepia_all_aspect_ratios(self, frame_fixture, request):
        """Test sepia effect with all aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = sepia()
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_hue_shift_aspect_ratios(self, frame_fixture, request):
        """Test hue shift with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = hue_shift(120)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_gamma_correction_aspect_ratios(self, frame_fixture, request):
        """Test gamma correction with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = gamma_correction(1.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_posterize_aspect_ratios(self, frame_fixture, request):
        """Test posterize with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = posterize(4)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_vibrance_aspect_ratios(self, frame_fixture, request):
        """Test vibrance with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = vibrance(0.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)


# ============================================================================
# Blur Effects - Aspect Ratio Tests
# ============================================================================

class TestBlurEffectsAspectRatios:
    """Test blur effects with various aspect ratios."""
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_box_blur_aspect_ratios(self, frame_fixture, request):
        """Test box blur with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = box_blur(5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_gaussian_blur_aspect_ratios(self, frame_fixture, request):
        """Test gaussian blur with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = gaussian_blur(5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture,angle", [
        ("frame_small_16_9", 0),    # Horizontal blur on landscape
        ("frame_small_16_9", 90),   # Vertical blur on landscape
        ("frame_small_portrait", 0),  # Horizontal blur on portrait
        ("frame_small_portrait", 90), # Vertical blur on portrait
    ])
    def test_motion_blur_aspect_ratios(self, frame_fixture, angle, request):
        """Test motion blur with different aspect ratios and angles."""
        frame = request.getfixturevalue(frame_fixture)
        effect = motion_blur(angle=angle, amount=10)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_radial_blur_aspect_ratios(self, frame_fixture, request):
        """Test radial blur with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = radial_blur(0.3)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_pixelate_aspect_ratios(self, frame_fixture, request):
        """Test pixelate with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = pixelate(8)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_sharpen_aspect_ratios(self, frame_fixture, request):
        """Test sharpen with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = sharpen(1.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)


# ============================================================================
# Texture Effects - Aspect Ratio Tests
# ============================================================================

class TestTextureEffectsAspectRatios:
    """Test texture effects with various aspect ratios."""
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_scan_lines_aspect_ratios(self, frame_fixture, request):
        """Test scan lines with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = scan_lines(spacing=2, intensity=0.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_16_9_hd",
        "frame_4_3",
        "frame_1_1_square",
        "frame_21_9_ultrawide",
        "frame_9_16_portrait",
        "frame_cinematic",
    ])
    def test_letterbox_all_aspect_ratios(self, frame_fixture, request):
        """Test letterbox with all aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        h = frame.shape[0]
        bar_height = int(h * 0.1)  # 10% bars
        effect = letterbox(bar_height, bar_height, (0, 0, 0))
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
        
        # Verify letterbox bars are black
        assert np.all(result[:bar_height, :, :] == 0), "Top bar not black"
        assert np.all(result[-bar_height:, :, :] == 0), "Bottom bar not black"
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_16_9_hd",
        "frame_4_3",
        "frame_1_1_square",
        "frame_21_9_ultrawide",
        "frame_9_16_portrait",
        "frame_cinematic",
    ])
    def test_vignette_all_aspect_ratios(self, frame_fixture, request):
        """Test vignette with all aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = vignette_simple(0.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture,direction", [
        ("frame_small_16_9", "vertical"),
        ("frame_small_16_9", "horizontal"),
        ("frame_small_portrait", "vertical"),
        ("frame_small_portrait", "horizontal"),
    ])
    def test_gradient_overlay_aspect_ratios(self, frame_fixture, direction, request):
        """Test gradient overlay with different aspect ratios and directions."""
        frame = request.getfixturevalue(frame_fixture)
        effect = gradient_overlay(
            (255, 0, 0), (0, 0, 255), direction, 0.5
        )
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_border_aspect_ratios(self, frame_fixture, request):
        """Test border with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = border(10, (255, 0, 0))
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_light_leak_aspect_ratios(self, frame_fixture, request):
        """Test light leak with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = light_leak(0.5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)


# ============================================================================
# Stylization Effects - Aspect Ratio Tests
# ============================================================================

class TestStylizationEffectsAspectRatios:
    """Test stylization effects with various aspect ratios."""
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_chromatic_aberration_aspect_ratios(self, frame_fixture, request):
        """Test chromatic aberration with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = chromatic_aberration(5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_glitch_rgb_split_aspect_ratios(self, frame_fixture, request):
        """Test glitch RGB split with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = glitch_rgb_split(max_offset=10)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_glitch_block_displacement_aspect_ratios(self, frame_fixture, request):
        """Test glitch block displacement with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = glitch_block_displacement(block_size=10, displacement=5)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_threshold_bw_aspect_ratios(self, frame_fixture, request):
        """Test threshold B&W with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = threshold_bw(128)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_halftone_aspect_ratios(self, frame_fixture, request):
        """Test halftone with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = halftone(4)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)
    
    @pytest.mark.parametrize("frame_fixture", [
        "frame_small_16_9",
        "frame_small_portrait",
    ])
    def test_crt_retro_aspect_ratios(self, frame_fixture, request):
        """Test CRT retro with different aspect ratios."""
        frame = request.getfixturevalue(frame_fixture)
        effect = crt_retro(0.3)
        result = effect(frame, t=0.5, progress=0.5)
        validate_output(result, frame)


# ============================================================================
# Comprehensive Aspect Ratio Tests
# ============================================================================

class TestAllEffectsWithAspectRatios:
    """Comprehensive tests of all effect categories with aspect ratios."""
    
    def test_landscape_vs_portrait_color_effects(
        self, frame_small_16_9, frame_small_portrait
    ):
        """Test that color effects work identically on landscape and portrait."""
        effects = [
            grayscale(),
            sepia(),
            posterize(4),
        ]
        
        for effect in effects:
            # Test landscape
            result_landscape = effect(frame_small_16_9, t=0.5, progress=0.5)
            validate_output(result_landscape, frame_small_16_9)
            
            # Test portrait
            result_portrait = effect(frame_small_portrait, t=0.5, progress=0.5)
            validate_output(result_portrait, frame_small_portrait)
    
    def test_landscape_vs_portrait_blur_effects(
        self, frame_small_16_9, frame_small_portrait
    ):
        """Test that blur effects work on both landscape and portrait."""
        effects = [
            box_blur(5),
            gaussian_blur(5),
            pixelate(8),
        ]
        
        for effect in effects:
            # Test landscape
            result_landscape = effect(frame_small_16_9, t=0.5, progress=0.5)
            validate_output(result_landscape, frame_small_16_9)
            
            # Test portrait
            result_portrait = effect(frame_small_portrait, t=0.5, progress=0.5)
            validate_output(result_portrait, frame_small_portrait)
    
    def test_extreme_aspect_ratios(self):
        """Test effects with extreme aspect ratios."""
        # Very wide (32:9)
        very_wide = np.random.randint(0, 256, (270, 960, 3), dtype=np.uint8)
        
        # Very tall (9:32)
        very_tall = np.random.randint(0, 256, (960, 270, 3), dtype=np.uint8)
        
        effects = [
            grayscale(),
            box_blur(5),
            vignette_simple(0.5),
            threshold_bw(128),
        ]
        
        for effect in effects:
            # Test very wide
            result_wide = effect(very_wide, t=0.5, progress=0.5)
            validate_output(result_wide, very_wide)
            
            # Test very tall
            result_tall = effect(very_tall, t=0.5, progress=0.5)
            validate_output(result_tall, very_tall)
    
    def test_square_frame_symmetry(self, frame_1_1_square):
        """Test that effects on square frames maintain symmetry where expected."""
        # Effects that should be symmetric on square frames
        effect = vignette_simple(0.5)
        result = effect(frame_1_1_square, t=0.5, progress=0.5)
        validate_output(result, frame_1_1_square)
        
        # For vignette, corners should have similar darkness
        h, w = result.shape[:2]
        corner_tl = result[0:10, 0:10, :].mean()
        corner_tr = result[0:10, -10:, :].mean()
        corner_bl = result[-10:, 0:10, :].mean()
        corner_br = result[-10:, -10:, :].mean()
        
        # All corners should be similar (within tolerance)
        corners = [corner_tl, corner_tr, corner_bl, corner_br]
        assert max(corners) - min(corners) < 20, \
            "Vignette corners not symmetric on square frame"


# ============================================================================
# Edge Case Aspect Ratio Tests
# ============================================================================

class TestEdgeCaseAspectRatios:
    """Test effects with edge case aspect ratios."""
    
    def test_very_narrow_frame(self):
        """Test effects on very narrow frame (1:10 aspect ratio)."""
        narrow_frame = np.random.randint(0, 256, (100, 10, 3), dtype=np.uint8)
        
        effects = [
            grayscale(),
            box_blur(3),
            scan_lines(2, 0.5),
            threshold_bw(128),
        ]
        
        for effect in effects:
            result = effect(narrow_frame, t=0.5, progress=0.5)
            validate_output(result, narrow_frame)
    
    def test_very_wide_frame(self):
        """Test effects on very wide frame (10:1 aspect ratio)."""
        wide_frame = np.random.randint(0, 256, (10, 100, 3), dtype=np.uint8)
        
        effects = [
            grayscale(),
            box_blur(3),
            vignette_simple(0.5),
            threshold_bw(128),
        ]
        
        for effect in effects:
            result = effect(wide_frame, t=0.5, progress=0.5)
            validate_output(result, wide_frame)
    
    def test_non_standard_resolutions(self):
        """Test effects with non-standard resolutions."""
        # Odd dimensions
        odd_frame = np.random.randint(0, 256, (333, 555, 3), dtype=np.uint8)
        
        # Prime number dimensions
        prime_frame = np.random.randint(0, 256, (127, 251, 3), dtype=np.uint8)
        
        effects = [
            grayscale(),
            pixelate(5),
            vignette_simple(0.5),
        ]
        
        for effect in effects:
            result_odd = effect(odd_frame, t=0.5, progress=0.5)
            validate_output(result_odd, odd_frame)
            
            result_prime = effect(prime_frame, t=0.5, progress=0.5)
            validate_output(result_prime, prime_frame)


# ============================================================================
# Performance Tests with Different Aspect Ratios
# ============================================================================

class TestAspectRatioPerformance:
    """Test that effects scale reasonably with different aspect ratios."""
    
    def test_effect_scales_with_pixel_count(self):
        """Verify effects handle different pixel counts appropriately."""
        # Small frame (57,600 pixels)
        small = np.random.randint(0, 256, (180, 320, 3), dtype=np.uint8)
        
        # Medium frame (230,400 pixels - 4x small)
        medium = np.random.randint(0, 256, (360, 640, 3), dtype=np.uint8)
        
        # Large frame (921,600 pixels - 16x small)
        large = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
        
        # Test a representative effect
        effect = box_blur(5)
        
        # All should complete without error
        result_small = effect(small, t=0.5, progress=0.5)
        validate_output(result_small, small)
        
        result_medium = effect(medium, t=0.5, progress=0.5)
        validate_output(result_medium, medium)
        
        result_large = effect(large, t=0.5, progress=0.5)
        validate_output(result_large, large)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
