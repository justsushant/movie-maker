## ADDED Requirements

### Requirement: Rich texture overlays

The system SHALL provide a library of texture and overlay effects for adding production value to video frames.

#### Scenario: Apply scan lines effect

- **WHEN** user applies scan lines effect to a video clip
- **THEN** system creates horizontal dark CRT monitor lines by multiplying every Nth row by a darkening factor
- Frame shape and dtype are preserved (HxWx3 uint8)
- Line frequency and darkening factor are configurable
- Effect can be chained with other effects

#### Scenario: Apply letterbox bars effect

- **WHEN** user applies letterbox effect to a video clip
- **THEN** system adds cinematic black bars at top and bottom of frame by setting top and bottom pixel rows to black (0)
- Frame shape and dtype are preserved
- Middle section is unchanged
- Top and bottom bar heights are configurable
- Effect can be chained with other effects

#### Scenario: Apply border/frame effect

- **WHEN** user applies border effect to a video clip
- **THEN** system draws colored rectangular border around frame or pads frame with colored border
- Frame dimensions may increase for border
- Border color and thickness are configurable
- Border can be inset or outset
- Effect can be chained with other effects

#### Scenario: Apply gradient overlay effect

- **WHEN** user applies gradient overlay effect to a video clip
- **THEN** system generates linear or radial color gradient and blends it onto frame using alpha blending: frame * (1 - alpha) + gradient * alpha
- Frame shape and dtype are preserved
- Gradient colors (start, end) and direction are configurable
- Effect can be chained with other effects

#### Scenario: Apply image watermark effect

- **WHEN** user applies watermark effect to a video clip
- **THEN** system loads watermark image and alpha-composites it at fixed or animated position onto frame
- Frame shape and dtype are preserved
- Watermark path is required
- Position, opacity, and size are configurable
- Effect can be chained with other effects

#### Scenario: Apply pattern overlay effect

- **WHEN** user applies pattern overlay effect to a video clip
- **THEN** system tiles a small pattern array (stripes, dots, grid) and multiplies or blends it onto frame
- Frame shape and dtype are preserved
- Pattern type and scaling are configurable
- Effect can be chained with other effects

#### Scenario: Apply light leak effect

- **WHEN** user applies light leak effect to a video clip
- **THEN** system creates bright colored blobs near frame edges simulating film light leak artifact using Gaussian blobs at random edge positions with additive blend
- Frame shape and dtype are preserved
- Blob color, intensity, and edge positions are configurable
- Creates cinematic light leak aesthetic
- Effect can be chained with other effects

#### Scenario: Apply bokeh overlay effect

- **WHEN** user applies bokeh overlay effect to a video clip
- **THEN** system draws blurred circular light highlights simulating bokeh using circles with radial gradient and additive blend
- Frame shape and dtype are preserved
- Bokeh color, size, count, and blur amount are configurable
- Creates cinematic shallow depth-of-field look
- Effect can be chained with other effects

#### Scenario: Apply dust and scratches effect

- **WHEN** user applies dust and scratches effect to a video clip
- **THEN** system draws random marks and hairline scratches simulating old film damage onto frame using Pillow drawing primitives
- Frame shape and dtype are preserved (HxWx3 uint8)
- Dust and scratch density, color, and size are configurable
- Creates vintage film aesthetic
- Effect can be chained with other effects

#### Scenario: Apply lens flare effect

- **WHEN** user applies lens flare effect to a video clip
- **THEN** system creates bright radial streaks from a light source position simulating lens flare using radial gradient + streak lines at position with additive blend
- Frame shape and dtype are preserved
- Flare position, color, and size are configurable
- Creates cinematic lens flare effect
- Effect can be chained with other effects

#### Scenario: Apply progress bar overlay

- **WHEN** user applies progress bar effect to a video clip
- **THEN** system draws animated bar showing video playback progress where width = total_width * (t / duration)
- Frame shape and dtype are preserved
- Progress bar position, color, and height are configurable
- Effect can be chained with other effects
