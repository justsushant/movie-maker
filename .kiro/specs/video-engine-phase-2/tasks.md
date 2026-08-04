# Implementation Plan: Video Engine Phase 2

## Overview

This implementation plan builds on Phase 1's clip-based video composition system by adding transitions and effects. The approach follows a bottom-up strategy: implement core transition and effect functions first, then update the planner and renderer to orchestrate them, and finally add comprehensive testing.

## Tasks

- [x] 1. Set up Phase 2 module structure
  - Create `engine/transitions.py` and `engine/effects.py` modules
  - Add necessary imports and type hints
  - Set up module docstrings
  - _Requirements: Architecture overview_

- [x] 2. Extend Scene DSL with transitions and effects
  - [x] 2.1 Add TransitionType enum to engine/scene.py
    - Define all 24 transition types (blend, geometric, animated)
    - _Requirements: 1.2_
  
  - [x] 2.2 Create Transition dataclass
    - Add type, duration, and easing attributes
    - Implement __post_init__ validation for positive duration
    - Set default easing to ease_in_out_cubic
    - _Requirements: 1.1, 1.3, 1.4_
  
  - [x] 2.3 Define TransitionFunction and EffectFunction protocols
    - Create TransitionFunction protocol with (frame_a, frame_b, progress) signature
    - Create EffectFunction protocol with (frame, t, progress) signature
    - _Requirements: 5.1, 10.1, 11.1_
  
  - [x] 2.4 Update Scene dataclass
    - Add transitions list attribute with default empty list
    - Add __post_init__ validation for transition count <= N-1
    - _Requirements: 1.5, 1.6_
  
  - [x] 2.5 Update ImageClip dataclass
    - Add effects list attribute with default empty list
    - _Requirements: 5.2_

- [x] 3. Implement blend transitions
  - [x] 3.1 Implement crossfade transition
    - Linear interpolation: result = frame_a * (1-p) + frame_b * p
    - _Requirements: 2.1_
  
  - [x] 3.2 Implement fade_through_black transition
    - Fade to black in first half, from black in second half
    - _Requirements: 2.2_
  
  - [x] 3.3 Implement fade_through_white transition
    - Fade to white in first half, from white in second half
    - _Requirements: 2.3_
  
  - [x] 3.4 Implement fade_through_color transition factory
    - Fade through specified RGB color (parameterized)
    - _Requirements: 2.4_
  
  - [x] 3.5 Write property test for blend transition boundaries
    - **Property 7: Transition Boundary Conditions**
    - **Validates: Requirements 2.5, 2.6, 10.3, 10.4**
  
  - [x] 3.6 Write property test for crossfade formula
    - **Property 4: Crossfade Mathematical Correctness**
    - **Validates: Requirements 2.1**

- [x] 4. Implement geometric transitions - slides
  - [x] 4.1 Implement slide_left, slide_right, slide_up, slide_down
    - Frame_b enters from edge and moves over frame_a
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 4.2 Write property test for slide monotonicity
    - **Property 9: Slide Transition Monotonicity**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 5. Implement geometric transitions - pushes
  - [x] 5.1 Implement push_left, push_right, push_up, push_down
    - Both frames move together, no black regions
    - _Requirements: 3.5, 3.6, 3.7, 3.8_
  
  - [x]* 5.2 Write property test for push frame coverage
    - **Property 10: Push Transition Frame Coverage**
    - **Validates: Requirements 3.5, 3.6, 3.7, 3.8**

- [x] 6. Implement geometric transitions - wipes
  - [x] 6.1 Implement wipe_left, wipe_right, wipe_up, wipe_down
    - Hard edge reveal with no blending
    - _Requirements: 3.9, 3.10, 3.11, 3.12_
  
  - [x] 6.2 Add soft_edge parameter support to wipe transitions
    - Apply gradient feather to wipe boundary when enabled
    - _Requirements: 3.13_
  
  - [x]* 6.3 Write property test for wipe hard edges
    - **Property 11: Wipe Transition Hard Edge**
    - **Validates: Requirements 3.9, 3.10, 3.11, 3.12**

- [x] 7. Implement geometric transitions - shapes
  - [x] 7.1 Implement iris_open and iris_close
    - Circular mask expanding/shrinking from center
    - _Requirements: 3.14, 3.15_
  
  - [x] 7.2 Implement clock_wipe
    - Clockwise sweep from 12 o'clock using angle map
    - _Requirements: 3.16_
  
  - [x] 7.3 Implement diamond_wipe
    - Manhattan distance for diamond shape
    - _Requirements: 3.17_
  
  - [x] 7.4 Implement blinds_horizontal and blinds_vertical
    - 10 strips revealing progressively
    - _Requirements: 3.18, 3.19_
  
  - [x]* 7.5 Write property test for shape transition monotonicity
    - **Property 12: Shape Transition Geometric Correctness**
    - **Validates: Requirements 3.14, 3.15, 3.16, 3.17**
  
  - [x]* 7.6 Write property test for blinds strip count
    - **Property 13: Blinds Transition Strip Count**
    - **Validates: Requirements 3.18, 3.19**

- [x] 8. Implement animated transitions
  - [x] 8.1 Implement zoom_through transition
    - Scale frame_a up while fading out, scale frame_b down while fading in
    - _Requirements: 4.1_
  
  - [x] 8.2 Implement whip_pan transition
    - Horizontal motion blur effect
    - _Requirements: 4.2_
  
  - [x] 8.3 Implement pixelate transition
    - Pixelate frame_a, un-pixelate frame_b
    - _Requirements: 4.3_
  
  - [x] 8.4 Implement glitch transition
    - RGB channel shifts and scanlines
    - _Requirements: 4.4_
  
  - [x]* 8.5 Write property test for animated transition validity
    - **Property 14: Animated Transition Frame Validity**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [x] 9. Implement transition registry
  - [x] 9.1 Create get_transition_function registry
    - Map TransitionType enum to function implementations
    - Include all 25 transition types (24 + fade_through_color factory)
    - Raise ValueError for unknown types
    - _Requirements: 13.4_
  
  - [x]* 9.2 Write property test for invalid transition type rejection
    - **Property 36: Invalid Transition Type Rejection**
    - **Validates: Requirements 13.4**

- [x] 10. Checkpoint - Ensure transition tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement color effects
  - [x] 11.1 Implement brightness effect factory
    - Add/subtract from pixel values, clamp to [0, 255]
    - _Requirements: 6.1, 6.2, 6.8_
  
  - [x] 11.2 Implement contrast effect factory
    - Multiply centered values, clamp to [0, 255]
    - _Requirements: 6.3, 6.4, 6.8_
  
  - [x] 11.3 Implement saturation effect factory
    - Adjust HSV saturation channel, convert back to RGB
    - _Requirements: 6.5, 6.6_
  
  - [x] 11.4 Implement vignette effect factory
    - Create radial gradient mask, darken edges
    - _Requirements: 6.7_
  
  - [x]* 11.5 Write property test for brightness monotonicity
    - **Property 18: Brightness Effect Monotonicity**
    - **Validates: Requirements 6.1, 6.2**
  
  - [x]* 11.6 Write property test for contrast behavior
    - **Property 19: Contrast Effect Behavior**
    - **Validates: Requirements 6.3, 6.4**
  
  - [x]* 11.7 Write property test for saturation behavior
    - **Property 20: Saturation Effect Behavior**
    - **Validates: Requirements 6.5, 6.6**
  
  - [x]* 11.8 Write property test for vignette edge darkening
    - **Property 21: Vignette Effect Edge Darkening**
    - **Validates: Requirements 6.7**
  
  - [x] 11.9 Write property test for color value clamping
    - **Property 22: Color Value Clamping**
    - **Validates: Requirements 6.8**

- [x] 12. Implement texture effects
  - [x] 12.1 Implement film_grain effect factory
    - Generate random noise based on time, add to frame
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x]* 12.2 Write property test for film grain noise addition
    - **Property 23: Film Grain Adds Noise**
    - **Validates: Requirements 7.1**
  
  - [x]* 12.3 Write property test for film grain intensity scaling
    - **Property 24: Film Grain Intensity Scaling**
    - **Validates: Requirements 7.2**
  
  - [x]* 12.4 Write property test for film grain temporal variation
    - **Property 25: Film Grain Temporal Variation**
    - **Validates: Requirements 7.3**
  
  - [x]* 12.5 Write property test for film grain brightness preservation
    - **Property 26: Film Grain Brightness Preservation**
    - **Validates: Requirements 7.4**

- [x] 13. Implement animated effects
  - [x] 13.1 Implement fade_in and fade_out effect factories
    - Multiply frame by progress-based factor
    - _Requirements: 5.4_
  
  - [x] 13.2 Implement pulse effect factory
    - Sine wave brightness modulation based on time
    - _Requirements: 5.4_
  
  - [x] 13.3 Implement chain_effects utility
    - Compose multiple effects into single function
    - _Requirements: 5.3_

- [x] 14. Update ScenePlanner for transitions
  - [x] 14.1 Add TransitionRegion dataclass to planner.py
    - Define start_time, end_time, clip indices, transition function, easing
    - _Requirements: 8.5_
  
  - [x] 14.2 Update ResolvedTimeline dataclass
    - Add transitions list attribute
    - _Requirements: 8.5_
  
  - [x] 14.3 Update ResolvedClip dataclass
    - Add effects list attribute
    - _Requirements: 5.2_
  
  - [x] 14.4 Implement transition validation in _validate_transitions
    - Check transition count <= N-1
    - Check positive durations
    - Check durations don't exceed clip durations
    - _Requirements: 1.6, 8.6, 13.1, 13.2, 13.3_
  
  - [x] 14.5 Update plan() method to compute transition overlaps
    - Adjust clip start times for overlaps
    - Create TransitionRegion objects
    - Compute total duration accounting for overlaps
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x]* 14.6 Write property test for timeline overlap computation
    - **Property 27: Timeline Overlap Computation**
    - **Validates: Requirements 8.1, 8.2, 8.3**
  
  - [x]* 14.7 Write property test for sequential timing without transitions
    - **Property 28: Sequential Timing Without Transitions**
    - **Validates: Requirements 8.4, 12.1, 12.2**
  
  - [x]* 14.8 Write property test for transition region creation
    - **Property 29: Transition Region Creation**
    - **Validates: Requirements 8.5**
  
  - [x]* 14.9 Write property test for transition duration validation
    - **Property 1: Transition Duration Validation**
    - **Validates: Requirements 1.3, 8.6, 13.1, 13.2**
  
  - [x]* 14.10 Write property test for scene transition count validation
    - **Property 2: Scene Transition Count Validation**
    - **Validates: Requirements 1.6, 13.3**

- [x] 15. Checkpoint - Ensure planner tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Update FrameRenderer for transitions and effects
  - [x] 16.1 Implement _find_transition_at_time method
    - Search transition regions for time t
    - _Requirements: 9.1_
  
  - [x] 16.2 Implement _render_transition_frame method
    - Render both clips with effect chains
    - Compute and ease progress
    - Call transition function
    - Validate frame dimensions match
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 10.7, 13.5_
  
  - [x] 16.3 Implement _render_single_clip_frame method
    - Render clip with effect chain (Phase 1 behavior when no transition)
    - _Requirements: 9.7_
  
  - [x] 16.4 Implement _apply_effects method
    - Apply effects in sequence
    - Validate dimensions and dtype after each effect
    - Wrap exceptions with context
    - _Requirements: 5.3, 5.6, 11.3, 14.1, 14.2, 14.3_
  
  - [x] 16.5 Update render_frame method
    - Check for transition region
    - Route to transition or single clip rendering
    - _Requirements: 9.1, 9.7_
  
  - [x]* 16.6 Write property test for renderer transition detection
    - **Property 30: Renderer Transition Detection**
    - **Validates: Requirements 9.1, 9.2**
  
  - [x]* 16.7 Write property test for transition rendering process
    - **Property 31: Transition Rendering Process**
    - **Validates: Requirements 9.3, 9.4, 9.5, 9.6**
  
  - [x]* 16.8 Write property test for single clip rendering outside transitions
    - **Property 32: Single Clip Rendering Outside Transitions**
    - **Validates: Requirements 9.7**
  
  - [x]* 16.9 Write property test for transition progress range
    - **Property 33: Transition Progress Range**
    - **Validates: Requirements 10.2, 11.2**
  
  - [x]* 16.10 Write property test for transition frame dimension matching
    - **Property 34: Transition Frame Dimension Matching**
    - **Validates: Requirements 10.7, 13.5**
  
  - [x]* 16.11 Write property test for transition output dimensions
    - **Property 35: Transition Output Dimensions**
    - **Validates: Requirements 10.5**
  
  - [x]* 16.12 Write property test for effect chain ordering
    - **Property 15: Effect Chain Ordering**
    - **Validates: Requirements 5.3**
  
  - [x]* 16.13 Write property test for no effects preserves frame
    - **Property 16: No Effects Preserves Frame**
    - **Validates: Requirements 5.5, 12.3, 12.4**
  
  - [x]* 16.14 Write property test for effect dimension preservation
    - **Property 17: Effect Dimension Preservation**
    - **Validates: Requirements 5.6, 11.3, 14.1, 14.2**

- [x] 17. Checkpoint - Ensure renderer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Add error handling and validation
  - [x] 18.1 Add error handling tests for transitions
    - Test invalid duration raises ValueError
    - Test duration exceeding clip raises ValueError
    - Test too many transitions raises ValueError
    - Test frame dimension mismatch raises ValueError
    - _Requirements: 13.1, 13.2, 13.3, 13.5, 13.6_
  
  - [x] 18.2 Add error handling tests for effects
    - Test effect dimension change raises ValueError
    - Test effect dtype change raises ValueError
    - Test effect exception wrapping with context
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [x] 19. Add backward compatibility tests
  - [x] 19.1 Test Phase 1 scenes without transitions attribute
    - Verify scenes render with sequential timing
    - _Requirements: 12.1_
  
  - [x] 19.2 Test Phase 1 clips without effects attribute
    - Verify clips render base frames unchanged
    - _Requirements: 12.3_
  
  - [x] 19.3 Test missing transitions render as cuts
    - **Property 3: Missing Transitions Render as Cuts**
    - **Validates: Requirements 1.7**
  
  - [x] 19.4 Run Phase 1 test suite
    - Ensure no regressions in Phase 1 functionality
    - _Requirements: 12.5_

- [x] 20. Add integration tests
  - [x] 20.1 Test complete pipeline with transitions
    - Scene → Planner → Renderer → Frames with transitions
    - _Requirements: Integration testing_
  
  - [x] 20.2 Test effect chain integration
    - Clips with multiple effects render correctly
    - _Requirements: Integration testing_
  
  - [x] 20.3 Test transition + effects combination
    - Both clips have effects during transition
    - _Requirements: Integration testing_
  
  - [x] 20.4 Test end-to-end video generation
    - Scene with transitions produces valid MP4
    - _Requirements: Integration testing_

- [x] 21. Add visual regression tests
  - [x] 21.1 Generate reference frames for transitions
    - Create reference frames for each transition type at progress=[0.0, 0.25, 0.5, 0.75, 1.0]
    - Store in tests/fixtures/reference_frames/phase2/
    - _Requirements: Visual regression testing_
  
  - [x] 21.2 Generate reference frames for effects
    - Create reference frames for each effect type
    - Store in tests/fixtures/reference_frames/phase2/
    - _Requirements: Visual regression testing_
  
  - [x] 21.3 Implement visual comparison tests
    - Compare rendered frames against references with tolerance
    - _Requirements: Visual regression testing_

- [x] 22. Add unit tests for specific examples
  - [x] 22.1 Write unit tests for transition functions
    - Test each of the 24 transition types with known frames at progress=0.0, 0.5, 1.0
    - Test fade_through_color with different color parameters
    - Test wipe transitions with soft_edge parameter
    - _Requirements: Unit testing focus_
  
  - [x] 22.2 Write unit tests for effect functions
    - Test brightness with positive and negative values
    - Test contrast with values <1.0, =1.0, >1.0
    - Test saturation with values from 0.0 to 2.0
    - Test vignette with different intensity and radius parameters
    - Test film_grain with different intensity values
    - _Requirements: Unit testing focus_
  
  - [x] 22.3 Write unit tests for Scene DSL
    - Test Transition dataclass creation with all parameters
    - Test TransitionType enum has all 24 values
    - Test Scene validation for transition count
    - Test Transition validation for positive duration
    - Test default easing is ease_in_out_cubic
    - _Requirements: Unit testing focus_

- [x] 23. Add performance tests
  - [x] 23.1 Measure transition performance
    - Benchmark each transition type at 1080p
    - Verify blend <50ms, geometric <100ms, animated <150ms
    - _Requirements: Performance testing_
  
  - [x] 23.2 Measure effect performance
    - Benchmark each effect type at 1080p
    - Verify effect chains don't cause exponential slowdown
    - _Requirements: Performance testing_
  
  - [x] 23.3 Compare Phase 2 to Phase 1 baseline
    - Verify Phase 2 within 2x of Phase 1 performance
    - _Requirements: Performance testing_

- [x] 24. Final checkpoint - Complete test suite
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: transitions → effects → planner → renderer → integration
- Backward compatibility is maintained throughout - Phase 1 scenes work unchanged
