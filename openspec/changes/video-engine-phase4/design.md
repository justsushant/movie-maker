## Context

PRISM's video engine currently implements Phases 1-3 with a small but stable effect library (7 color/texture/animated effects, 6 audio-reactive effects). The architecture is well-established with:
- EffectFunction protocol for pure functions
- Class-based pattern for stateful effects (audio-reactive)
- Linear effect chain in `engine/renderer.py`
- Property-based testing with Hypothesis
- Integration with Scene DSL via `ImageClip.effects` list

Phase 4 introduces ~60 new effects across 5 categories without requiring new dependencies or architectural changes. All dependencies (numpy, opencv-python, scipy, librosa, pillow) are already installed and tested.

**Constraints**:
- Must follow existing EffectFunction protocol: `(frame: np.ndarray, t: float, progress: float) -> np.ndarray`
- Must preserve frame shape and dtype (HxWx3 uint8)
- Must clamp all pixel values to [0, 255]
- Must integrate seamlessly with existing effect chain
- Must support graceful degradation when optional dependencies unavailable
- Must be testable with property-based tests
- Performance target: 5-100ms per effect at 1080p

**Stakeholders**:
- Content creators using PRISM for video production
- Developers integrating PRISM into pipelines
- Quality assurance team testing video output

## Goals / Non-Goals

**Goals:**

1. Expand color grading capabilities from 4 to 25+ effects for professional video production
2. Add blur and focus effects (11 effects) for cinematic depth and motion effects
3. Implement texture and overlay effects (17 effects) for production value
4. Create stylization effects (15 effects) for unique visual identities
5. Complete transition library with 11 advanced transitions
6. Maintain existing code quality (SOLID principles, testing standards)
7. Keep effects performant (target 5-100ms per effect at 1080p)
8. Ensure comprehensive test coverage (>90% code coverage, all edge cases)

**Non-Goals:**

- Implement particle systems (deferred to Phase 5 due to state complexity)
- Implement depth-based effects (deferred to Phase 5, requires depth map infrastructure)
- Implement advanced typography animations (deferred to Phase 6)
- Modify existing Scene DSL or renderer architecture
- Break backward compatibility with existing effects
- Add new external dependencies (all required dependencies are installed)

## Decisions

### D1: Implementation Order by Effect Category Priority

**Decision**: Implement effects in 5 priority tiers:
- **Priority 1 (Week 1)**: High-value, low-complexity color effects (6 effects: grayscale, invert, sepia, hue shift, gamma, temperature)
- **Priority 2 (Weeks 2-3)**: Blur effects (5 effects: motion blur, radial blur, tilt-shift, pixelate, box blur)
- **Priority 3 (Weeks 4-5)**: Texture overlays (10 effects: scan lines, letterbox, gradient, colored noise, bokeh, light leak, dust/scratches, lens flare)
- **Priority 4 (Weeks 6-8)**: Stylization effects (9 effects: glitch variants, chromatic aberration, edge detection, threshold, posterize)
- **Priority 5 (Weeks 8-10)**: Advanced transitions (11 effects: push, blinds, diamond, zoom-through, whip pan, pixelate, glitch)

**Rationale**:
- Quick wins establish value and build developer confidence
- Blur effects provide high visual impact with medium complexity
- Texture overlays add production value quickly
- Stylization effects are highest impact but highest complexity
- Advanced transitions complete the feature set

**Alternatives considered**:
- Implement all 60+ effects in parallel - REJECTED (would be overwhelming, no clear starting point)
- Implement by random order - REJECTED (no clear dependencies between effects)
- Implement Phase 4 as one monolithic release - REJECTED (harder to test, review, and verify)

### D2: Use Pure Function Pattern for Simple Effects

**Decision**: Simple effects (color, texture, simple blur) use pure function pattern returning callable.

**Rationale**:
- Matches existing Phase 2 pattern (brightness, contrast, saturation, vignette)
- Stateless and easy to test
- Natural composition with existing chain_effects()
- Clear parameter signature

**Example**:
```python
def grayscale() -> Callable[[np.ndarray, float, float], np.ndarray]:
    def effect(frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        gray = (frame[:,:,0] * 0.299 + frame[:,:,1] * 0.587 + frame[:,:,2] * 0.114)
        return np.stack([gray, gray, gray], axis=2).astype(np.uint8)
    return effect
```

**Alternatives considered**:
- Use classes for all effects - REJECTED (overhead for simple, stateless effects)
- Mix function and class patterns - REJECTED (inconsistent, harder to reason about)

### D3: Use Class-Based Pattern for Stateful Effects

**Decision**: Stateful effects (glitch variants with randomness, future particle systems) use class pattern with `__call__` method.

**Rationale**:
- Maintains internal state across frames
- Compatible with EffectFunction protocol (class is callable)
- Matches existing Phase 3 pattern (OnsetFlash, OnsetZoomPulse, etc.)
- Clear initialization and update lifecycle

**Example**:
```python
class GlitchRGBSplit:
    def __init__(self, max_offset: int = 20):
        self.max_offset = max_offset
        self._rng = np.random.RandomState(None)
    
    def __call__(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        # Per-frame state updates
        r_offset = self._rng.randint(-self.max_offset, self.max_offset)
        # Apply effect
        # ...
        return result
```

**Alternatives considered**:
- Use global state - REJECTED (not thread-safe, breaks composition)
- Use closure-based state - REJECTED (unclear state management)

### D4: Organize Effects in Single File (engine/effects.py)

**Decision**: Add all ~60 Phase 4 effects to existing `engine/effects.py` rather than creating new files.

**Rationale**:
- Keeps all effects in one discoverable location
- Matches existing architecture (Phase 2 effects are in single file)
- Simplifies imports (one import statement)
- No file proliferation (no effects/color.py, effects/blur.py, etc.)

**Structure**:
```python
# engine/effects.py

# Existing Phase 2 effects
brightness, contrast, saturation, vignette, film_grain, fade_in, fade_out, pulse

# Existing Phase 3 effects (audio-reactive)
OnsetFlash, OnsetZoomPulse, EnergyZoom, EnergyBrightness, EnergyShake, SpectralColorShift

# Phase 4: Color Effects (20+)
grayscale, invert, sepia, hue_shift, color_temperature, tint, gamma_correction, curves_lut, channel_mixer, duotone, tricolor, cinematic_teal_orange, bleach_bypass, cross_process, auto_white_balance, vibrance, color_pulse, fade_to_color, thermal

# Phase 4: Blur Effects (10+)
motion_blur, radial_blur, zoom_blur, tilt_shift, depth_of_field, sharpen, pixelate, bilateral_blur, box_blur, animated_blur

# Phase 4: Texture Effects (17+) - deferred particle effects
scan_lines, letterbox, border, gradient_overlay, image_watermark, pattern_overlay, light_leak, bokeh, dust_scratches, lens_flare, progress_bar

# Phase 4: Stylization Effects (12+)
edge_detection, sketch, oil_painting, emboss, halftone, chromatic_aberration, glitch_rgb_split, glitch_block_displacement, glitch_scan_line_shift, glitch_color_corruption, crt_retro, vhs_tape_distortion, threshold_b_w, dithering

# Phase 4: Transitions (11)
push_left, push_right, push_up, push_down, blinds_horizontal, blinds_vertical, diamond_wipe, zoom_through, whip_pan, pixelate_transition, glitch_transition
```

**Alternatives considered**:
- Create separate files per category (effects/color.py, effects/blur.py) - REJECTED (matches plan document's single-file approach)
- Create module package with submodules - REJECTED (plan document specifies `engine/effects/color.py` structure but current codebase uses single file)

### D5: Extend Existing Test Files, Not Create New Ones

**Decision**: Add Phase 4 tests to existing `tests/test_effects.py` and `tests/test_transitions.py` rather than creating new test files.

**Rationale**:
- Keeps test suite consolidated
- Follows existing pattern (Phase 2 and 3 effects are in same files)
- Simplifies test discovery and execution
- No proliferation of test files

**Alternatives considered**:
- Create separate test files (test_phase4_color_effects.py, test_phase4_blur_effects.py, etc.) - REJECTED (test file proliferation)

### D6: Follow Established Testing Strategy (Pyramid)

**Decision**: Use four-tier testing strategy matching Phase 2/3: property-based → unit → integration → visual regression.

**Rationale**:
- Property-based tests catch 90% of bugs with minimal effort
- Unit tests cover edge cases and error handling
- Integration tests validate real-world workflows
- Visual regression ensures visual correctness

**Test Structure**:
```
tests/test_effects.py
  ├── Property-Based Tests (universal properties)
  │   ├── Shape/Dtype Preservation
  │   ├── Value Clamping (all pixels in [0,255])
  │   ├── Effect-Specific Properties
  │   └── Chain Ordering
  ├── Unit Tests
  │   ├── Effect-Specific Behavior
  │   ├── Edge Cases
  │   └── Error Handling
  └── Integration Tests
      ├── Effect Chains
      └── With Transitions
```

**Alternatives considered**:
- Only visual regression - REJECTED (slow, catches few bugs)
- Only unit tests - REJECTED (misses integration issues)

### D7: Prioritize Effects by Impact vs Complexity Matrix

**Decision**: Use complexity vs impact matrix to guide implementation order within each priority tier.

**Matrix**:
```
Complexity Level: Simple (5-15 LOC) | Medium (15-40 LOC) | Complex (40-80 LOC)
Impact:           Low   | Medium  | High
                   -------|----------|------
Simple/Medium     | 1st   | 2nd      | 3rd
Simple/High        | 2nd   | 3rd      | 1st
Medium/Low        | 4th   | 5th      | ---
Medium/Medium     | 5th   | 4th      | 2nd
```

**Implementation order within Priority 1**:
1. Grayscale (Simple, High impact)
2. Invert (Simple, Medium impact)
3. Sepia (Simple, High impact)
4. Hue Shift (Simple, Medium impact)
5. Gamma (Simple, Medium impact)
6. Color Temperature (Simple, Medium impact)

**Alternatives considered**:
- Implement all Priority 1 effects in random order - REJECTED (no clear starting point)
- Implement by code size (LOC) - REJECTED (doesn't correlate with impact)

### D8: Defer Complex Particle Systems to Phase 5

**Decision**: Do NOT implement snow, rain, confetti, floating particles, dust motes, sparkle, or smoke/fog in Phase 4.

**Rationale**:
- Particle systems require complex state management (position, velocity, lifetime per particle)
- Need physics simulation (gravity, wind, collisions) for realistic motion
- Require Perlin or noise algorithms for natural movement
- Are significant effort (40-80 LOC per effect) for moderate visual impact
- Deserve dedicated phase for proper design and testing
- Other Phase 4 effects provide higher value with lower complexity

**Alternatives considered**:
- Implement simplified particle systems (static particles, simple movement) - REJECTED (still complex, poor quality)
- Implement particle effects as texture overlays (pre-rendered) - REJECTED (less flexible, harder to customize)

### D9: Defer Mosaic/Stained Glass to Phase 5

**Decision**: Do NOT implement mosaic/voronoi stylization effect in Phase 4.

**Rationale**:
- Requires scipy Voronoi or complex tiling algorithms
- Computationally expensive for real-time rendering
- Moderate visual impact for high complexity
- Better to defer until scipy-based effects infrastructure is mature

**Alternatives considered**:
- Implement simple grid-based mosaic - REJECTED (not true Voronoi, poor quality)
- Use approximate Voronoi (k-means) - REJECTED (inaccurate, still complex)

### D10: Create Showcase Demo for Phase 4

**Decision**: Create `examples/demo_phase4_rich_effects.py` demonstrating Phase 4 effects.

**Rationale**:
- Provides working examples for users
- Tests effect combinations in realistic scenarios
- Documents effect parameters and visual outcomes
- Matches existing demo pattern (demo_phase2_showcase.py, demo_phase3_audio_reactive.py)

**Demo Structure**:
```python
# Section 1: Color Effects Showcase
# - Grayscale, Sepia, Hue Shift, Gamma, etc.

# Section 2: Blur Effects Showcase
# - Motion Blur, Radial Blur, Tilt-Shift, etc.

# Section 3: Texture Effects Showcase
# - Scan Lines, Letterbox, Gradient Overlay, etc.

# Section 4: Stylization Effects Showcase
# - Glitch variants, Chromatic Aberration, Edge Detection, etc.

# Section 5: Transition Effects Showcase
# - Push, Blinds, Diamond, Zoom Through, etc.

# Section 6: Effect Chain Showcase
# - Multiple Phase 4 effects chained together
```

**Alternatives considered**:
- No demo - REJECTED (users have no working examples)
- Inline demos in docstrings - REJECTED (hard to execute and visualize)

## Risks / Trade-offs

### [R1] Performance Risk: Too Many Effects Slow Rendering

**Risk**: Implementing 60+ effects could degrade rendering performance significantly.

**Impact**: 1080p video rendering could take 2-3x longer than baseline.

**Mitigation**:
- Implement effects in priority order (quick wins first)
- Profile each effect to identify bottlenecks
- Optimize hot spots (use vectorized numpy operations, minimize copies)
- Provide performance guidelines for users (effect count vs. quality trade-off)
- Cache expensive computations (e.g., gradient masks) where applicable
- Consider optional GPU acceleration for heavy effects (future Phase)

### [R2] Test Coverage Risk: Large Effect Count

**Risk**: 60+ effects may make comprehensive testing overwhelming.

**Impact**: Edge cases could be missed, regression bugs introduced.

**Mitigation**:
- Prioritize property-based tests (catch 90% of bugs automatically)
- Group effects by category for targeted testing
- Use Hypothesis for exhaustive input generation
- Create visual regression references for manual inspection
- Implement stress tests with various resolutions and effect counts
- Leverage existing test patterns from Phase 2/3

### [R3] Complexity Risk: Stylization Effects Are Hard to Test

**Risk**: Effects with randomness (glitch, particle systems) are difficult to test deterministically.

**Impact**: Flaky tests, missed edge cases, unpredictable behavior.

**Mitigation**:
- Use seeded randomness for deterministic testing
- Test properties rather than exact outputs (e.g., "all pixels are valid" vs. "output equals expected")
- For stateful effects, test invariants (shape, dtype, value range) rather than exact pixel values
- Use visual regression testing for randomness-based effects
- Document expected behavior ranges and probabilities

### [R4] API Consistency Risk: Mixed Effect Patterns

**Risk**: Mixing pure function and class-based patterns could confuse users.

**Impact**: Inconsistent parameter passing, unclear initialization behavior.

**Mitigation**:
- Document both patterns clearly in docstrings
- Provide examples for each pattern
- Use type hints extensively
- Ensure both patterns are callable (implement `__call__` for classes)
- Test both patterns identically (same EffectFunction protocol)

### [R5] Documentation Risk: 60 Effects Hard to Document Thoroughly

**Risk**: Poor documentation leads to confusion and misuse.

**Impact**: Users cannot use effects effectively, support burden increases.

**Mitigation**:
- Require docstrings for all effects with examples
- Create comprehensive showcase demo
- Update `docs/video_engine.md` with Phase 4 effects catalog
- Include parameter ranges and typical values
- Provide visual examples (where possible)

### [R6] Backward Compatibility Risk: Existing Code Changes

**Risk**: Modifications to effect chain or renderer could break existing effects.

**Impact**: Phase 2/3 effects stop working, user videos break.

**Mitigation**:
- NO modifications to `engine/renderer.py` effect chain logic
- NO modifications to `engine/planner.py`
- NO modifications to Scene DSL
- ALL Phase 4 effects are additive only
- Run full test suite after each effect implementation
- Run integration tests after each category completion

## Open Questions

1. **Effect parameter validation**: Should we add parameter validation (range checking) at effect creation time, or allow invalid parameters to fail naturally during rendering?

2. **Effect naming convention**: Should we use snake_case function names (grayscale) or factory names with parameters (fade_through_color)?

3. **Default parameters**: Should each effect have sensible defaults, or require all parameters explicitly?

4. **Error handling**: Should effects raise ValueError on invalid inputs, or attempt graceful fallback (e.g., ignore invalid parameters)?

5. **Performance budget**: Should we establish maximum acceptable rendering time per effect (e.g., 100ms at 1080p), or let users trade off quality vs. speed?

6. **Effect deprecation**: How will we handle potentially obsolete effects in future phases (remove with deprecation warning vs. silent removal)?

7. **Cross-platform compatibility**: Should we test effects on different platforms (Windows/Mac/Linux) for OpenCV behavior differences?

8. **Effect composition limitations**: Should we document maximum recommended effect chain length per clip (e.g., 5-10 effects) to maintain performance?

9. **Visual regression baseline**: How often should we update visual regression references (major versions, significant effect changes, CI runs)?

10. **Advanced easing functions**: Should we implement additional easing functions (bounce, elastic, bezier) beyond current cubic variants for Phase 4 animations?
