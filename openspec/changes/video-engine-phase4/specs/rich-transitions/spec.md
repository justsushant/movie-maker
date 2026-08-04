## ADDED Requirements

### Requirement: Rich transitions

The system SHALL provide a comprehensive library of transition effects between video clips, completing the transition set from Phase 2.

#### Scenario: Apply push left transition

- **WHEN** user applies push left transition between two clips
- **THEN** both clips move left together: A scrolls left, B follows from right edge
- Frame shape and dtype are preserved (HxWx3 uint8)
- Both clips are visible during transition
- Creates motion effect where camera pans left
- Transition duration is configurable

#### Scenario: Apply push right transition

- **WHEN** user applies push right transition between two clips
- **THEN** both clips move right together: A scrolls right, B follows from left edge
- Frame shape and dtype are preserved
- Both clips are visible during transition
- Creates motion effect where camera pans right
- Transition duration is configurable

#### Scenario: Apply push up transition

- **WHEN** user applies push up transition between two clips
- **THEN** both clips move up together: A scrolls up, B follows from bottom edge
- Frame shape and dtype are preserved
- Both clips are visible during transition
- Creates motion effect where camera pans up
- Transition duration is configurable

#### Scenario: Apply push down transition

- **WHEN** user applies push down transition between two clips
- **THEN** both clips move down together: A scrolls down, B follows from top edge
- Frame shape and dtype are preserved
- Both clips are visible during transition
- Creates motion effect where camera pans down
- Transition duration is configurable

#### Scenario: Apply blinds horizontal transition

- **WHEN** user applies blinds horizontal transition between two clips
- **THEN** horizontal strips alternate between A and B using striped row mask with moving threshold per strip
- Frame shape and dtype are preserved
- Creates venetian blind effect horizontally
- Strip width is configurable
- Transition duration is configurable

#### Scenario: Apply blinds vertical transition

- **WHEN** user applies blinds vertical transition between two clips
- **THEN** vertical strips alternate between A and B using striped column mask with moving threshold per strip
- Frame shape and dtype are preserved
- Creates venetian blind effect vertically
- Strip width is configurable
- Transition duration is configurable

#### Scenario: Apply diamond wipe transition

- **WHEN** user applies diamond wipe transition between two clips
- **THEN** diamond shape expands from center revealing B using Manhattan distance mask (abs(dx) + abs(dy)) < threshold
- Frame shape and dtype are preserved
- Creates diamond wipe effect
- Transition duration is configurable

#### Scenario: Apply zoom through transition

- **WHEN** user applies zoom through transition between two clips
- **THEN** A zooms past camera (scale up + fade) and B appears behind
- Frame shape and dtype are preserved
- Creates dramatic zoom-through effect
- Transition duration is configurable

#### Scenario: Apply whip pan transition

- **WHEN** user applies whip pan transition between two clips
- **THEN** system applies fast motion blur in one direction during switch using motion blur kernel and crossfades in middle
- Frame shape and dtype are preserved
- Direction is configurable (0-360 degrees)
- Blur amount is configurable
- Creates fast, energetic transition
- Transition duration is configurable

#### Scenario: Apply pixelate transition

- **WHEN** user applies pixelate transition between two clips
- **THEN** A pixelates out (increasing block size), B pixelates in using progressive downscale-upscale with crossfade
- Frame shape and dtype are preserved
- Creates blocky pixelated transition effect
- Transition duration is configurable

#### Scenario: Apply glitch transition

- **WHEN** user applies glitch transition between two clips
- **THEN** system creates RGB split + block displacement layered over crossfade intensifying at cut point
- Frame shape and dtype are preserved
- Creates digital glitch transition effect
- Transition duration is configurable
