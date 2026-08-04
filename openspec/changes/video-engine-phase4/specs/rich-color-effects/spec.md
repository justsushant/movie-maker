## ADDED Requirements

### Requirement: Rich color effects

The system SHALL provide a comprehensive library of color grading effects for professional video production, enabling users to apply various color transformations to video frames.

#### Scenario: Apply grayscale transformation

- **WHEN** user applies grayscale effect to a video clip
- **THEN** system renders all frames in black and white using weighted RGB channel averaging
- Frame shape and dtype are preserved (HxWx3 uint8)
- Effect can be chained with other color effects

#### Scenario: Apply invert/negative effect

- **WHEN** user applies invert effect to a video clip
- **THEN** system renders all frames with colors reversed (255 - pixel_value)
- Frame shape and dtype are preserved
- Effect can be chained with other color effects

#### Scenario: Apply sepia effect

- **WHEN** user applies sepia effect to a video clip
- **THEN** system renders all frames with warm brown vintage tone using 3x3 color matrix multiplication
- Frame shape and dtype are preserved
- Output has red channel > green channel > blue channel (sepia characteristic)
- Effect can be chained with other color effects

#### Scenario: Apply hue shift effect

- **WHEN** user applies hue shift effect to a video clip
- **THEN** system rotates all colors around the color wheel by converting to HSV, adding offset to H channel, and converting back to RGB
- Frame shape and dtype are preserved
- Hue value wraps around 360 degrees
- Effect can be chained with other color effects

#### Scenario: Apply color temperature adjustment

- **WHEN** user applies warm color temperature effect to a video clip
- **THEN** system increases red channel and decreases blue channel proportionally
- Frame shape and dtype are preserved
- Pixel values are clamped to [0, 255]
- Cool temperature does the inverse (decrease red, increase blue)
- Effect can be chained with other color effects

#### Scenario: Apply tint/color overlay effect

- **WHEN** user applies tint effect to a video clip with a specified RGB color and opacity
- **THEN** system blends each pixel linearly between original frame and tint color using alpha
- Frame shape and dtype are preserved
- Alpha value is in range [0, 1]
- Effect can be chained with other color effects

#### Scenario: Apply gamma correction

- **WHEN** user applies gamma correction effect to a video clip
- **THEN** system applies non-linear brightness curve using power function: ((frame / 255) ** gamma) * 255
- Frame shape and dtype are preserved
- Gamma values > 1.0 darken, < 1.0 brighten, 1.0 has no effect
- Pixel values are clamped to [0, 255]
- Effect can be chained with other color effects

#### Scenario: Apply curves/LUT transformation

- **WHEN** user applies curves effect with a custom lookup table (LUT) per RGB channel
- **THEN** system maps each pixel value through 256-element lookup tables for each channel
- Frame shape and dtype are preserved
- Allows arbitrary color curves via table lookup
- Effect can be chained with other color effects

#### Scenario: Apply channel mixer effect

- **WHEN** user applies channel mixer effect to a video clip
- **THEN** system cross-blends RGB channels using a 3x3 weight matrix
- Frame shape and dtype are preserved
- Weights matrix is applied as linear transformation
- Effect can be chained with other color effects

#### Scenario: Apply duotone effect

- **WHEN** user applies duotone effect to a video clip with two endpoint colors
- **THEN** system converts frame to grayscale, then interpolates between two colors based on luminance
- Frame shape and dtype are preserved
- Creates two-tone color grading look
- Effect can be chained with other color effects

#### Scenario: Apply tricolor/gradient map effect

- **WHEN** user applies tricolor effect to a video clip with multiple color stops
- **THEN** system converts frame to grayscale, then maps luminance to N-color gradient using lookup
- Frame shape and dtype are preserved
- Creates gradient color grading with multiple control points
- Effect can be chained with other color effects

#### Scenario: Apply cinematic teal-orange effect

- **WHEN** user applies cinematic teal-orange effect to a video clip
- **THEN** system converts frame to HSV and adjusts shadows (low luminance) toward teal and highlights (high luminance) toward warm orange
- Frame shape and dtype are preserved
- Creates popular Hollywood color grade
- Effect can be chained with other color effects

#### Scenario: Apply bleach bypass effect

- **WHEN** user applies bleach bypass effect to a video clip
- **THEN** system creates desaturated, high-contrast film look by blending grayscale with original and boosting contrast
- Frame shape and dtype are preserved
- Creates vintage film aesthetic
- Effect can be chained with other color effects

#### Scenario: Apply cross-process effect

- **WHEN** user applies cross-process effect to a video clip
- **THEN** system applies per-channel S-curve adjustments to create unnatural color shifts
- Frame shape and dtype are preserved
- Creates lomography film aesthetic
- Effect can be chained with other color effects

#### Scenario: Apply auto white balance

- **WHEN** user applies auto white balance effect to a video clip
- **THEN** system corrects color cast by scaling each RGB channel to equal the mean luminance (gray-world algorithm)
- Frame shape and dtype are preserved
- Removes unwanted color tints automatically
- Effect can be chained with other color effects

#### Scenario: Apply vibrance effect

- **WHEN** user applies vibrance effect to a video clip
- **THEN** system boosts saturation selectively on pixels with low saturation values while preserving highly saturated pixels
- Frame shape and dtype are preserved
- Creates more natural-looking color enhancement than uniform saturation
- Effect can be chained with other color effects

#### Scenario: Apply color pulse/flash effect

- **WHEN** user applies color pulse effect to a video clip
- **THEN** system modulates frame brightness over time using sine wave envelope with specified frequency and amplitude
- Frame shape and dtype are preserved
- Pulse oscillates around base brightness (no net change over full cycle)
- Effect can be chained with other color effects

#### Scenario: Apply fade to color effect

- **WHEN** user applies fade to color effect to a video clip
- **THEN** system interpolates entire frame linearly from original frame toward specified RGB color over clip duration
- Frame shape and dtype are preserved
- At progress=0.0, output equals original frame; at progress=1.0, output equals target color
- Effect can be chained with other color effects

#### Scenario: Apply thermal/infrared effect

- **WHEN** user applies thermal effect to a video clip
- **THEN** system converts frame to grayscale and applies false-color heat map lookup using OpenCV's COLORMAP_JET
- Frame shape and dtype are preserved
- Creates thermal camera / night vision look
- Effect can be chained with other color effects
