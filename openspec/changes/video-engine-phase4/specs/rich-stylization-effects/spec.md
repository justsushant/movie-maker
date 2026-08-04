## ADDED Requirements

### Requirement: Rich stylization effects

The system SHALL provide a library of stylization effects for creating unique visual identities in video frames.

#### Scenario: Apply edge detection effect

- **WHEN** user applies edge detection effect to a video clip
- **THEN** system shows only edges as white lines on black background using OpenCV's Canny edge detector
- Frame shape and dtype are preserved (HxWx3 uint8)
- Threshold values are configurable for edge sensitivity
- Creates sketch/outline look
- Effect can be chained with other effects

#### Scenario: Apply sketch/pencil effect

- **WHEN** user applies sketch effect to a video clip
- **THEN** system creates black and white pencil drawing look using OpenCV's pencilSketch function
- Frame shape and dtype are preserved
- Sigma parameters (sigma_s, sigma_r, shade) are configurable for detail control
- Creates artistic pencil drawing aesthetic
- Effect can be chained with other effects

#### Scenario: Apply oil painting effect

- **WHEN** user applies oil painting effect to a video clip
- **THEN** system creates smooth, painterly brush-stroke look using OpenCV's stylization function
- Frame shape and dtype are preserved
- Sigma parameters (sigma_s, sigma_r) are configurable for brush stroke size
- Creates artistic oil painting aesthetic
- Effect can be chained with other effects

#### Scenario: Apply emboss effect

- **WHEN** user applies emboss effect to a video clip
- **THEN** system creates raised/stamped surface illusion using convolution with emboss kernel [[-2,-1,0],[-1,1,1],[0,1,2]]
- Frame shape and dtype are preserved
- Creates 3D embossed look
- Effect can be chained with other effects

#### Scenario: Apply halftone effect

- **WHEN** user applies halftone effect to a video clip
- **THEN** system maps luminance to dot radius and draws dots on a grid creating vintage printing look
- Frame shape and dtype are preserved
- Dot size and spacing are configurable
- Creates vintage halftone/printing aesthetic
- Effect can be chained with other effects

#### Scenario: Apply chromatic aberration effect

- **WHEN** user applies chromatic aberration effect to a video clip
- **THEN** system creates subtle RGB channel offset simulating lens fringing by shifting R channel +2px and B channel -2px
- Frame shape and dtype are preserved
- Offset amount is configurable (typically small, 1-5px)
- Creates subtle color separation at edges
- Effect can be chained with other effects

#### Scenario: Apply glitch RGB split effect

- **WHEN** user applies glitch RGB split effect to a video clip
- **THEN** system creates large offset between color channels by shifting R/G/B by 5-20px in different directions using numpy.roll
- Frame shape and dtype are preserved
- Max offset is configurable
- Creates color separation/distortion effect
- Effect can be chained with other effects

#### Scenario: Apply glitch block displacement effect

- **WHEN** user applies glitch block displacement effect to a video clip
- **THEN** system creates rectangular blocks shifted horizontally using random horizontal row-slice offsets
- Frame shape and dtype are preserved
- Block size and offset range are configurable
- Creates blocky glitch aesthetic
- Effect can be chained with other effects

#### Scenario: Apply glitch scan line shift effect

- **WHEN** user applies glitch scan line shift effect to a video clip
- **THEN** system creates visual artifact where individual rows are displaced horizontally using per-row random horizontal pixel offsets
- Frame shape and dtype are preserved
- Offset range is configurable
- Creates scan line distortion effect
- Effect can be chained with other effects

#### Scenario: Apply glitch color corruption effect

- **WHEN** user applies glitch color corruption effect to a video clip
- **THEN** system swaps RGB channels randomly in rectangular regions creating unnatural color corruption
- Frame shape and dtype are preserved
- Region size and swap probability are configurable
- Creates color corruption artifact
- Effect can be chained with other effects

#### Scenario: Apply CRT/retro effect

- **WHEN** user applies CRT effect to a video clip
- **THEN** system combines scan line mask + barrel remap + slight channel blur to create CRT monitor look
- Frame shape and dtype are preserved
- Creates retro CRT aesthetic
- Effect can be chained with other effects

#### Scenario: Apply VHS/tape distortion effect

- **WHEN** user applies VHS effect to a video clip
- **THEN** system creates horizontal jitter + color bleed + noise bands simulating VHS tape distortion
- Frame shape and dtype are preserved
- Jitter amount, noise intensity are configurable
- Creates retro VHS aesthetic
- Effect can be chained with other effects

#### Scenario: Apply threshold/high contrast B&W effect

- **WHEN** user applies threshold effect to a video clip
- **THEN** system converts frame to pure black and white with no grays using numpy where(gray > threshold, 255, gray)
- Frame shape and dtype are preserved
- Threshold value is configurable (0-255)
- Creates high contrast monochrome look
- Effect can be chained with other effects
