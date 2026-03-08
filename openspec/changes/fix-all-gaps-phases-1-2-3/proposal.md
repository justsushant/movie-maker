# Proposal: Complete Video Engine Phases 1-3

## Why

The video engine Phases 1-3 have significant gaps that prevent the system from reaching its full potential as documented in `docs/video_engine_plan.md`:

- **Phase 3 Critical Issue**: Beat synchronization is non-functional. The `BeatSync` enum with modes (NONE, NEAREST_BEAT, BEAT_GRID) exists in the Scene DSL and is defined in `Transition` objects, but these modes are never actually used. Audio analysis completes successfully, but the results are ignored during scene planning - transitions always use declared timing regardless of sync mode.

- **Phase 2 Incomplete Effects Library**: Phase 2 implemented 24/24 transition types (100% complete) but the effects library remains severely incomplete:
  - Only 4 of 25 planned color effects are implemented (16%)
  - Only 1 of 20 planned texture effects is implemented (5%)
  - Zero blur effects, zero stylization effects, zero typography effects

- **Phase 1 Limited Animation Foundation**: The easing function library that powers all smooth animation has only 4 of 23 planned easing functions (17%), missing quadratic, quartic, quintic, exponential, sine, circular, bounce, elastic, back, spring, bezier, and spline variants.

This change completes all identified gaps to deliver the full feature set originally planned for Phases 1-3, enabling professional video production capabilities with audio-reactive effects, comprehensive visual effects, and rich animation options.

## What Changes

### Phase 3 - Beat Synchronization (CRITICAL)

**Breaking Change**: ScenePlanner internal implementation modified (external API unchanged)

- Implement `ScenePlanner._analyze_audio()` method to integrate audio analysis into the planning pipeline:
  - Check if `scene.audio` is None, return None if so
  - Import and instantiate AudioAnalyzer and AudioSync (catch ImportError for graceful degradation)
  - Call `analyzer.analyze_all()` to extract beats, onsets, energy, and spectral features
  - Create AudioSync object from analysis results
  - Handle exceptions gracefully with logging

- Implement `ScenePlanner._apply_beat_sync()` method to align transitions with audio beats:
  - Handle `BeatSync.NONE`: preserve declared timings (no-op)
  - Handle `BeatSync.NEAREST_BEAT`: adjust transition start time to nearest detected beat using `audio_sync.get_nearest_beat()`
  - Handle `BeatSync.BEAT_GRID`: adjust both start and end times to beat boundaries
  - Validate that beat-snapped timings don't create negative clip durations or invalid overlaps
  - Log warnings and fall back to declared timing if validation fails

- Update `ScenePlanner.plan()` method:
  - Call `_analyze_audio()` early in planning process
  - Store AudioSync in ResolvedTimeline
  - Call `_apply_beat_sync()` after computing initial clip timings
  - Use beat-adjusted timings for final timeline construction

- Update `ResolvedTimeline` dataclass:
  - Add `audio_sync: Optional[AudioSync]` attribute with default None
  - Maintain backward compatibility for Phase 1 and Phase 2 scenes

### Phase 1 - Easing Functions

**Breaking Change**: New easing functions added to public API (backward compatible)

- Implement 19 missing easing functions in `engine/easing.py`:
  - Quadratic variants: ease_in_quadratic, ease_out_quadratic, ease_in_out_quadratic
  - Quartic variants: ease_in_quartic, ease_out_quartic, ease_in_out_quartic
  - Quintic variants: ease_in_quintic, ease_out_quintic, ease_in_out_quintic
  - Exponential variants: ease_in_exponential, ease_out_exponential, ease_in_out_exponential
  - Sine variants: ease_in_sine, ease_out_sine, ease_in_out_sine
  - Circular variants: ease_in_circular, ease_out_circular, ease_in_out_circular
  - Elastic variants: ease_in_elastic, ease_out_elastic, ease_in_out_elastic
  - Back variants: ease_in_back, ease_out_back, ease_in_out_back
  - Spring variant: spring (requires scipy)
  - Bezier curve: cubic_bezier
  - Step function: step
  - Cubic spline: cubic_spline (requires scipy)

- Add missing motion preset to `engine/scene.py`:
  - Add `SLOW_ZOOM_IN` to MotionPreset enum
  - Implement slow zoom in logic in `compute_motion_path()` in `engine/camera.py`

- Update `engine/__init__.py` to export all new easing functions

### Phase 2 - Color Effects

- Implement 21 missing color effects in `engine/effects.py`:

  **Color Adjustments**:
  - `hue_shift(amount)`: Rotate all colors around color wheel (convert HSV, add offset to H channel)
  - `color_temperature(warmth)`: Shift toward warm/cool tones (R/B channel adjustments)
  - `tint(color, opacity)`: Blend frame with solid color
  - `sepia()`: Warm brownish vintage tone (3x3 matrix multiply)
  - `grayscale()`: Remove all color (weighted sum of R/G/B)
  - `invert()`: Reverse all colors (255 - frame)
  - `posterize(levels)`: Reduce to N discrete color levels (quantize)
  - `solarize(threshold)`: Invert pixels above threshold
  - `gamma_correction(gamma)`: Non-linear brightness curve (pow transformation)

  **Advanced Color**:
  - `curves(r_curve, g_curve, b_curve)`: Custom color mapping via LUT (256-element lookup tables)
  - `channel_mixer(r_weights, g_weights, b_weights)`: Cross-blend R/G/B channels via 3x3 matrix
  - `duotone(color1, color2)`: Map luminance to two endpoint colors
  - `tricolor(color1, color2, color3)`: Map luminance to 3-color gradient
  - `cinematic_teal_orange()`: Shadows go teal, highlights go warm orange (HSV selective adjustment)
  - `bleach_bypass()`: Desaturated, high-contrast film look
  - `cross_process()`: Unnatural color shifts (S-curve per channel)
  - `auto_white_balance()`: Correct color cast automatically (Gray-world algorithm)
  - `vibrance(amount)`: Boost saturation on low-saturation pixels only
  - `color_pulse(intensity, duration)`: Brief brightness spike animated over time
  - `fade_to_color(color)`: Lerp entire frame toward solid color over progress
  - `thermal()`: False-color heat map look (grayscale + cv2.COLORMAP_JET)

### Phase 2 - Blur Effects

- Implement 11 blur effects in new `engine/effects/blur.py`:

  - `gaussian_blur(radius)`: Soft uniform blur with configurable radius (cv2.GaussianBlur)
  - `box_blur(size)`: Fast uniform blur with equal-weight kernel (cv2.blur)
  - `motion_blur(angle, distance)`: Directional streak simulating camera movement (cv2.filter2D with line kernel)
  - `radial_blur(strength)`: Blur radiating from center point outward
  - `zoom_blur(strength)`: Blur radiating outward (blend multiple scaled copies)
  - `tilt_shift(blur_amount, focus_y)`: Sharp horizontal band, blurred above/below (gradient mask + variable blur)
  - `depth_of_field(depth_map, focal_depth)`: Blur proportional to distance from focal plane (per-pixel blur radius)
  - `sharpen(strength)`: Enhance edges via unsharp mask (frame + alpha * (frame - blurred))
  - `pixelate(block_size)`: Blocky mosaic effect (downscale + upscale with INTER_NEAREST)
  - `bilateral_filter(d, sigma_color, sigma_space)`: Smooth flat regions while preserving sharp edges
  - `animated_blur(base_radius, max_radius)`: Blur intensity changes over clip duration

### Phase 2 - Texture Effects

- Implement 19 missing texture effects in new `engine/effects/texture.py`:

  - `colored_noise(intensity)`: Per-channel independent random noise
  - `scan_lines(intensity)`: Horizontal dark lines (multiply every Nth row by darkening factor)
  - `letterbox(height)`: Cinematic black bars at top and bottom (set pixel rows to black)
  - `border(size, color)`: Colored rectangular border around frame (draw rectangle)
  - `gradient_overlay(start_color, end_color, direction)`: Linear or radial color gradient blended on top
  - `image_watermark(image, position, opacity)`: Semi-transparent image composited at position
  - `pattern_overlay(pattern)`: Repeating pattern (stripes, dots, grid) blended
  - `light_leak(intensity)`: Bright colored blobs near edges (Gaussian blobs, additive blend)
  - `bokeh_overlay(radius, intensity)`: Blurred circular light highlights (draw circles with radial gradient)
  - `dust_and_scratches(intensity)`: Random marks and hairline scratches (draw random lines/dots)
  - `lens_flare(position, intensity)`: Bright radial streaks from light source (radial gradient + streak lines)
  - `snow(density)`: Falling white dots (particle system with downward velocity)
  - `rain(intensity, angle)`: Falling semi-transparent streaks (particle system with slight angle)
  - `confetti()`: Colorful falling/tumbling small shapes (particle system with rotation)
  - `floating_particles()`: Slow-drifting small dots (Perlin-like noise drift)
  - `sparkle()`: Brief bright points that flash randomly (random positions with sine intensity)
  - `smoke_fog(intensity)`: Semi-transparent drifting cloud layer (scrolling Perlin noise field)
  - `progress_bar()`: Animated bar showing video playback progress (filled rectangle where width = total_width * (t / duration))

### Phase 2 - Stylization Effects

- Implement 15 stylization effects in new `engine/effects/stylize.py`:

  - `edge_detection(threshold1, threshold2)`: Show only edges as white lines (cv2.Canny)
  - `sketch()`: Black and white pencil drawing look (cv2.pencilSketch)
  - `oil_painting(sigma_s, sigma_r)`: Smooth painterly brush-stroke look (cv2.stylization)
  - `emboss()`: Raised/stamped surface illusion (convolution with emboss kernel)
  - `halftone(dot_size)`: Dots of varying size based on local luminance (map luminance to dot radius)
  - `chromatic_aberration(offset)`: Subtle RGB channel offset (shift R channel +2px, B channel -2px)
  - `glitch_rgb_split()`: Large offset between color channels (shift R/G/B by 5-20px)
  - `glitch_block_displacement()`: Rectangular blocks shifted horizontally (random row-slice offsets)
  - `glitch_scan_line_shift()`: Individual rows displaced horizontally (per-row random horizontal offset)
  - `glitch_color_corruption()`: Random color channel swaps in rectangular regions (swap R/G/B in random rects)
  - `crt_retro()`: Scan lines + barrel distortion + color bleed (combine multiple effects)
  - `vhs_tape_distortion()`: Horizontal jitter + color bleed + noise bands (row shifts + per-channel blur + noise stripes)
  - `threshold()`: Pure black and white, no grays (np.where(gray > threshold, 255, 0))
  - `dithering()`: Threshold with error diffusion (Floyd-Steinberg algorithm on grayscale)
  - `mosaic_stained_glass()`: Voronoi-style colored regions (random Voronoi cells, fill each with mean color)

### Phase 2 - Typography Effects

- Implement 21 typography effects in new `engine/typography/animated_text.py`:

  **Basic Text**:
  - `static_text(text, x, y, font, color)`: Text drawn at fixed position (PIL ImageDraw.text)
  - `fade_in_text(text, duration)`: Text appears from fully transparent (draw on RGBA layer with increasing alpha)
  - `fade_out_text(text, duration)`: Text disappears to fully transparent

  **Motion Effects**:
  - `fly_in(direction)`: Text slides in from off-screen edge (animated (x,y) with easing)
  - `fly_out(direction)`: Text slides out to off-screen edge (reversed direction)
  - `scale_up()`: Text grows from zero to full size (render at increasing font size or downscale large)
  - `scale_down()`: Text shrinks from full size to zero (reversed)
  - `bounce_in()`: Text arrives with overshoot bounce (position driven by bounce easing)
  - `elastic_in()`: Text arrives with spring oscillation (position driven by elastic easing)

  **Content-Based**:
  - `typewriter()`: Characters appear one by one left to right (text[:n(t)] where n increases with time)
  - `word_by_word_reveal()`: Words appear sequentially (use TTS word timestamps)
  - `word_highlight()`: Current spoken word shown in different color (already exists in subtitle system)
  - `kinetic_typography()`: Spoken word animates per word timing (per-word position/scale/opacity driven by word start/end times)

  **Visual Enhancements**:
  - `drop_shadow(offset, color, blur_radius)`: Shadow copy drawn behind text (draw twice: offset shadow, then normal)
  - `outline(stroke_width, stroke_color)`: Colored border around each character (Pillow stroke_width + stroke_fill)
  - `glow(blur_radius, color)`: Soft light halo behind text (draw text on layer, apply Gaussian blur, composite behind crisp text)

  **Layout Effects**:
  - `lower_third(direction)`: Animated bar/shape with text that slides in from edge (draw filled rect + text, animate x/y position from off-screen)
  - `ticker(text, speed)`: Text scrolls continuously left to right (animated x position that wraps, text wider than screen)
  - `vertical_scroll(text)`: Text scrolls upward continuously (animated y position, text taller than screen)

  **Utility**:
  - `counter(start, end)`: Number that counts up or down between two values (format int(lerp(start, end, progress)) as text, draw)
  - `subtitle_karaoke_sweep()`: Highlight sweeps across text pixel-by-pixel (gradient mask moving across text based on time within segment)

### Phase 1 - Spatial Effects

- Implement 9 missing spatial effects in new `engine/effects/spatial.py`:

  - `rotate(angle)`: Rotate frame around center (cv2.getRotationMatrix2D + cv2.warpAffine)
  - `flip_horizontal()`: Mirror left-right (cv2.flip(frame, 1))
  - `flip_vertical()`: Mirror top-bottom (cv2.flip(frame, 0))
  - `camera_shake(intensity)`: Random jitter on crop position (random offsets smoothed with savgol_filter)
  - `perspective_tilt(tilt_x, tilt_y)`: Fake 3D rotation (cv2.getPerspectiveTransform + cv2.warpPerspective)
  - `barrel_distortion(strength)`: Lens bulge / fisheye effect (cv2.remap with radial displacement field)
  - `pincushion_distortion(strength)`: Inverse lens effect (cv2.remap with inverse radial field)
  - `crop(x1, y1, x2, y2)`: Fixed sub-region of source (array slicing)
  - `animated_crop(rect_start, rect_end)`: Sub-region that moves/resizes over time (interpolated crop coords with easing)

### Phase 2 - Temporal Effects

- Implement 5 temporal effects in new `engine/effects/temporal.py`:

  - `motion_trail(num_frames, fade_factor)`: Current frame blended with N previous frames (ring buffer, weighted blend)
  - `ghosting()`: Faint copy of immediately previous frame persists (output = frame * 0.7 + prev_frame * 0.3)
  - `strobe(frequency, color)`: Alternate between current frame and solid color (frame if (t * freq) % 1 > 0.5 else solid_color)
  - `freeze_frame(freeze_time, duration)`: Hold a single frame for specified duration (cache frame at freeze_time, return cached for duration)
  - `flash_frame(timestamp, color)`: Single-frame burst of solid color at specific timestamp (return np.full(shape, color) at exact time, normal frame otherwise)

## Capabilities

### New Capabilities

None (this change enhances existing capabilities rather than introducing new ones)

### Modified Capabilities

- **video-engine-phase-1**: Expanding easing function library from 4 to 23 functions, adding SLOW_ZOOM_IN motion preset
- **video-engine-phase-2**: Expanding effects library from 8 to 90+ effects across color, blur, texture, stylization, typography, spatial, and temporal categories
- **video-engine-phase-3**: Completing beat synchronization - making BeatSync modes functional instead of non-operative

## Impact

### Affected Code

- `engine/easing.py`: 19 new easing functions added
- `engine/camera.py`: SLOW_ZOOM_IN motion preset added
- `engine/scene.py`: MotionPreset enum updated
- `engine/__init__.py`: Exports updated for new easing functions
- `engine/planner.py`: _analyze_audio(), _apply_beat_sync() methods added, plan() method modified
- `ResolvedTimeline` dataclass: audio_sync attribute added
- `engine/effects.py`: 21 new color effects added
- `engine/effects/blur.py` (NEW): 11 blur effects
- `engine/effects/texture.py` (NEW): 19 texture effects
- `engine/effects/stylize.py` (NEW): 15 stylization effects
- `engine/typography/animated_text.py` (NEW): 21 typography effects
- `engine/effects/spatial.py` (NEW): 9 spatial effects
- `engine/effects/temporal.py` (NEW): 5 temporal effects

### Dependencies

- **Existing**: All changes use existing dependencies (numpy, opencv-python, scipy, pillow)
- **No new dependencies required** (librosa already added for Phase 3)

### APIs

- **Public API**: No breaking changes - all additions are additive
- **Scene DSL**: Backward compatible - BeatSync becomes functional, not a breaking change
- **Effect System**: Expanded effect set available for users
- **Planner API**: Internal changes only, public API unchanged

### Performance Considerations

- **Beat Synchronization**: Minimal overhead - runs once during planning phase, not per-frame
- **Easing Functions**: Pure math functions, no performance impact
- **Color Effects**: Most are O(N) per pixel with numpy vectorization
- **Blur Effects**: Use OpenCV's optimized implementations
- **Texture Effects**: Particle systems (snow, rain, confetti) may have measurable CPU overhead - recommend profiling
- **Typography Effects**: Text rendering with Pillow, minimal overhead
- **Stylization Effects**: Some effects (oil painting, halftone, mosaic) may be CPU-intensive - recommend profiling

### Testing Strategy

- **Unit Tests**: Each new effect function tested with various parameters
- **Property Tests**: Hypothesis-based tests for correctness (e.g., blur doesn't change dimensions, color values stay in [0, 255])
- **Integration Tests**: Complete scenes with multiple effects across categories
- **Backward Compatibility Tests**: All existing Phase 1 and Phase 2 tests must pass
- **Performance Tests**: Benchmark new effects at 1080p, verify <150ms per effect
- **Visual Regression Tests**: Reference frames for key effects

### Migration Notes

- **No migration required**: All changes are additive
- **Existing Scenes**: Continue to work unchanged
- **New Functionality**: Opt-in via new effects and BeatSync modes
