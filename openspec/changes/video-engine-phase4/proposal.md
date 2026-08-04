## Why

PRISM's video engine currently has **7 effects** (brightness, contrast, saturation, vignette, film grain, fade in/out, pulse) and **6 audio-reactive effects** (Phase 3). This provides basic color grading and subtitle support, but lacks the comprehensive effects library required for professional video production workflows.

**The Problem**:
- Content creators need cinematic looks (blur, stylization, texture overlays, advanced transitions)
- Current effect palette is too limited for professional video production
- Many common effects (grayscale, sepia, motion blur, chromatic aberration, glitch, etc.) are missing
- Transition library is incomplete (missing push, blinds, diamond, zoom-through, whip pan, pixelate, glitch)

**The Opportunity**:
Phase 4 expands PRISM's capabilities from **13 total effects** to **~60+ effects** across 5 major categories:
1. **Color Effects** (25 new effects) - Professional color grading
2. **Blur and Focus Effects** (11 new effects) - Cinematic depth and motion blur
3. **Texture and Overlay Effects** (20 new effects) - Production value additions
4. **Stylization Effects** (15 new effects) - Unique visual identities
5. **Advanced Transitions** (11 new effects) - Complete transition library

This makes PRISM competitive with professional video editing tools while maintaining the clean, modular architecture established in Phases 1-3.

**Why Now**:
- All required dependencies (numpy, opencv-python, scipy, librosa, pillow) are already installed
- Effect system architecture is stable and well-tested from Phases 1-3
- Clear integration patterns exist (effect chain, protocol-based effects)
- Video engine pipeline (planner → renderer → output) is production-ready
- Testing strategy is established (property-based, unit, integration, visual regression)

This is the right time to expand the effects library before moving to complex features like depth-based effects or particle systems (deferred to Phase 5).

## What Changes

### New Capabilities

Implement **~60 new video effects** across 5 categories, following the established EffectFunction protocol and integrating seamlessly with existing effect chain architecture.

#### `rich-color-effects`
Implement 20+ new color grading effects for professional video production.

**Effects to implement**:
- Grayscale - Convert to black and white
- Invert/Negative - Reverse all colors
- Sepia - Warm brown vintage tone
- Hue Shift - Rotate colors around color wheel
- Color Temperature (Warm/Cool) - Shift toward amber or blue tones
- Tint/Color Overlay - Blend with solid color
- Gamma Correction - Non-linear brightness curve
- Curves/LUT - Custom lookup table transformation
- Channel Mixer - Cross-blend RGB channels
- Duotone - Map luminance to two colors
- Tricolor/Gradient Map - Map luminance to gradient
- Cinematic Teal-Orange - Shadows teal, highlights warm
- Bleach Bypass - Desaturated, high-contrast film look
- Cross-Process - Unnatural color shifts (lomography)
- Auto White Balance - Correct color cast automatically
- Vibrance - Boost saturation on low-saturation pixels
- Color Pulse/Flash - Animated brightness spike
- Fade to Color - Lerp entire frame toward color
- Thermal/Infrared - False-color heat map

#### `rich-blur-effects`
Implement 10 blur and focus effects for cinematic depth and motion.

**Effects to implement**:
- Motion Blur - Directional streak simulating camera movement
- Radial Blur - Blur radiating from center point
- Zoom Blur - Blur radiating outward (fast zoom feel)
- Tilt-Shift/Miniature - Sharp band in middle, blurred edges
- Depth-of-Field - Blur proportional to distance from focal depth
- Sharpen - Enhance edges (unsharp mask)
- Pixelate - Blocky mosaic/low-res effect
- Bilateral Blur - Smooth flat regions, preserve edges
- Box Blur - Fast uniform blur
- Animated Blur - Blur intensity changes over time

#### `rich-texture-overlays`
Implement 17 texture and overlay effects to add production value.

**Effects to implement**:
- Scan Lines - Horizontal dark CRT lines
- Letterbox Bars - Cinematic black bars
- Border/Frame - Colored rectangular border
- Gradient Overlay - Linear or radial color gradient
- Image Watermark - Semi-transparent image overlay
- Pattern Overlay - Repeating pattern (stripes, dots, grid)
- Light Leak - Bright colored blobs near edges
- Bokeh Overlay - Blurred circular light highlights
- Dust and Scratches - Random marks and hairline scratches
- Lens Flare - Bright radial streaks from light source
- Progress Bar - Animated bar showing playback progress

Note: Particle effects (snow, rain, confetti, floating particles, dust motes, sparkle, smoke/fog) are deferred to Phase 5 due to complexity and state management requirements.

#### `rich-stylization-effects`
Implement 12 stylization effects for unique visual identities.

**Effects to implement**:
- Edge Detection - Show only edges as white lines
- Sketch/Pencil - Black and white pencil drawing look
- Oil Painting - Smooth, painterly brush-stroke look
- Emboss - Raised/stamped surface illusion
- Halftone - Dots of varying size based on luminance
- Chromatic Aberration - Subtle RGB channel offset (lens fringing)
- Glitch (RGB Split) - Large offset between color channels
- Glitch (Block Displacement) - Rectangular blocks shifted
- Glitch (Scan Line Shift) - Individual rows displaced
- Glitch (Color Corruption) - Random color channel swaps
- CRT/Retro - Scan lines + barrel distortion + color bleed
- VHS/Tape Distortion - Horizontal jitter + color bleed + noise bands
- Threshold/High Contrast B&W - Pure black and white
- Dithering - Threshold with error diffusion (retro print)

Note: Mosaic/Stained Glass is deferred to Phase 5 (requires scipy Voronoi or complex tiling).

#### `rich-transitions`
Implement 11 advanced transitions to complete the transition library.

**Transitions to implement**:
- Push Left - A and B both move left together
- Push Right - Both move right together
- Push Up - Both move up together
- Push Down - Both move down together
- Blinds Horizontal - Horizontal strips alternate between A and B
- Blinds Vertical - Vertical strips alternate
- Diamond Wipe - Diamond shape expands from center
- Zoom Through - A zooms past camera (scale + fade), B appears behind
- Whip Pan - Fast motion blur in one direction during switch
- Pixelate Transition - A pixelates out, B pixelates in
- Glitch Transition - Glitch effects intensify at cut point

### Modified Capabilities

None. All changes are additive additions to the effect library. No existing behavior or requirements are changing.

## Impact

### Affected Code

- `engine/effects.py` - Add ~60 new effect functions (expand from 7 to ~67)
- `tests/test_effects.py` - Add property-based and unit tests for new effects
- `tests/test_*.py` - Create new test files for blur, texture, stylization effects, and transitions
- `examples/` - Add showcase demos for Phase 4 effects (similar to demo_phase2_showcase.py, demo_phase3_audio_reactive.py)

### New Dependencies Required

None. All dependencies are already installed:
- ✓ numpy (already in requirements.txt)
- ✓ opencv-python (already in requirements.txt)
- ✓ scipy (already in requirements.txt)
- ✓ librosa (already in requirements.txt)
- ✓ pillow (already in requirements.txt)

### Integration Points

All Phase 4 effects integrate via existing **EffectFunction protocol** without code changes to the renderer:

```python
# Example integration (no code changes needed!)
from engine.scene import ImageClip, MotionPreset
from engine.effects import grayscale, sepia, motion_blur, glitch_rgb_split

clip = ImageClip(
    source="image.jpg",
    duration=5.0,
    motion=MotionPreset.KEN_BURNS,
    effects=[
        # New Phase 4 effects work seamlessly
        grayscale(),
        sepia(),
        motion_blur(angle=45, amount=10),
        glitch_rgb_split(max_offset=20),
        # Can chain with existing Phase 2/3 effects
        brightness(0.1),
        contrast(1.2),
    ]
)
```

### Testing Strategy

- **Property-Based Tests**: Universal properties (clamping, shape preservation, dtype preservation) for all effects using Hypothesis
- **Unit Tests**: Effect-specific behavior tests for complex effects
- **Integration Tests**: Effect chains with multiple Phase 4 effects
- **Visual Regression Tests**: Generate reference outputs for manual inspection
- **Stress Tests**: Various resolutions and effect counts

Target: >90% code coverage, all edge cases covered.

### Performance Considerations

- Color effects: ~5-15ms per effect (fast, numpy operations)
- Blur effects: ~10-50ms per effect (OpenCV operations)
- Stylization effects: ~20-100ms per effect (algorithms)
- Transitions: ~50-150ms per transition (complex blending)

Estimated rendering overhead: 15-25% increase over Phase 2 baseline.

### Backward Compatibility

- All changes are additive - no breaking changes
- Existing effects continue to work unchanged
- Scene DSL requires no modifications
- Existing tests continue to pass
