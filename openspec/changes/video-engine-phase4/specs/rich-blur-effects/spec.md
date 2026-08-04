## ADDED Requirements

### Requirement: Rich blur effects

The system SHALL provide a library of blur and focus effects for cinematic depth and motion effects in video production.

#### Scenario: Apply motion blur effect

- **WHEN** user applies motion blur effect to a video clip
- **THEN** system applies directional streak effect simulating camera movement using convolution with a line kernel at specified angle
- Frame shape and dtype are preserved (HxWx3 uint8)
- Blur direction is configurable (0-360 degrees)
- Blur amount (kernel length) is configurable
- Effect can be chained with other effects

#### Scenario: Apply radial blur effect

- **WHEN** user applies radial blur effect to a video clip
- **THEN** system creates blur radiating from center point outward by sampling pixels along radial lines and averaging them
- Frame shape and dtype are preserved
- Blur intensity decreases with distance from center
- Effect can be chained with other effects

#### Scenario: Apply zoom blur effect

- **WHEN** user applies zoom blur effect to a video clip
- **THEN** system creates blur radiating outward simulating fast zoom feel by blending multiple scaled copies of frame
- Frame shape and dtype are preserved
- Zoom intensity is configurable via scale range
- Effect can be chained with other effects

#### Scenario: Apply tilt-shift/miniature effect

- **WHEN** user applies tilt-shift effect to a video clip
- **THEN** system creates sharp horizontal band in middle of frame with blur above and below using gradient mask controlling per-pixel blur radius
- Frame shape and dtype are preserved
- Creates miniature/dollhouse look
- Effect can be chained with other effects

#### Scenario: Apply depth-of-field effect

- **WHEN** user applies depth-of-field effect to a video clip with depth map
- **THEN** system applies blur intensity proportional to distance from focal plane using per-pixel variable-radius Gaussian blur driven by depth map
- Frame shape and dtype are preserved
- Focal depth is configurable
- Gracefully degrades to no blur if depth map is not provided
- Effect can be chained with other effects

#### Scenario: Apply sharpen effect

- **WHEN** user applies sharpen effect to a video clip
- **THEN** system enhances edges and fine detail using unsharp mask: frame + alpha * (frame - blurred)
- Frame shape and dtype are preserved
- Sharpen amount (alpha) is configurable
- Uses Gaussian blur for base blurred frame
- Effect can be chained with other effects

#### Scenario: Apply pixelate/mosaic effect

- **WHEN** user applies pixelate effect to a video clip
- **THEN** system creates blocky mosaic/low-res effect by downscaling frame with INTER_NEAREST and upscaling back to original resolution
- Frame shape and dtype are preserved
- Creates retro/pixelated look
- Effect can be chained with other effects

#### Scenario: Apply bilateral blur effect

- **WHEN** user applies bilateral blur effect to a video clip
- **THEN** system smooths flat regions while preserving sharp edges using OpenCV's bilateralFilter function
- Frame shape and dtype are preserved
- Reduces noise while maintaining edges
- Parameters (d, sigmaColor, sigmaSpace) are configurable
- Effect can be chained with other effects

#### Scenario: Apply box blur effect

- **WHEN** user applies box blur effect to a video clip
- **THEN** system applies fast uniform blur using equal-weight kernel via OpenCV's blur function
- Frame shape and dtype are preserved
- More performant than Gaussian blur
- Kernel size is configurable
- Effect can be chained with other effects

#### Scenario: Apply animated blur effect

- **WHEN** user applies animated blur effect to a video clip
- **THEN** system varies blur intensity over clip duration using easing-driven animated kernel size parameter
- Frame shape and dtype are preserved
- Blur starts at initial size and progresses to final size
- Effect can be chained with other effects
