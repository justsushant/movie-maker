# Design: Complete Video Engine Phases 1-3

## Context

The PRISM video engine has completed Phase 1 (motion presets), Phase 2 (transitions), and Phase 3 (audio analysis foundation) with partial implementation. However, comprehensive analysis of the implementation against `docs/video_engine_plan.md` reveals significant gaps:

- **Phase 3 Critical Gap**: Beat synchronization exists in the Scene DSL (`BeatSync` enum with NONE, NEAREST_BEAT, BEAT_GRID modes) but is never executed. AudioAnalyzer and AudioSync classes are implemented and functional, but ScenePlanner doesn't call them - transitions always use declared timing regardless of `sync` setting.

- **Phase 2 Effects Gap**: While transitions are 100% complete (24/24), the effects library is severely incomplete (8 out of 90+ planned effects implemented). Missing entire categories: blur (11), texture (19), stylization (15), typography (21), and additional color effects (21), spatial effects (9), temporal effects (5).

- **Phase 1 Animation Gap**: The easing function library that powers all smooth animation is minimal (4 out of 23 planned functions), missing quadratic, quartic, quintic, exponential, sine, circular, bounce, elastic, back, spring, bezier, and spline variants.

This change addresses all gaps to deliver the full, production-ready video engine capabilities as originally designed.

**Stakeholders**: Video engine users seeking professional video production capabilities

**Constraints**:
- Maintain backward compatibility with all existing Phase 1 and Phase 2 functionality
- No new dependencies beyond those already in use (librosa, opencv-python, scipy, pillow)
- All new effects must follow existing protocols (EffectFunction, TransitionFunction)
- Beat sync must degrade gracefully when librosa unavailable or audio file missing
- Performance must remain within acceptable bounds for real-time rendering

## Goals / Non-Goals

**Goals:**

1. **Enable Functional Beat Synchronization**: Make BeatSync modes (NONE, NEAREST_BEAT, BEAT_GRID) operational so transitions align with musical beats

2. **Complete Easing Function Library**: Add 19 missing easing functions to support rich animation patterns

3. **Expand Color Effects**: Implement 21 missing color effects for comprehensive color grading capabilities

4. **Add Blur Effects**: Implement 11 blur effects for visual softening and focus control

5. **Implement Texture Effects**: Add 19 texture effects for overlays, particles, and environmental effects

6. **Add Stylization Effects**: Implement 15 stylization effects for artistic video looks

7. **Implement Typography Effects**: Add 21 typography effects for animated text overlays

8. **Add Spatial Effects**: Implement 9 missing spatial effects for advanced transforms

9. **Implement Temporal Effects**: Add 5 temporal effects for time-based effects

10. **Maintain Backward Compatibility**: Ensure all existing Phase 1, Phase 2, and Phase 3 scenes work unchanged

11. **100% Test Coverage**: Add comprehensive tests for all new effects with unit, property, integration, and visual regression tests

**Non-Goals:**

- Do NOT modify existing transition implementations
- Do NOT break backward compatibility with Phase 1 or Phase 2 scenes
- Do NOT add new external dependencies
- Do NOT redesign the core architecture (Scene DSL, Planner, Renderer patterns remain unchanged)
- Do NOT implement Phase 4 effects that weren't planned for Phases 1-3 (e.g., depth-based effects)
- Do NOT implement features that require GPU acceleration or hardware-specific optimizations

## Decisions

### Decision 1: Beat Synchronization Implementation Approach

**Decision**: Integrate audio analysis directly into ScenePlanner rather than adding new public API

**Rationale**:
- Beat sync is a planning-phase operation, not a rendering-phase operation
- Audio analysis happens once per scene, not per-frame
- By keeping it internal to ScenePlanner, we avoid exposing AudioAnalyzer/AudioSync as public dependencies for ScenePlanner callers
- The existing Scene DSL already has `audio` attribute and `Transition.sync` - we only need to wire them together

**Alternatives Considered**:
- Create new public API for users to manually call `_analyze_audio()` and `_apply_beat_sync()` → Rejected: Too complex for users
- Run audio analysis in renderer and cache beat-snapped transitions → Rejected: Beat sync should affect timing, not just rendering
- Add beat sync as a separate pipeline step before ScenePlanner → Rejected: Adds unnecessary complexity

### Decision 2: Easing Functions Implementation Order

**Decision**: Add all 19 missing easing functions in single batch using existing pattern from Phase 1

**Rationale**:
- Easing functions are pure math functions with no dependencies
- They can be implemented independently and tested separately
- Adding them in batch allows for systematic testing
- Following Phase 1's established patterns (quadratic, cubic) ensures consistency

**Alternatives Considered**:
- Implement easing functions only as needed by specific effects → Rejected: Unclear which effects will need which easing functions
- Use an external easing library → Rejected: Adds new dependency, current implementation is sufficient

### Decision 3: Effects Library Module Structure

**Decision**: Create new effect category modules (blur.py, texture.py, stylize.py, spatial.py, temporal.py, typography/animated_text.py) while keeping existing effects.py for color effects

**Rationale**:
- Color effects (21 functions) fit in existing effects.py with current 4 color effects
- New categories are distinct domains with different implementation patterns
- Blur effects use specific OpenCV functions not used elsewhere
- Texture effects include particle systems that benefit from dedicated module
- Typography effects are a large, complex category deserving its own module
- Spatial effects use geometric transforms distinct from other categories
- Temporal effects need state management (ring buffers), cleaner in separate module

**Alternatives Considered**:
- Put all 90+ effects in single effects.py file → Rejected: Would become unmanageable (3000+ lines)
- Create separate package for each effect category → Rejected: Over-engineering for a single project
- Organize by effect "type" instead of category → Rejected: Less intuitive for users

### Decision 4: Particle System Architecture

**Decision**: Implement simple, frame-based particle systems for snow, rain, confetti without complex physics engines

**Rationale**:
- Full physics engines are overkill and add significant complexity
- Frame-based approach (update particle positions per frame) is sufficient for visual effects
- Maintains pure function pattern (frame, t, progress) → frame
- Allows for deterministic testing (seed-based random)

**Alternatives Considered**:
- Use Pymunk physics engine → Rejected: Too heavy dependency
- Implement GPU-accelerated particles → Rejected: Out of scope
- Pre-render particle animations as video overlays → Rejected: Loses interactivity with other effects

### Decision 5: Typography Text Rendering Approach

**Decision**: Use Pillow (PIL) for text rendering, integrate with existing numpy/OpenCV workflow

**Rationale**:
- Pillow is already a dependency (used by ImageLoader)
- Text rendering with Pillow is mature and well-tested
- Easy to convert Pillow images to numpy arrays for OpenCV compositing
- Allows for rich text features (fonts, colors, outlines, shadows)

**Alternatives Considered**:
- Use OpenCV's putText → Rejected: Limited font support, poor anti-aliasing
- Use matplotlib text rendering → Rejected: Overkill, slow
- Implement a new typography engine → Rejected: Existing Pillow is sufficient

### Decision 6: Graceful Degradation for All New Features

**Decision**: All new features check for dependencies and data availability, fail safely with warnings

**Rationale**:
- Maintains backward compatibility - existing scenes without audio/effect attributes continue to work
- scipy-dependent easing functions (spring, spline) check for scipy import, raise ImportError with helpful message if unavailable
- Audio-reactive effects already handle None AudioSync gracefully (from Phase 3)
- Particle systems handle missing parameters by using sensible defaults

**Alternatives Considered**:
- Make scipy mandatory → Rejected: Would break environments without scipy
- Make effects crash if dependencies missing → Rejected: Poor user experience
- Implement fallback implementations for missing dependencies → Rejected: Too much effort for limited value

### Decision 7: Testing Strategy

**Decision**: Use Hypothesis for property-based testing of all new effects, plus unit tests and integration tests

**Rationale**:
- Property tests catch edge cases automatically that manual tests miss
- Existing Phase 1 and Phase 2 use Hypothesis successfully
- Unit tests validate specific behaviors
- Integration tests ensure all effects work together
- Visual regression tests prevent regressions in artistic effects

**Alternatives Considered**:
- Manual test case enumeration → Rejected: Time-consuming, misses edge cases
- Only visual testing → Rejected: Not automatable, doesn't catch all bugs
- Skip testing for "simple" effects → Rejected: All effects need validation

## Risks / Trade-offs

### Risk 1: Particle System Performance

[Risk] Particle systems (snow, rain, confetti, floating particles) with per-frame updates may be CPU-intensive

→ **Mitigation**: Implement efficient numpy vectorization, use simple physics (gravity only), limit particle counts, add performance tests with strict thresholds (<150ms per effect at 1080p)

### Risk 2: Typography System Complexity

[Risk] Typography effects involve multiple layers (text, shadow, glow, outline) that may be error-prone

→ **Mitigation**: Implement carefully with clear separation of concerns, add comprehensive unit tests, use Pillow's built-in features (stroke_width, stroke_fill) where possible

### Risk 3: Test Suite Size

[Risk] Adding 90+ new effects will significantly increase test suite size and execution time

→ **Mitigation**: Use property-based tests to cover many cases with few tests, run performance tests in parallel, use pytest marks to allow selective test running

### Risk 4: Scipy Dependency for Easing Functions

[Risk] spring() and cubic_spline() easing functions require scipy, which may not be available in all environments

→ **Mitigation**: Make scipy optional, add ImportError checks with helpful messages, provide fallback to simpler easing functions if scipy unavailable, document scipy as optional dependency

### Risk 5: Breaking Phase 1/2 Backward Compatibility

[Risk] Adding audio_sync to ResolvedTimeline and modifying ScenePlanner plan() method could break existing scenes

→ **Mitigation**: Add audio_sync as Optional[AudioSync] with default None, ensure all existing tests pass, use __post_init__ validation to prevent invalid states, add explicit backward compatibility tests

### Risk 6: Large Codebase Changes

[Risk] Adding ~90 new effect functions across multiple new files is a large change that could introduce bugs

→ **Mitigation**: Implement incrementally with comprehensive testing at each stage, follow existing patterns rigorously, use strict type hints, add property-based tests that catch contract violations

## Open Questions

None - All design decisions are clear and implementation path is well-defined.
