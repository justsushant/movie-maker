# Requirements Document: Video Engine Phase 2

## Introduction

Phase 2 of the video engine extends Phase 1's clip-based composition system with transitions and effects. This phase enables smooth visual transitions between clips (crossfades, slides, wipes, etc.) and per-clip effect chains (color grading, vignettes, film grain). The architecture maintains Phase 1's declarative approach while adding composable visual enhancements.

The system builds on Phase 1's Scene DSL, adding transition specifications between clips and effect lists per clip. The planner accounts for transition overlaps in timeline computation, and the renderer blends frames during transition regions using pure functions.

## Glossary

- **Transition**: A visual effect that blends two clips during an overlap period, defined by a pure function `(frame_a, frame_b, progress) -> frame`
- **Effect**: A visual transformation applied to a single frame, defined by a pure function `(frame, t, progress) -> frame`
- **Effect Chain**: A sequence of effects applied to a clip in order, where each effect receives the output of the previous effect
- **Transition Region**: A time interval where two clips overlap and require blending via a transition function
- **Progress**: A normalized value in [0.0, 1.0] representing completion of a transition or effect over time
- **Frame**: A numpy array of shape (height, width, 3) with dtype uint8 representing an RGB image
- **Easing Function**: A function mapping progress [0.0, 1.0] to eased progress [0.0, 1.0], used to control transition timing
- **Blend Transition**: A transition that combines two frames using alpha blending or color space operations
- **Geometric Transition**: A transition that uses spatial transformations (slides, wipes, iris) to reveal one frame while hiding another
- **Animated Transition**: A transition with complex motion or distortion effects (zoom-through, whip pan, pixelate, glitch)
- **Source Frame**: The base frame from a clip before effects are applied
- **Processed Frame**: A frame after the effect chain has been applied

## Requirements

### Requirement 1: Transition Data Structures

**User Story:** As a video creator, I want to specify transitions between clips in my scene, so that I can create smooth visual flow between images.

#### Acceptance Criteria

1. THE System SHALL define a Transition dataclass with type, duration, and easing attributes
2. THE System SHALL define a TransitionType enum containing all supported transition types
3. WHEN a Transition is created with duration, THEN the duration SHALL be a positive float representing seconds
4. WHEN a Transition is created with easing, THEN the easing SHALL be a valid EasingFunction from Phase 1
5. THE Scene dataclass SHALL include a transitions list attribute containing Transition objects
6. WHEN a Scene has N clips, THEN the transitions list SHALL contain at most N-1 transitions
7. WHEN a Scene has fewer transitions than N-1, THEN missing transitions SHALL be treated as instant cuts (no blend)

### Requirement 2: Blend Transitions

**User Story:** As a video creator, I want to use blend-based transitions like crossfades, so that I can create smooth dissolves between clips.

#### Acceptance Criteria

1. WHEN a CROSSFADE transition is applied, THE System SHALL linearly interpolate between frame_a and frame_b using alpha blending
2. WHEN a FADE_THROUGH_BLACK transition is applied, THE System SHALL fade frame_a to black in the first half and fade from black to frame_b in the second half
3. WHEN a FADE_THROUGH_WHITE transition is applied, THE System SHALL fade frame_a to white in the first half and fade from white to frame_b in the second half
4. WHEN a FADE_THROUGH_COLOR transition is applied with a specified color, THE System SHALL fade through that color
5. WHEN progress is 0.0 for any blend transition, THE System SHALL return frame_a unchanged
6. WHEN progress is 1.0 for any blend transition, THE System SHALL return frame_b unchanged
7. THE System SHALL apply the transition's easing function to progress before computing the blend

### Requirement 3: Geometric Transitions

**User Story:** As a video creator, I want to use geometric transitions like slides and wipes, so that I can create directional reveals between clips.

#### Acceptance Criteria

1. WHEN a SLIDE_LEFT transition is applied, THE System SHALL move frame_b from right to left over frame_a
2. WHEN a SLIDE_RIGHT transition is applied, THE System SHALL move frame_b from left to right over frame_a
3. WHEN a SLIDE_UP transition is applied, THE System SHALL move frame_b from bottom to top over frame_a
4. WHEN a SLIDE_DOWN transition is applied, THE System SHALL move frame_b from top to bottom over frame_a
5. WHEN a PUSH_LEFT transition is applied, THE System SHALL push frame_a left while frame_b enters from right
6. WHEN a PUSH_RIGHT transition is applied, THE System SHALL push frame_a right while frame_b enters from left
7. WHEN a PUSH_UP transition is applied, THE System SHALL push frame_a up while frame_b enters from bottom
8. WHEN a PUSH_DOWN transition is applied, THE System SHALL push frame_a down while frame_b enters from top
9. WHEN a WIPE_LEFT transition is applied, THE System SHALL reveal frame_b from left to right with a hard edge
10. WHEN a WIPE_RIGHT transition is applied, THE System SHALL reveal frame_b from right to left with a hard edge
11. WHEN a WIPE_UP transition is applied, THE System SHALL reveal frame_b from top to bottom with a hard edge
12. WHEN a WIPE_DOWN transition is applied, THE System SHALL reveal frame_b from bottom to top with a hard edge
13. WHEN a wipe transition has soft_edge enabled, THE System SHALL apply a gradient feather to the wipe boundary
14. WHEN an IRIS_OPEN transition is applied, THE System SHALL reveal frame_b through an expanding circle from center
15. WHEN an IRIS_CLOSE transition is applied, THE System SHALL reveal frame_b outside a shrinking circle from center
16. WHEN a CLOCK_WIPE transition is applied, THE System SHALL reveal frame_b in a clockwise sweep from 12 o'clock
17. WHEN a DIAMOND_WIPE transition is applied, THE System SHALL reveal frame_b through an expanding diamond from center
18. WHEN a BLINDS_HORIZONTAL transition is applied, THE System SHALL reveal frame_b through horizontal strips
19. WHEN a BLINDS_VERTICAL transition is applied, THE System SHALL reveal frame_b through vertical strips

### Requirement 4: Animated Transitions

**User Story:** As a video creator, I want to use animated transitions with motion effects, so that I can create dynamic visual changes between clips.

#### Acceptance Criteria

1. WHEN a ZOOM_THROUGH transition is applied, THE System SHALL scale frame_a up while fading out and scale frame_b down while fading in
2. WHEN a WHIP_PAN transition is applied, THE System SHALL create a fast horizontal motion blur effect between frames
3. WHEN a PIXELATE transition is applied, THE System SHALL pixelate frame_a while un-pixelating frame_b
4. WHEN a GLITCH transition is applied, THE System SHALL create digital distortion effects during the transition
5. THE System SHALL apply the transition's easing function to control animation timing

### Requirement 5: Effect System Architecture

**User Story:** As a video creator, I want to apply visual effects to individual clips, so that I can enhance the appearance of each image independently.

#### Acceptance Criteria

1. THE System SHALL define an Effect protocol with a function signature `(frame, t, progress) -> frame`
2. THE ImageClip dataclass SHALL include an effects list attribute containing Effect objects
3. WHEN rendering a clip, THE System SHALL apply effects in sequence from first to last
4. WHEN an effect is applied, THE System SHALL receive the current frame, absolute time t, and clip progress
5. WHEN a clip has no effects, THE System SHALL return the source frame unchanged
6. THE System SHALL ensure each effect returns a frame with the same dimensions as the input

### Requirement 6: Color Effects

**User Story:** As a video creator, I want to apply color adjustments to clips, so that I can control brightness, contrast, and saturation.

#### Acceptance Criteria

1. WHEN a BRIGHTNESS effect is applied with a positive value, THE System SHALL increase pixel intensity
2. WHEN a BRIGHTNESS effect is applied with a negative value, THE System SHALL decrease pixel intensity
3. WHEN a CONTRAST effect is applied with a value greater than 1.0, THE System SHALL increase contrast
4. WHEN a CONTRAST effect is applied with a value less than 1.0, THE System SHALL decrease contrast
5. WHEN a SATURATION effect is applied with a value greater than 1.0, THE System SHALL increase color saturation
6. WHEN a SATURATION effect is applied with a value less than 1.0, THE System SHALL decrease color saturation
7. WHEN a VIGNETTE effect is applied, THE System SHALL darken the frame edges while keeping the center bright
8. THE System SHALL clamp all color values to valid range [0, 255] after applying effects

### Requirement 7: Texture Effects

**User Story:** As a video creator, I want to apply texture effects to clips, so that I can add film grain or other visual textures.

#### Acceptance Criteria

1. WHEN a FILM_GRAIN effect is applied, THE System SHALL add random noise to the frame
2. WHEN a FILM_GRAIN effect has an intensity parameter, THE System SHALL scale the noise amplitude by that intensity
3. THE System SHALL generate different grain patterns for each frame to simulate film texture
4. THE System SHALL preserve the original frame's brightness and color while adding grain

### Requirement 8: Timeline Planning with Transitions

**User Story:** As a system developer, I want the planner to account for transition overlaps, so that clips can blend smoothly during transition periods.

#### Acceptance Criteria

1. WHEN a Scene has transitions, THE ScenePlanner SHALL compute overlap regions between adjacent clips
2. WHEN a transition has duration D, THE ScenePlanner SHALL create an overlap of D seconds between the two clips
3. WHEN computing clip timings with transitions, THE System SHALL ensure clip_n.end_time overlaps with clip_n+1.start_time by transition duration
4. WHEN a Scene has no transitions between clips, THE ScenePlanner SHALL use sequential timing with no overlap
5. THE ResolvedTimeline SHALL include transition information for each overlap region
6. WHEN planning a timeline, THE System SHALL validate that transition durations do not exceed clip durations

### Requirement 9: Renderer Updates for Transitions

**User Story:** As a system developer, I want the renderer to detect and handle transition regions, so that frames are properly blended during transitions.

#### Acceptance Criteria

1. WHEN rendering a frame at time t, THE FrameRenderer SHALL determine if t falls within a transition region
2. WHEN t is in a transition region, THE FrameRenderer SHALL identify both the outgoing and incoming clips
3. WHEN rendering during a transition, THE FrameRenderer SHALL render both clips independently with their effect chains
4. WHEN both clip frames are rendered, THE FrameRenderer SHALL compute transition progress based on t and transition duration
5. WHEN transition progress is computed, THE FrameRenderer SHALL apply the transition's easing function
6. WHEN frames are ready, THE FrameRenderer SHALL call the transition function with frame_a, frame_b, and eased progress
7. WHEN t is not in a transition region, THE FrameRenderer SHALL render a single clip as in Phase 1
8. WHEN rendering at the start of the timeline with a transition, THE System SHALL handle the edge case gracefully
9. WHEN rendering at the end of the timeline with a transition, THE System SHALL handle the edge case gracefully

### Requirement 10: Transition Function Protocol

**User Story:** As a system developer, I want a consistent interface for all transitions, so that new transitions can be added without changing the renderer.

#### Acceptance Criteria

1. THE System SHALL define a TransitionFunction protocol with signature `(frame_a: np.ndarray, frame_b: np.ndarray, progress: float) -> np.ndarray`
2. WHEN a transition function is called, THE System SHALL pass progress in range [0.0, 1.0]
3. WHEN progress is 0.0, THE transition function SHALL return a frame visually identical to frame_a
4. WHEN progress is 1.0, THE transition function SHALL return a frame visually identical to frame_b
5. THE transition function SHALL return a frame with the same shape and dtype as the input frames
6. THE transition function SHALL be a pure function with no side effects
7. THE System SHALL validate that frame_a and frame_b have identical dimensions before calling the transition function

### Requirement 11: Effect Function Protocol

**User Story:** As a system developer, I want a consistent interface for all effects, so that new effects can be added without changing the renderer.

#### Acceptance Criteria

1. THE System SHALL define an EffectFunction protocol with signature `(frame: np.ndarray, t: float, progress: float) -> np.ndarray`
2. WHEN an effect function is called, THE System SHALL pass the current frame, absolute time t, and clip progress in [0.0, 1.0]
3. THE effect function SHALL return a frame with the same shape and dtype as the input frame
4. THE effect function SHALL be a pure function with no side effects
5. THE System SHALL allow effects to use time t for animated effects
6. THE System SHALL allow effects to use progress for clip-relative animations

### Requirement 12: Backward Compatibility

**User Story:** As a user of Phase 1, I want my existing scenes to continue working, so that I don't need to update my code when upgrading to Phase 2.

#### Acceptance Criteria

1. WHEN a Scene has no transitions list, THE System SHALL render clips sequentially with instant cuts
2. WHEN a Scene has an empty transitions list, THE System SHALL render clips sequentially with instant cuts
3. WHEN an ImageClip has no effects list, THE System SHALL render the clip without effects
4. WHEN an ImageClip has an empty effects list, THE System SHALL render the clip without effects
5. THE System SHALL maintain all Phase 1 functionality without modification to existing code

### Requirement 13: Error Handling for Transitions

**User Story:** As a video creator, I want clear error messages when transitions are misconfigured, so that I can fix issues quickly.

#### Acceptance Criteria

1. WHEN a transition duration is negative, THE System SHALL raise a ValueError with a descriptive message
2. WHEN a transition duration exceeds the shorter of the two adjacent clips, THE System SHALL raise a ValueError
3. WHEN a Scene has more transitions than N-1 for N clips, THE System SHALL raise a ValueError
4. WHEN a transition type is invalid, THE System SHALL raise a ValueError
5. WHEN frame dimensions don't match during transition, THE System SHALL raise a ValueError with frame dimensions
6. THE System SHALL include the transition index and clip indices in error messages

### Requirement 14: Error Handling for Effects

**User Story:** As a video creator, I want clear error messages when effects are misconfigured, so that I can fix issues quickly.

#### Acceptance Criteria

1. WHEN an effect returns a frame with different dimensions than input, THE System SHALL raise a ValueError
2. WHEN an effect returns a frame with different dtype than input, THE System SHALL raise a ValueError
3. WHEN an effect raises an exception, THE System SHALL wrap it with context about which clip and effect failed
4. THE System SHALL include the effect index and clip index in error messages

### Requirement 15: Performance Considerations

**User Story:** As a video creator, I want effects and transitions to render efficiently, so that video generation remains fast.

#### Acceptance Criteria

1. WHEN rendering a frame with effects, THE System SHALL apply effects in-place when possible to minimize memory allocation
2. WHEN rendering a transition, THE System SHALL reuse frame buffers when possible
3. WHEN applying multiple effects, THE System SHALL avoid unnecessary array copies
4. THE System SHALL render frames with effects in comparable time to Phase 1 frames (within 2x overhead)
5. THE System SHALL document the performance impact of each effect type
