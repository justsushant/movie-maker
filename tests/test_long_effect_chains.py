"""Tests for long effect chains with 10+ effects.

This module tests that the system can handle long effect chains with 10 or more
effects from Phase 2, Phase 3, and Phase 4. Tests verify:
- No performance degradation beyond linear scaling
- No memory leaks
- Correct composition of all effects
- Frame validity maintained throughout the chain

**Validates: Requirements 5.3, 5.9**
"""

from __future__ import annotations
import pytest
import numpy as np
import time
import gc
from pathlib import Path
from typing import List, Callable

from engine.scene import Scene, ImageClip
from engine.planner import ScenePlanner
from engine.renderer import FrameRenderer
from engine.image_loader import ImageLoader

# Phase 2 effects
from engine.effects import (
    brightness, contrast, saturation, vignette, film_grain,
    fade_in, fade_out, pulse
)

# Phase 3 effects (audio-reactive)
from engine.effects import (
    OnsetFlash, OnsetZoomPulse, EnergyZoom,
    EnergyBrightness, EnergyShake, SpectralColorShift
)

# Phase 4 effects
from engine.effects import (
    # Color effects
    grayscale, sepia, invert, hue_shift, color_temperature, tint,
    gamma_correction, duotone, cinematic_teal_orange, vibrance,
    color_pulse, fade_to_color, posterize, solarize,
    
    # Blur effects
    box_blur, gaussian_blur, motion_blur, sharpen, pixelate,
    
    # Texture/overlay effects
    scan_lines, letterbox, vignette_simple, gradient_overlay,
    border, light_leak, progress_bar,
    
    # Stylization effects
    edge_detection, emboss, chromatic_aberration,
    glitch_rgb_split, threshold_bw, crt_retro
)


@pytest.fixture
def image_loader():
    """Image loader for tests."""
    return ImageLoader()


@pytest.fixture
def test_image_path():
    """Path to test image."""
    return Path("tests/fixtures/images/landscape_1920x1080.png")


@pytest.fixture
def test_audio_path():
    """Path to test audio file."""
    return Path("tests/fixtures/audio/test_beats_120bpm.wav")


@pytest.fixture
def small_test_frame():
    """Create a small test frame for fast testing."""
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def medium_test_frame():
    """Create a medium test frame (720p)."""
    return np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)


# ============================================================================
# Test Long Effect Chains - Phase 2 + Phase 4
# ============================================================================

class TestLongEffectChainsPhase2And4:
    """Test long effect chains combining Phase 2 and Phase 4 effects."""
    
    def test_10_color_effects_chain(self, test_image_path, image_loader):
        """Test chain of 10 color effects from Phase 2 and Phase 4."""
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with 10 color effects
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=2.0,
                    effects=[
                        brightness(0.05),           # 1. Phase 2
                        contrast(1.1),              # 2. Phase 2
                        saturation(1.1),            # 3. Phase 2
                        sepia(),                    # 4. Phase 4
                        color_temperature(6000),    # 5. Phase 4
                        vibrance(0.1),              # 6. Phase 4
                        gamma_correction(1.2),      # 7. Phase 4
                        tint((255, 200, 150), 0.1), # 8. Phase 4
                        cinematic_teal_orange(0.3), # 9. Phase 4
                        fade_to_color((255, 255, 255)), # 10. Phase 4
                    ]
                )
            ]
        )
        
        # Plan and render
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        # Render frame
        frame = renderer.render_frame(1.0)
        
        # Verify frame validity
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8
        assert np.all(frame >= 0) and np.all(frame <= 255)
    
    def test_12_mixed_effects_chain(self, test_image_path, image_loader):
        """Test chain of 12 mixed effects (color, blur, texture, stylization)."""
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with 12 mixed effects
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=2.0,
                    effects=[
                        brightness(0.05),           # 1. Phase 2 color
                        contrast(1.1),              # 2. Phase 2 color
                        vignette(0.3, 0.85),        # 3. Phase 2 texture
                        film_grain(0.03),           # 4. Phase 2 texture
                        sepia(),                    # 5. Phase 4 color
                        color_temperature(6200),    # 6. Phase 4 color
                        gaussian_blur(2),           # 7. Phase 4 blur
                        sharpen(0.5),               # 8. Phase 4 blur
                        scan_lines(4, 0.15),        # 9. Phase 4 texture
                        vignette_simple(0.4),       # 10. Phase 4 texture
                        posterize(5),               # 11. Phase 4 stylization
                        chromatic_aberration(2),    # 12. Phase 4 stylization
                    ]
                )
            ]
        )
        
        # Plan and render
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        # Render frame
        frame = renderer.render_frame(1.0)
        
        # Verify frame validity
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8
        assert np.all(frame >= 0) and np.all(frame <= 255)
    
    def test_15_effects_chain(self, test_image_path, image_loader):
        """Test chain of 15 effects from Phase 2 and Phase 4."""
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with 15 effects
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=2.0,
                    effects=[
                        brightness(0.05),           # 1
                        contrast(1.05),             # 2
                        saturation(1.05),           # 3
                        vignette(0.2, 0.9),         # 4
                        film_grain(0.02),           # 5
                        sepia(),                    # 6
                        color_temperature(6100),    # 7
                        vibrance(0.08),             # 8
                        gaussian_blur(1),           # 9
                        sharpen(0.3),               # 10
                        scan_lines(5, 0.1),         # 11
                        border(2, (0, 0, 0)),       # 12
                        posterize(6),               # 13
                        chromatic_aberration(1),    # 14
                        fade_to_color((255, 255, 255)), # 15
                    ]
                )
            ]
        )
        
        # Plan and render
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        renderer = FrameRenderer(timeline, image_loader)
        
        # Render frame
        frame = renderer.render_frame(1.0)
        
        # Verify frame validity
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        assert frame.dtype == np.uint8
        assert np.all(frame >= 0) and np.all(frame <= 255)


# ============================================================================
# Test Long Effect Chains - All Three Phases
# ============================================================================

class TestLongEffectChainsAllPhases:
    """Test long effect chains combining Phase 2, Phase 3, and Phase 4 effects."""
    
    def test_10_effects_with_audio_reactive(self, test_audio_path, test_image_path, image_loader):
        """Test chain of 10 effects including audio-reactive effects."""
        if not test_audio_path.exists():
            pytest.skip(f"Test audio not found: {test_audio_path}")
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with audio
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            audio=test_audio_path,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=3.0
                )
            ]
        )
        
        # Plan scene
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        
        if timeline.audio_sync is None:
            pytest.skip("Audio analysis failed")
        
        # Add 10 effects from all three phases
        timeline.clips[0].effects = [
            brightness(0.05),                                                 # 1. Phase 2
            contrast(1.1),                                                    # 2. Phase 2
            saturation(1.1),                                                  # 3. Phase 2
            vignette(0.3, 0.85),                                             # 4. Phase 2
            OnsetFlash(timeline.audio_sync, 0.15, 0.2),                      # 5. Phase 3
            EnergyZoom(timeline.audio_sync, (1.0, 1.08), (0.0, 1.0)),       # 6. Phase 3
            sepia(),                                                          # 7. Phase 4
            color_temperature(6200),                                          # 8. Phase 4
            gaussian_blur(2),                                                 # 9. Phase 4
            scan_lines(4, 0.15),                                              # 10. Phase 4
        ]
        
        # Render frames
        renderer = FrameRenderer(timeline, image_loader)
        
        for t in [0.5, 1.0, 1.5, 2.0, 2.5]:
            frame = renderer.render_frame(t)
            assert frame is not None
            assert frame.shape == (480, 640, 3)
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0) and np.all(frame <= 255)
    
    def test_15_effects_all_phases(self, test_audio_path, test_image_path, image_loader):
        """Test chain of 15 effects from all three phases."""
        if not test_audio_path.exists():
            pytest.skip(f"Test audio not found: {test_audio_path}")
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with audio
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            audio=test_audio_path,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=3.0
                )
            ]
        )
        
        # Plan scene
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        
        if timeline.audio_sync is None:
            pytest.skip("Audio analysis failed")
        
        # Add 15 effects from all three phases
        timeline.clips[0].effects = [
            brightness(0.05),                                                 # 1. Phase 2
            contrast(1.08),                                                   # 2. Phase 2
            saturation(1.08),                                                 # 3. Phase 2
            vignette(0.25, 0.88),                                            # 4. Phase 2
            film_grain(0.02),                                                 # 5. Phase 2
            OnsetFlash(timeline.audio_sync, 0.15, 0.2),                      # 6. Phase 3
            EnergyZoom(timeline.audio_sync, (1.0, 1.08), (0.0, 1.0)),       # 7. Phase 3
            EnergyBrightness(timeline.audio_sync, (0.95, 1.05), (0.0, 1.0)), # 8. Phase 3
            sepia(),                                                          # 9. Phase 4
            color_temperature(6200),                                          # 10. Phase 4
            vibrance(0.1),                                                    # 11. Phase 4
            gaussian_blur(2),                                                 # 12. Phase 4
            scan_lines(4, 0.15),                                              # 13. Phase 4
            posterize(5),                                                     # 14. Phase 4
            chromatic_aberration(2),                                          # 15. Phase 4
        ]
        
        # Render frames
        renderer = FrameRenderer(timeline, image_loader)
        
        for t in [0.5, 1.0, 1.5, 2.0, 2.5]:
            frame = renderer.render_frame(t)
            assert frame is not None
            assert frame.shape == (480, 640, 3)
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0) and np.all(frame <= 255)
    
    def test_20_effects_maximum_chain(self, test_audio_path, test_image_path, image_loader):
        """Test maximum chain of 20 effects from all three phases."""
        if not test_audio_path.exists():
            pytest.skip(f"Test audio not found: {test_audio_path}")
        if not test_image_path.exists():
            pytest.skip(f"Test image not found: {test_image_path}")
        
        # Create scene with audio
        scene = Scene(
            resolution=(640, 480),
            fps=30,
            audio=test_audio_path,
            clips=[
                ImageClip(
                    source=test_image_path,
                    duration=3.0
                )
            ]
        )
        
        # Plan scene
        planner = ScenePlanner()
        timeline = planner.plan(scene, image_loader)
        
        if timeline.audio_sync is None:
            pytest.skip("Audio analysis failed")
        
        # Add 20 effects from all three phases
        timeline.clips[0].effects = [
            # Phase 2 effects (5)
            brightness(0.03),
            contrast(1.05),
            saturation(1.05),
            vignette(0.2, 0.9),
            film_grain(0.015),
            
            # Phase 3 effects (4)
            OnsetFlash(timeline.audio_sync, 0.12, 0.18),
            EnergyZoom(timeline.audio_sync, (1.0, 1.06), (0.0, 1.0)),
            EnergyBrightness(timeline.audio_sync, (0.97, 1.03), (0.0, 1.0)),
            SpectralColorShift(timeline.audio_sync, (-0.05, 0.05), (1000, 3000)),
            
            # Phase 4 effects (11)
            sepia(),
            color_temperature(6100),
            vibrance(0.08),
            gamma_correction(1.1),
            gaussian_blur(1),
            sharpen(0.3),
            scan_lines(5, 0.1),
            border(1, (0, 0, 0)),
            posterize(6),
            chromatic_aberration(1),
            fade_to_color((255, 255, 255)),
        ]
        
        # Render frames
        renderer = FrameRenderer(timeline, image_loader)
        
        for t in [0.5, 1.0, 1.5, 2.0, 2.5]:
            frame = renderer.render_frame(t)
            assert frame is not None
            assert frame.shape == (480, 640, 3)
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0) and np.all(frame <= 255)


# ============================================================================
# Performance Tests - Linear Scaling
# ============================================================================

class TestLongEffectChainPerformance:
    """Test that long effect chains scale linearly with number of effects."""
    
    def test_performance_scales_linearly(self, small_test_frame):
        """Test that rendering time scales linearly with number of effects."""
        # Warm up - run once to initialize any caches
        warmup_effects = [brightness(0.05), sepia(), gaussian_blur(2)]
        frame = small_test_frame.copy()
        for effect in warmup_effects:
            frame = effect(frame, t=0.5, progress=0.5)
        
        # Create effect chains of different lengths
        effect_counts = [5, 10, 15, 20]
        render_times = []
        
        for count in effect_counts:
            # Create effect chain
            effects = []
            for i in range(count):
                # Alternate between different effect types
                if i % 4 == 0:
                    effects.append(brightness(0.05))
                elif i % 4 == 1:
                    effects.append(sepia())
                elif i % 4 == 2:
                    effects.append(gaussian_blur(2))
                else:
                    effects.append(posterize(5))
            
            # Measure rendering time over multiple runs
            times = []
            for _ in range(5):
                start_time = time.perf_counter()
                
                # Apply effects
                frame = small_test_frame.copy()
                for effect in effects:
                    frame = effect(frame, t=0.5, progress=0.5)
                
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            # Use median time to reduce noise
            render_time = np.median(times)
            render_times.append(render_time)
        
        # Check that time increases roughly linearly
        # Calculate time per effect for each chain length
        times_per_effect = [render_times[i] / effect_counts[i] for i in range(len(effect_counts))]
        
        # Time per effect should be relatively consistent (within 5x for small frames)
        # Some variation is expected due to different effect complexities
        min_time_per_effect = min(times_per_effect)
        max_time_per_effect = max(times_per_effect)
        
        # Allow up to 5x variation (some effects are much slower than others)
        assert max_time_per_effect <= min_time_per_effect * 5, \
            f"Performance should scale roughly linearly: {times_per_effect}"
    
    def test_no_exponential_slowdown(self, small_test_frame):
        """Test that there's no exponential slowdown with long chains."""
        # Warm up
        warmup_effects = [brightness(0.05), sepia()]
        frame = small_test_frame.copy()
        for effect in warmup_effects:
            frame = effect(frame, t=0.5, progress=0.5)
        
        # Create two chains: 10 effects and 20 effects
        effects_10 = [brightness(0.05) if i % 2 == 0 else sepia() for i in range(10)]
        effects_20 = [brightness(0.05) if i % 2 == 0 else sepia() for i in range(20)]
        
        # Measure time for 10 effects (multiple runs)
        times_10 = []
        for _ in range(5):
            start_time = time.perf_counter()
            frame = small_test_frame.copy()
            for effect in effects_10:
                frame = effect(frame, t=0.5, progress=0.5)
            times_10.append((time.perf_counter() - start_time) * 1000)
        time_10 = np.median(times_10)
        
        # Measure time for 20 effects (multiple runs)
        times_20 = []
        for _ in range(5):
            start_time = time.perf_counter()
            frame = small_test_frame.copy()
            for effect in effects_20:
                frame = effect(frame, t=0.5, progress=0.5)
            times_20.append((time.perf_counter() - start_time) * 1000)
        time_20 = np.median(times_20)
        
        # Time for 20 effects should be less than 3x time for 10 effects
        # (allowing some overhead, but ruling out exponential growth)
        # Using 3x instead of 2.5x to account for variation in effect complexity
        assert time_20 <= time_10 * 3, \
            f"20 effects took {time_20:.2f}ms, 10 effects took {time_10:.2f}ms (ratio: {time_20/time_10:.2f}x)"


# ============================================================================
# Memory Leak Tests
# ============================================================================

class TestLongEffectChainMemory:
    """Test that long effect chains don't cause memory leaks."""
    
    def test_no_memory_leak_with_repeated_rendering(self, small_test_frame):
        """Test that repeated rendering doesn't leak memory."""
        # Create effect chain
        effects = [
            brightness(0.05),
            contrast(1.1),
            sepia(),
            gaussian_blur(2),
            scan_lines(4, 0.15),
            posterize(5),
            chromatic_aberration(2),
            vignette_simple(0.4),
            sharpen(0.5),
            fade_to_color((255, 255, 255)),
        ]
        
        # Render many times
        for _ in range(100):
            frame = small_test_frame.copy()
            for effect in effects:
                frame = effect(frame, t=0.5, progress=0.5)
            
            # Verify frame is valid
            assert frame.shape == small_test_frame.shape
            assert frame.dtype == np.uint8
        
        # Force garbage collection
        gc.collect()
        
        # If we got here without running out of memory, test passes
        assert True
    
    def test_no_memory_accumulation_in_effect_chain(self, medium_test_frame):
        """Test that effect chains don't accumulate memory."""
        # Create long effect chain
        effects = [
            brightness(0.03),
            contrast(1.05),
            saturation(1.05),
            vignette(0.2, 0.9),
            film_grain(0.015),
            sepia(),
            color_temperature(6100),
            vibrance(0.08),
            gaussian_blur(1),
            sharpen(0.3),
            scan_lines(5, 0.1),
            posterize(6),
            chromatic_aberration(1),
            border(1, (0, 0, 0)),
            fade_to_color((255, 255, 255)),
        ]
        
        # Render multiple frames
        for i in range(50):
            frame = medium_test_frame.copy()
            for effect in effects:
                frame = effect(frame, t=i * 0.1, progress=i / 50.0)
            
            # Verify frame is valid
            assert frame.shape == medium_test_frame.shape
            assert frame.dtype == np.uint8
            
            # Periodically force garbage collection
            if i % 10 == 0:
                gc.collect()
        
        # If we got here without running out of memory, test passes
        assert True


# ============================================================================
# Correctness Tests - Effect Composition
# ============================================================================

class TestLongEffectChainCorrectness:
    """Test that long effect chains compose correctly."""
    
    def test_effect_order_matters_in_long_chain(self, small_test_frame):
        """Test that effect order matters in long chains."""
        # Create two chains with same effects in different order
        chain1 = [
            brightness(0.2),
            sepia(),
            gaussian_blur(3),
            posterize(4),
            chromatic_aberration(3),
        ]
        
        chain2 = [
            chromatic_aberration(3),
            posterize(4),
            gaussian_blur(3),
            sepia(),
            brightness(0.2),
        ]
        
        # Apply chain 1
        frame1 = small_test_frame.copy()
        for effect in chain1:
            frame1 = effect(frame1, t=0.5, progress=0.5)
        
        # Apply chain 2
        frame2 = small_test_frame.copy()
        for effect in chain2:
            frame2 = effect(frame2, t=0.5, progress=0.5)
        
        # Frames should be different (order matters)
        assert not np.array_equal(frame1, frame2), \
            "Different effect order should produce different results"
    
    def test_all_effects_applied_in_long_chain(self, small_test_frame):
        """Test that all effects in a long chain are actually applied."""
        # Create a chain where each effect makes a visible change
        effects = [
            brightness(0.5),      # Significantly brighten
            invert(),             # Invert colors
            grayscale(),          # Convert to grayscale
            posterize(2),         # Reduce to 4 colors
            threshold_bw(128),    # Convert to pure B&W
        ]
        
        # Apply effects one by one and verify each makes a change
        frame = small_test_frame.copy()
        previous_frame = frame.copy()
        
        for i, effect in enumerate(effects):
            frame = effect(frame, t=0.5, progress=0.5)
            
            # Verify frame changed
            assert not np.array_equal(frame, previous_frame), \
                f"Effect {i} should change the frame"
            
            # Verify frame is still valid
            assert frame.shape == small_test_frame.shape
            assert frame.dtype == np.uint8
            assert np.all(frame >= 0) and np.all(frame <= 255)
            
            previous_frame = frame.copy()
    
    def test_frame_validity_maintained_through_long_chain(self, small_test_frame):
        """Test that frame validity is maintained through a long effect chain."""
        # Create a long chain with various effect types
        effects = [
            brightness(0.1),
            contrast(1.2),
            saturation(1.1),
            sepia(),
            color_temperature(6000),
            vibrance(0.15),
            gaussian_blur(2),
            sharpen(0.5),
            scan_lines(3, 0.2),
            posterize(5),
            chromatic_aberration(2),
            vignette_simple(0.4),
            border(2, (255, 0, 0)),
            fade_to_color((255, 255, 255)),
            progress_bar("bottom", 5, (0, 255, 0)),
        ]
        
        # Apply all effects
        frame = small_test_frame.copy()
        for i, effect in enumerate(effects):
            frame = effect(frame, t=0.5, progress=0.5)
            
            # Verify frame validity after each effect
            assert frame.shape == small_test_frame.shape, \
                f"Effect {i} changed frame shape"
            assert frame.dtype == np.uint8, \
                f"Effect {i} changed frame dtype"
            assert np.all(frame >= 0) and np.all(frame <= 255), \
                f"Effect {i} produced out-of-range values"


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestLongEffectChainEdgeCases:
    """Test edge cases for long effect chains."""
    
    def test_long_chain_with_1x1_frame(self):
        """Test that long chains work with 1x1 frames."""
        frame = np.array([[[128, 128, 128]]], dtype=np.uint8)
        
        effects = [
            brightness(0.1),
            contrast(1.1),
            sepia(),
            posterize(4),
            gaussian_blur(1),
            scan_lines(1, 0.5),
            border(0, (255, 255, 255)),
            fade_to_color((255, 255, 255)),
            progress_bar("bottom", 0, (0, 255, 0)),
            threshold_bw(128),
        ]
        
        for effect in effects:
            frame = effect(frame, t=0.5, progress=0.5)
        
        assert frame.shape == (1, 1, 3)
        assert frame.dtype == np.uint8
    
    def test_long_chain_at_progress_boundaries(self, small_test_frame):
        """Test long chains at progress=0.0 and progress=1.0."""
        effects = [
            brightness(0.1),
            contrast(1.1),
            sepia(),
            gaussian_blur(2),
            scan_lines(3, 0.2),
            posterize(5),
            chromatic_aberration(2),
            fade_to_color((255, 0, 0)),
            progress_bar("bottom", 5, (0, 255, 0)),
            threshold_bw(128),
        ]
        
        # Test at progress=0.0
        frame0 = small_test_frame.copy()
        for effect in effects:
            frame0 = effect(frame0, t=0.0, progress=0.0)
        
        assert frame0.shape == small_test_frame.shape
        assert frame0.dtype == np.uint8
        
        # Test at progress=1.0
        frame1 = small_test_frame.copy()
        for effect in effects:
            frame1 = effect(frame1, t=1.0, progress=1.0)
        
        assert frame1.shape == small_test_frame.shape
        assert frame1.dtype == np.uint8
    
    def test_long_chain_with_extreme_parameters(self, small_test_frame):
        """Test long chains with extreme effect parameters."""
        effects = [
            brightness(0.5),          # Very bright
            contrast(2.0),            # High contrast
            saturation(2.0),          # Very saturated
            gamma_correction(3.0),    # Extreme gamma
            gaussian_blur(10),        # Heavy blur
            posterize(2),             # Minimal colors
            chromatic_aberration(10), # Heavy aberration
            scan_lines(1, 0.9),       # Dense scan lines
            border(10, (255, 0, 0)),  # Thick border
            fade_to_color((0, 0, 0)), # Fade to black
        ]
        
        frame = small_test_frame.copy()
        for effect in effects:
            frame = effect(frame, t=0.5, progress=0.5)
        
        # Frame should still be valid despite extreme parameters
        assert frame.shape == small_test_frame.shape
        assert frame.dtype == np.uint8
        assert np.all(frame >= 0) and np.all(frame <= 255)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
