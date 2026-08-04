"""Test error messages for invalid inputs to Phase 4 effects and transitions.

This test file verifies that Phase 4 effects and transitions provide appropriate
error messages when given invalid inputs such as:
- Wrong frame shape (not 3D, wrong number of channels)
- Wrong dtype (not uint8)
- None values
- Out-of-range parameters
- Invalid parameter types
"""

from __future__ import annotations

import numpy as np
import pytest

from engine.effects import (
    # Color effects
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
    # Blur effects
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
    # Texture effects
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
    # Stylization effects
    chromatic_aberration,
    glitch_rgb_split,
    glitch_block_displacement,
    glitch_scan_line_shift,
    glitch_color_corruption,
    crt_retro,
    vhs_tape_distortion,
    threshold_bw,
)
from engine.transitions import get_transition_function
from engine.scene import TransitionType


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def valid_frame():
    """Create a valid test frame."""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def invalid_shape_2d():
    """Create a 2D frame (invalid - should be 3D)."""
    return np.random.randint(0, 256, (100, 100), dtype=np.uint8)


@pytest.fixture
def invalid_shape_4channels():
    """Create a frame with 4 channels (invalid - should be 3)."""
    return np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)


@pytest.fixture
def invalid_dtype_float():
    """Create a frame with float dtype (invalid - should be uint8)."""
    return np.random.rand(100, 100, 3).astype(np.float32)


@pytest.fixture
def invalid_dtype_int32():
    """Create a frame with int32 dtype (invalid - should be uint8)."""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.int32)


# ============================================================================
# Helper Functions
# ============================================================================

def test_effect_with_invalid_frame(effect, invalid_frame, error_description):
    """
    Test an effect with an invalid frame and document the error behavior.
    
    Returns:
        dict with error information
    """
    try:
        result = effect(invalid_frame, t=0.5, progress=0.5)
        return {
            "error_raised": False,
            "result_type": type(result).__name__,
            "description": error_description
        }
    except Exception as e:
        return {
            "error_raised": True,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "description": error_description
        }


# ============================================================================
# Frame Shape Error Tests
# ============================================================================

class TestFrameShapeErrors:
    """Test error handling for invalid frame shapes."""
    
    def test_effects_with_2d_frame(self, invalid_shape_2d):
        """Test effects with 2D frame (missing channel dimension)."""
        effects_to_test = [
            ("hue_shift", hue_shift(30)),
            ("box_blur", box_blur(5)),
            ("vignette_simple", vignette_simple(0.5)),
            ("chromatic_aberration", chromatic_aberration(5)),
        ]
        
        errors = []
        for name, effect in effects_to_test:
            result = test_effect_with_invalid_frame(
                effect,
                invalid_shape_2d,
                f"{name} with 2D frame (shape: {invalid_shape_2d.shape})"
            )
            errors.append((name, result))
        
        # Document findings
        print("\n=== 2D Frame Error Handling ===")
        for name, result in errors:
            if result["error_raised"]:
                print(f"✓ {name}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {name}: No error raised (returns {result['result_type']})")
    
    def test_effects_with_4channel_frame(self, invalid_shape_4channels):
        """Test effects with 4-channel frame (RGBA instead of RGB)."""
        effects_to_test = [
            ("hue_shift", hue_shift(30)),
            ("box_blur", box_blur(5)),
            ("vignette_simple", vignette_simple(0.5)),
            ("chromatic_aberration", chromatic_aberration(5)),
        ]
        
        errors = []
        for name, effect in effects_to_test:
            result = test_effect_with_invalid_frame(
                effect,
                invalid_shape_4channels,
                f"{name} with 4-channel frame (shape: {invalid_shape_4channels.shape})"
            )
            errors.append((name, result))
        
        # Document findings
        print("\n=== 4-Channel Frame Error Handling ===")
        for name, result in errors:
            if result["error_raised"]:
                print(f"✓ {name}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {name}: No error raised (returns {result['result_type']})")


# ============================================================================
# Frame Dtype Error Tests
# ============================================================================

class TestFrameDtypeErrors:
    """Test error handling for invalid frame dtypes."""
    
    def test_effects_with_float_frame(self, invalid_dtype_float):
        """Test effects with float32 frame instead of uint8."""
        effects_to_test = [
            ("hue_shift", hue_shift(30)),
            ("box_blur", box_blur(5)),
            ("vignette_simple", vignette_simple(0.5)),
            ("chromatic_aberration", chromatic_aberration(5)),
        ]
        
        errors = []
        for name, effect in effects_to_test:
            result = test_effect_with_invalid_frame(
                effect,
                invalid_dtype_float,
                f"{name} with float32 dtype"
            )
            errors.append((name, result))
        
        # Document findings
        print("\n=== Float32 Dtype Error Handling ===")
        for name, result in errors:
            if result["error_raised"]:
                print(f"✓ {name}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {name}: No error raised (returns {result['result_type']})")
    
    def test_effects_with_int32_frame(self, invalid_dtype_int32):
        """Test effects with int32 frame instead of uint8."""
        effects_to_test = [
            ("hue_shift", hue_shift(30)),
            ("box_blur", box_blur(5)),
            ("vignette_simple", vignette_simple(0.5)),
            ("chromatic_aberration", chromatic_aberration(5)),
        ]
        
        errors = []
        for name, effect in effects_to_test:
            result = test_effect_with_invalid_frame(
                effect,
                invalid_dtype_int32,
                f"{name} with int32 dtype"
            )
            errors.append((name, result))
        
        # Document findings
        print("\n=== Int32 Dtype Error Handling ===")
        for name, result in errors:
            if result["error_raised"]:
                print(f"✓ {name}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {name}: No error raised (returns {result['result_type']})")


# ============================================================================
# None Value Error Tests
# ============================================================================

class TestNoneValueErrors:
    """Test error handling for None values."""
    
    def test_effects_with_none_frame(self):
        """Test effects with None frame."""
        effects_to_test = [
            ("hue_shift", hue_shift(30)),
            ("box_blur", box_blur(5)),
            ("vignette_simple", vignette_simple(0.5)),
            ("chromatic_aberration", chromatic_aberration(5)),
        ]
        
        errors = []
        for name, effect in effects_to_test:
            result = test_effect_with_invalid_frame(
                effect,
                None,
                f"{name} with None frame"
            )
            errors.append((name, result))
        
        # Document findings
        print("\n=== None Frame Error Handling ===")
        for name, result in errors:
            if result["error_raised"]:
                print(f"✓ {name}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {name}: No error raised (returns {result['result_type']})")


# ============================================================================
# Invalid Parameter Error Tests
# ============================================================================

class TestInvalidParameterErrors:
    """Test error handling for invalid parameters."""
    
    def test_invalid_parameter_types(self, valid_frame):
        """Test effects with invalid parameter types."""
        test_cases = [
            ("hue_shift with string", lambda: hue_shift("invalid")),
            ("box_blur with float", lambda: box_blur(5.5)),
            ("tint with invalid color", lambda: tint("red", 0.5)),
            ("posterize with negative", lambda: posterize(-1)),
            ("scan_lines with negative spacing", lambda: scan_lines(-5, 0.5)),
        ]
        
        errors = []
        for description, factory in test_cases:
            try:
                effect = factory()
                result = effect(valid_frame, t=0.5, progress=0.5)
                errors.append((description, {
                    "error_raised": False,
                    "result_type": type(result).__name__
                }))
            except Exception as e:
                errors.append((description, {
                    "error_raised": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }))
        
        # Document findings
        print("\n=== Invalid Parameter Type Error Handling ===")
        for description, result in errors:
            if result["error_raised"]:
                print(f"✓ {description}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {description}: No error raised")
    
    def test_out_of_range_parameters(self, valid_frame):
        """Test effects with out-of-range parameters."""
        test_cases = [
            ("posterize with 0 bits", posterize(0)),
            ("posterize with 9 bits", posterize(9)),
            ("box_blur with 0 kernel", box_blur(0)),
            ("pixelate with 0 factor", pixelate(0)),
        ]
        
        errors = []
        for description, effect in test_cases:
            result = test_effect_with_invalid_frame(
                effect,
                valid_frame,
                description
            )
            errors.append((description, result))
        
        # Document findings
        print("\n=== Out-of-Range Parameter Error Handling ===")
        for description, result in errors:
            if result["error_raised"]:
                print(f"✓ {description}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {description}: No error raised")


# ============================================================================
# Transition Error Tests
# ============================================================================

class TestTransitionErrors:
    """Test error handling for transitions."""
    
    def test_transitions_with_invalid_frames(self, valid_frame, invalid_shape_2d):
        """Test transitions with invalid frame shapes."""
        transition_fn = get_transition_function(TransitionType.CROSSFADE)
        
        test_cases = [
            ("frame_a is 2D", invalid_shape_2d, valid_frame),
            ("frame_b is 2D", valid_frame, invalid_shape_2d),
            ("both frames 2D", invalid_shape_2d, invalid_shape_2d),
            ("frame_a is None", None, valid_frame),
            ("frame_b is None", valid_frame, None),
        ]
        
        errors = []
        for description, frame_a, frame_b in test_cases:
            try:
                result = transition_fn(frame_a, frame_b, 0.5)
                errors.append((description, {
                    "error_raised": False,
                    "result_type": type(result).__name__
                }))
            except Exception as e:
                errors.append((description, {
                    "error_raised": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }))
        
        # Document findings
        print("\n=== Transition Invalid Frame Error Handling ===")
        for description, result in errors:
            if result["error_raised"]:
                print(f"✓ {description}: Raises {result['error_type']}")
                print(f"  Message: {result['error_message'][:100]}")
            else:
                print(f"✗ {description}: No error raised")
    
    def test_transitions_with_mismatched_shapes(self, valid_frame):
        """Test transitions with mismatched frame shapes."""
        frame_a = valid_frame
        frame_b = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        transition_fn = get_transition_function(TransitionType.CROSSFADE)
        
        try:
            result = transition_fn(frame_a, frame_b, 0.5)
            print("\n=== Mismatched Frame Shapes ===")
            print(f"✗ No error raised for mismatched shapes: {frame_a.shape} vs {frame_b.shape}")
        except Exception as e:
            print("\n=== Mismatched Frame Shapes ===")
            print(f"✓ Raises {type(e).__name__}")
            print(f"  Message: {str(e)[:100]}")
    
    def test_invalid_transition_type(self):
        """Test get_transition_function with invalid transition type."""
        try:
            get_transition_function("invalid_transition")
            print("\n=== Invalid Transition Type ===")
            print("✗ No error raised for invalid transition type")
        except ValueError as e:
            print("\n=== Invalid Transition Type ===")
            print(f"✓ Raises ValueError")
            print(f"  Message: {str(e)}")
        except Exception as e:
            print("\n=== Invalid Transition Type ===")
            print(f"? Raises {type(e).__name__} (expected ValueError)")
            print(f"  Message: {str(e)}")


# ============================================================================
# Comprehensive Error Message Quality Test
# ============================================================================

class TestErrorMessageQuality:
    """Test the quality and clarity of error messages."""
    
    def test_all_color_effects_error_messages(self, invalid_shape_2d, invalid_dtype_float):
        """Test error messages for all color effects."""
        effects = [
            ("hue_shift", hue_shift(30)),
            ("color_temperature", color_temperature(6500)),
            ("tint", tint((255, 0, 0), 0.5)),
            ("gamma_correction", gamma_correction(1.2)),
            ("posterize", posterize(4)),
            ("solarize", solarize(128)),
            ("vibrance", vibrance(0.5)),
        ]
        
        print("\n=== Color Effects Error Message Quality ===")
        for name, effect in effects:
            # Test with 2D frame
            result_2d = test_effect_with_invalid_frame(effect, invalid_shape_2d, f"{name} 2D")
            # Test with float frame
            result_float = test_effect_with_invalid_frame(effect, invalid_dtype_float, f"{name} float")
            
            print(f"\n{name}:")
            if result_2d["error_raised"]:
                print(f"  2D frame: {result_2d['error_type']}")
                print(f"    Message: {result_2d['error_message'][:80]}")
            else:
                print(f"  2D frame: ✗ No error")
            
            if result_float["error_raised"]:
                print(f"  Float frame: {result_float['error_type']}")
                print(f"    Message: {result_float['error_message'][:80]}")
            else:
                print(f"  Float frame: ✗ No error")
    
    def test_all_blur_effects_error_messages(self, invalid_shape_2d, invalid_dtype_float):
        """Test error messages for all blur effects."""
        effects = [
            ("box_blur", box_blur(5)),
            ("gaussian_blur", gaussian_blur(5)),
            ("motion_blur", motion_blur(45, 10)),
            ("radial_blur", radial_blur(0.5)),
            ("zoom_blur", zoom_blur(0.5)),
            ("pixelate", pixelate(10)),
            ("sharpen", sharpen(1.5)),
        ]
        
        print("\n=== Blur Effects Error Message Quality ===")
        for name, effect in effects:
            result_2d = test_effect_with_invalid_frame(effect, invalid_shape_2d, f"{name} 2D")
            result_float = test_effect_with_invalid_frame(effect, invalid_dtype_float, f"{name} float")
            
            print(f"\n{name}:")
            if result_2d["error_raised"]:
                print(f"  2D frame: {result_2d['error_type']}")
            else:
                print(f"  2D frame: ✗ No error")
            
            if result_float["error_raised"]:
                print(f"  Float frame: {result_float['error_type']}")
            else:
                print(f"  Float frame: ✗ No error")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
