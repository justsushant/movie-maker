# Delta Spec: Expanded Effects Library

## Overview

This delta specification significantly expands the existing video-engine-phase-2 capabilities by implementing the remaining 82+ effects planned in the original spec. Currently only 8 effects are implemented (4 color, 1 texture, 3 animated).

## Original Spec

The original Phase 2 specification is at `.kiro/specs/video-engine-phase-2/requirements.md`.

## MODIFIED Requirements

### Requirement: Color Effects Library Expansion

**Original Requirement 6**: Color Effects

The System SHALL implement color adjustment effects that modify pixel values directly. Each effect SHALL be a factory function accepting parameters and returning an EffectFunction.

**MODIFIED**:

The System SHALL implement additional color effects beyond the current 4:

1. **Hue Shift**: The System SHALL provide a hue_shift(amount) factory that rotates all colors around the color wheel using HSV color space, with amount in [-180, 180] range

2. **Color Temperature**: The System SHALL provide color_temperature(warmth) factory that shifts colors toward warm (positive) or cool (negative) tones by adjusting R and B channels, with warmth in [-1, 1] range

3. **Tint/Overlay**: The System SHALL provide tint(color, opacity) factory that blends the frame with a solid RGB color at specified opacity (0.0-1.0)

4. **Sepia**: The System SHALL provide a sepia() factory that applies a warm brownish vintage tone using a 3x3 color matrix transformation

5. **Grayscale**: The System SHALL provide a grayscale() factory that removes all color by computing weighted sum of R/G/B channels

6. **Invert**: The System SHALL provide an invert() factory that reverses all colors using 255 - frame

7. **Posterize**: The System SHALL provide a posterize(levels) factory that reduces the image to N discrete color levels using quantization, with levels typically 2-16

8. **Solarize**: The System SHALL provide a solarize(threshold) factory that inverts pixels above the specified threshold (0-255), creating a high-contrast effect

9. **Gamma Correction**: The System SHALL provide a gamma_correction(gamma) factory that applies non-linear brightness adjustment using pow transformation, with gamma typically 0.5-3.0

10. **Curves/LUT**: The System SHALL provide a curves(r_curve, g_curve, b_curve) factory that applies custom color mapping via 256-element lookup tables for each channel

11. **Channel Mixer**: The System SHALL provide a channel_mixer(r_weights, g_weights, b_weights) factory that cross-blends R/G/B channels using a 3x3 matrix transformation

12. **Duotone**: The System SHALL provide a duotone(color1, color2) factory that maps luminance to two endpoint colors

13. **Tricolor**: The System SHALL provide a tricolor(color1, color2, color3) factory that maps luminance to a 3-color gradient

14. **Cinematic Teal-Orange**: The System SHALL provide a cinematic_teal_orange() factory that applies shadows in teal and highlights in warm orange using HSV selective adjustment by luminance

15. **Bleach Bypass**: The System SHALL provide a bleach_bypass() factory that creates a desaturated, high-contrast film look by blending grayscale with original

16. **Cross-Process**: The System SHALL provide a cross_process() factory that applies unnatural color shifts using per-channel S-curve adjustments (lomography look)

17. **Auto White Balance**: The System SHALL provide an auto_white_balance() factory that corrects color casts automatically using the Gray-world algorithm (scale each channel to equal mean)

18. **Vibrance**: The System SHALL provide a vibrance(amount) factory that boosts saturation selectively on low-saturation pixels only, preserving skin tones

19. **Color Pulse**: The System SHALL provide a color_pulse(intensity, duration) factory that creates a brief brightness spike animated over time using easing

20. **Fade to Color**: The System SHALL provide a fade_to_color(color) factory that linearly interpolates the entire frame toward a solid RGB color over the clip duration

21. **Thermal**: The System SHALL provide a thermal() factory that creates a false-color heat map look by converting to grayscale and applying a JET colormap

#### Scenario: Applying hue shift effect

- **WHEN** user applies hue_shift(90) effect to a clip
- **THEN** all colors in the frame rotate 90 degrees around the color wheel (e.g., red becomes yellow)

#### Scenario: Applying gamma correction

- **WHEN** user applies gamma_correction(2.2) effect
- **THEN** frame brightness is adjusted non-linearly, midtones become brighter and shadows become darker

#### Scenario: Cinematic teal-orange look

- **WHEN** user applies cinematic_teal_orange() effect
- **THEN** darker pixels (shadows) shift toward teal, lighter pixels (highlights) shift toward orange

### Requirement: Blur Effects

**Original Requirement**: (Not explicitly listed, but implied by effects catalog)

The System SHALL implement blur effects that reduce image detail or simulate depth of field.

**MODIFIED**:

The System SHALL implement blur effects in a new `engine/effects/blur.py` module:

1. **Gaussian Blur**: The System SHALL provide gaussian_blur(radius) factory that applies soft uniform blur using cv2.GaussianBlur with configurable radius

2. **Box Blur**: The System SHALL provide a box_blur(size) factory that applies fast uniform blur with equal-weight kernel using cv2.blur

3. **Motion Blur**: The System SHALL provide a motion_blur(angle, distance) factory that creates directional streak simulating camera movement using cv2.filter2D with line kernel at specified angle and distance

4. **Radial Blur**: The System SHALL provide a radial_blur(strength) factory that creates blur radiating from center point outward by averaging pixels along radial lines

5. **Zoom Blur**: The System SHALL provide a zoom_blur(strength) factory that creates blur radiating outward by blending multiple scaled copies of the frame

6. **Tilt-Shift**: The System SHALL provide a tilt_shift(blur_amount, focus_y) factory that creates a sharp horizontal band in the middle with blurred regions above and below using a gradient mask controlling per-pixel blur radius

7. **Depth of Field**: The System SHALL provide a depth_of_field(depth_map, focal_depth) factory that applies blur proportional to distance from focal plane, using per-pixel blur radius derived from depth map

8. **Sharpen**: The System SHALL provide a sharpen(strength) factory that enhances edges using unsharp mask: output = frame + alpha * (frame - blurred_frame)

9. **Pixelate**: The System SHALL provide a pixelate(block_size) factory that creates blocky mosaic effect by downscaling with INTER_NEAREST and upscaling back to original size

10. **Bilateral Filter**: The System SHALL provide a bilateral_filter(d, sigma_color, sigma_space) factory that smooths flat regions while preserving sharp edges using cv2.bilateralFilter

11. **Animated Blur**: The System SHALL provide an animated_blur(base_radius, max_radius) factory that changes blur intensity over clip duration from base_radius to max_radius using easing

#### Scenario: Applying Gaussian blur

- **WHEN** user applies gaussian_blur(5) effect
- **THEN** the frame becomes soft and detail is reduced uniformly across the entire frame

#### Scenario: Applying motion blur

- **WHEN** user applies motion_blur(angle=45, distance=10) effect
- **THEN** the frame shows directional streaks at 45-degree angle simulating camera panning motion

#### Scenario: Applying tilt-shift

- **WHEN** user applies tilt_shift(blur_amount=20, focus_y=0.5) effect
- **THEN** a sharp horizontal band at 50% height remains clear, with graduated blur above and below that band

### Requirement: Texture Effects

**Original Requirement 7**: Texture Effects

The System SHALL implement texture effects that add visual elements on top of frames.

**MODIFIED**:

The System SHALL implement additional texture effects in a new `engine/effects/texture.py` module:

1. **Colored Noise**: The System SHALL provide a colored_noise(intensity) factory that generates per-channel independent random noise added to the frame

2. **Scan Lines**: The System SHALL provide a scan_lines(intensity) factory that adds horizontal dark lines at regular intervals (multiply every Nth row by darkening factor)

3. **Letterbox**: The System SHALL provide a letterbox(height) factory that adds cinematic black bars at top and bottom of the frame (set pixel rows to black)

4. **Border**: The System SHALL provide a border(size, color) factory that draws a colored rectangular border around the frame

5. **Gradient Overlay**: The System SHALL provide a gradient_overlay(start_color, end_color, direction) factory that blends a linear or radial color gradient onto the frame

6. **Image Watermark**: The System SHALL provide a image_watermark(image, position, opacity) factory that composites a semi-transparent image at specified position

7. **Pattern Overlay**: The System SHALL provide a pattern_overlay(pattern) factory that blends a repeating pattern (stripes, dots, grid) onto the frame

8. **Light Leak**: The System SHALL provide a light_leak(intensity) factory that creates bright colored blobs near edges using Gaussian blobs with additive blend mode

9. **Bokeh Overlay**: The System SHALL provide a bokeh_overlay(radius, intensity) factory that creates blurred circular light highlights using radial gradient circles drawn on the frame

10. **Dust and Scratches**: The System SHALL provide a dust_and_scratches(intensity) factory that adds random marks and hairline scratches by drawing random thin lines and dots

11. **Lens Flare**: The System SHALL provide a lens_flare(position, intensity) factory that creates bright radial streaks from a light source position using radial gradient and streak lines

12. **Snow**: The System SHALL provide a snow(density) factory that generates falling white dots using a simple particle system with downward velocity

13. **Rain**: The System SHALL provide a rain(intensity, angle) factory that generates falling semi-transparent streaks using a particle system with slight downward angle

14. **Confetti**: The System SHALL provide a confetti() factory that generates colorful falling/tumbling small shapes using a particle system with rotation

15. **Floating Particles**: The System SHALL provide a floating_particles() factory that generates slowly drifting small dots using Perlin-like noise for movement

16. **Sparkle**: The System SHALL provide a sparkle() factory that generates brief bright points that flash randomly at different positions with sine-based intensity

17. **Smoke/Fog**: The System SHALL provide a smoke_fog(intensity) factory that generates a semi-transparent drifting cloud layer using scrolling Perlin noise field blended onto the frame

18. **Progress Bar**: The System SHALL provide a progress_bar() factory that renders an animated bar showing video playback progress as a filled rectangle where width = total_width * (t / duration)

#### Scenario: Applying scan lines effect

- **WHEN** user applies scan_lines(intensity=0.3) effect
- **THEN** horizontal dark lines appear at regular intervals across the frame, creating a CRT monitor effect

#### Scenario: Applying snow effect

- **WHEN** user applies snow(density=50) effect
- **THEN** white dots fall from the top of the screen with downward velocity, creating a snowfall effect

#### Scenario: Applying light leak

- **WHEN** user applies light_leak(intensity=0.4) effect
- **THEN** bright colored blobs appear near the frame edges, simulating light leaking through the lens

### Requirement: Stylization Effects

**Original Requirement**: (Implied by effects catalog)

The System SHALL implement stylization effects that create artistic video looks.

**MODIFIED**:

The System SHALL implement stylization effects in a new `engine/effects/stylize.py` module:

1. **Edge Detection**: The System SHALL provide an edge_detection(threshold1, threshold2) factory that shows only edges as white lines on black background using cv2.Canny

2. **Sketch/Pencil**: The System SHALL provide a sketch() factory that creates black and white pencil drawing look using cv2.pencilSketch

3. **Oil Painting**: The System SHALL provide an oil_painting(sigma_s, sigma_r) factory that creates smooth, painterly brush-stroke look using cv2.stylization

4. **Emboss**: The System SHALL provide an emboss() factory that creates raised/stamped surface illusion using convolution with emboss kernel [-2, -1, 0, -1, 2, 1]

5. **Halftone**: The System SHALL provide a halftone(dot_size) factory that creates dots of varying size based on local luminance, mapping luminance to dot radius

6. **Chromatic Aberration**: The System SHALL provide a chromatic_aberration(offset) factory that creates subtle RGB channel offset (shift R channel +2px, B channel -2px)

7. **Glitch - RGB Split**: The System SHALL provide a glitch_rgb_split() factory that creates large offset between color channels (shift R/G/B by 5-20px)

8. **Glitch - Block Displacement**: The System SHALL provide a glitch_block_displacement() factory that creates rectangular blocks shifted horizontally using random row-slice offsets

9. **Glitch - Scan Line Shift**: The System SHALL provide a glitch_scan_line_shift() factory that creates individual rows displaced horizontally using per-row random horizontal offsets

10. **Glitch - Color Corruption**: The System SHALL provide a glitch_color_corruption() factory that creates random color channel swaps in rectangular regions

11. **CRT/Retro**: The System SHALL provide a crt_retro() factory that combines scan lines + barrel distortion + color bleed for a retro monitor look

12. **VHS/Tape Distortion**: The System SHALL provide a vhs_tape_distortion() factory that combines horizontal jitter + color bleed + noise bands for a VHS tape effect

13. **Threshold**: The System SHALL provide a threshold() factory that creates pure black and white image with no grays using np.where(gray > threshold, 255, 0)

14. **Dithering**: The System SHALL provide a dithering() factory that applies threshold with error diffusion using Floyd-Steinberg algorithm on grayscale

15. **Mosaic/Stained Glass**: The System SHALL provide a mosaic_stained_glass() factory that creates Voronoi-style colored regions using random Voronoi cells filled with mean colors

#### Scenario: Applying edge detection

- **WHEN** user applies edge_detection(threshold1=100, threshold2=200) effect
- **THEN** only edges between the specified intensity thresholds appear as white lines on black background

#### Scenario: Applying oil painting

- **WHEN** user applies oil_painting(sigma_s=150, sigma_r=0.25) effect
- **THEN** the frame has a smooth, painterly brush-stroke appearance with reduced detail

#### Scenario: Applying CRT retro effect

- **WHEN** user applies crt_retro() effect
- **THEN** the frame shows scan lines + barrel distortion + color bleed simulating an old CRT monitor

### Requirement: Typography Effects

**Original Requirement**: (Implied by effects catalog in Phase 6 but planned for Phase 2)

The System SHALL implement typography effects for animated text overlays.

**MODIFIED**:

The System SHALL implement typography effects in a new `engine/typography/animated_text.py` module:

1. **Static Text**: The System SHALL provide a static_text(text, x, y, font, color) factory that draws text at a fixed position using PIL ImageDraw.text

2. **Fade In/Out Text**: The System SHALL provide fade_in_text(text, duration) and fade_out_text(text, duration) factories that make text appear/disappear from/to fully transparent using alpha blending

3. **Motion Effects**: The System SHALL provide fly_in(direction), fly_out(direction), scale_up(), scale_down(), bounce_in(), and elastic_in() factories that animate text position or scale using easing functions

4. **Content-Based Effects**: The System SHALL provide typewriter(), word_by_word_reveal(), word_highlight(), and kinetic_typography() factories that animate text based on content (characters appearing one by one, word-by-word reveal, etc.)

5. **Visual Enhancements**: The System SHALL provide drop_shadow(), outline(), and glow() factories that add visual enhancements to text (shadow behind, stroke border, soft light halo)

6. **Layout Effects**: The System SHALL provide lower_third(direction), ticker(text, speed), and vertical_scroll(text) factories that create animated layout elements (bars, scrolling text)

7. **Utility**: The System SHALL provide counter(start, end) and subtitle_karaoke_sweep() factories for utility functions (counting number, karaoke sweep highlight)

#### Scenario: Static text overlay

- **WHEN** user applies static_text("Hello", x=100, y=100, font=None, color=(255,255,255))
- **THEN** white text "Hello" appears at position (100, 100) on the frame

#### Scenario: Kinetic typography with TTS

- **WHEN** user applies kinetic_typography() effect with TTS word timing data
- **THEN** each word animates (scale, bounce, fly, etc.) at its start timestamp, creating dynamic, word-by-word visual emphasis

## ADDED Requirements

### Requirement: Spatial Effects

**Original Requirement**: (Not explicitly listed in Phase 2 but implied by effects catalog)

The System SHALL implement spatial effects that modify pixel positions or geometry.

**MODIFIED**:

The System SHALL implement spatial effects in a new `engine/effects/spatial.py` module:

1. **Rotate**: The System SHALL provide a rotate(angle) factory that rotates the frame around its center using cv2.getRotationMatrix2D and cv2.warpAffine

2. **Flip Horizontal/Vertical**: The System SHALL provide flip_horizontal() and flip_vertical() factories that mirror the frame left-right or top-bottom using cv2.flip

3. **Camera Shake**: The System SHALL provide a camera_shake(intensity) factory that adds random jitter to the crop position (or frame) using random offsets smoothed with scipy.signal.savgol_filter

4. **Perspective Tilt**: The System SHALL provide a perspective_tilt(tilt_x, tilt_y) factory that creates fake 3D rotation using cv2.getPerspectiveTransform and cv2.warpPerspective

5. **Barrel Distortion**: The System SHALL provide a barrel_distortion(strength) factory that creates lens bulge/fisheye effect using cv2.remap with radial displacement field

6. **Pincushion Distortion**: The System SHALL provide a pincushion_distortion(strength) factory that creates inverse lens effect using cv2.remap with inverse radial field

7. **Crop (Static)**: The System SHALL provide a crop(x1, y1, x2, y2) factory that extracts a fixed sub-region using array slicing

8. **Crop (Animated)**: The System SHALL provide an animated_crop(rect_start, rect_end) factory that extracts a moving/resizing sub-region using interpolated crop coordinates with easing

#### Scenario: Rotating a frame

- **WHEN** user applies rotate(45) effect
- **THEN** the frame rotates 45 degrees clockwise around its center

#### Scenario: Camera shake effect

- **WHEN** user applies camera_shake(intensity=5) effect
- **THEN** the frame shows random jitter with smoothed offsets, simulating handheld camera movement

### Requirement: Temporal Effects

**Original Requirement**: (Implied by effects catalog)

The System SHALL implement temporal effects that use more than the current frame.

**MODIFIED**:

The System SHALL implement temporal effects in a new `engine/effects/temporal.py` module:

1. **Motion Trail**: The System SHALL provide a motion_trail(num_frames, fade_factor) factory that blends the current frame with N previous frames using a ring buffer and weighted averaging

2. **Ghosting**: The System SHALL provide a ghosting() factory that creates a faint copy of the immediately previous frame using blend: output = frame * 0.7 + prev_frame * 0.3

3. **Strobe**: The System SHALL provide a strobe(frequency, color) factory that alternates between the current frame and a solid color based on frequency: frame if (t * freq) % 1 > 0.5 else solid_color

4. **Freeze Frame**: The System SHALL provide a freeze_frame(freeze_time, duration) factory that holds a single frame for specified duration by caching the frame at freeze_time and returning it for duration

5. **Flash Frame**: The System SHALL provide a flash_frame(timestamp, color) factory that returns a solid color frame at the exact timestamp, normal frame otherwise

#### Scenario: Motion trail effect

- **WHEN** user applies motion_trail(num_frames=5, fade_factor=0.8) effect
- **THEN** current frame is blended with previous 5 frames with decreasing opacity, creating a trailing ghost effect

#### Scenario: Freeze frame

- **WHEN** user applies freeze_frame(freeze_time=2.5, duration=1.0) effect
- **THEN** the frame at t=2.5s is held and displayed for the next 1.0 second, even as the underlying clip would normally change

## REMOVED Requirements

None - No requirements are removed, only expanded with new functionality.

## RENAMED Requirements

None - No requirement names are changed.
