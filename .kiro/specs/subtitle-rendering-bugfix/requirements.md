# Requirements Document

## Introduction

This document specifies requirements for fixing two critical subtitle rendering bugs in the KokoroMoviePy project. These bugs were discovered through comprehensive integration testing and affect subtitle display in narrow videos (phone portrait mode) and word-highlight mode transitions.

The bugs cause:
1. Text overflow beyond video boundaries in phone-sized videos due to overestimated character widths
2. Sudden sentence breaks mid-display in word-highlight mode due to incorrect word filtering logic

## Glossary

- **Subtitle_Renderer**: The component responsible for drawing subtitle text onto video frames
- **Character_Width_Estimator**: The algorithm that estimates how many characters fit in available screen width
- **Word_Highlight_Layout**: The layout strategy that displays full sentences with individual word highlighting
- **Chunk**: A portion of a sentence that fits within the maximum text width constraint
- **Active_Chunk**: The chunk that should be displayed at a given timestamp
- **Edge_Clipping**: When subtitle pixels appear at the leftmost or rightmost column of the video frame
- **Max_Text_Width**: The maximum horizontal space available for subtitle text (width × max_width_ratio - 2 × x_margin)
- **Word_Index**: The position of a word within a segment's word list, used to track which words belong to which chunk

## Requirements

### Requirement 1: Accurate Character Width Estimation

**User Story:** As a content creator, I want subtitles to fit properly within narrow video frames, so that text is not clipped or unnecessarily wrapped.

#### Acceptance Criteria

1. WHEN the Character_Width_Estimator calculates maximum characters per line, THE System SHALL use a character-to-pixel ratio that produces estimation errors of 17% or less
2. WHEN text is measured for wrapping decisions, THE System SHALL maximize use of available screen width without causing overflow
3. WHEN a sentence is shorter than Max_Text_Width, THE System SHALL NOT split it into multiple chunks
4. THE Character_Width_Estimator SHALL use a ratio of 0.50 × font_size for average character width

### Requirement 2: Prevent Horizontal Edge Clipping

**User Story:** As a content creator, I want all subtitle text to appear fully within the video frame, so that no characters are cut off at the edges.

#### Acceptance Criteria

1. WHEN subtitles are rendered at any timestamp, THE Subtitle_Renderer SHALL ensure no text pixels appear in the leftmost column of the frame
2. WHEN subtitles are rendered at any timestamp, THE Subtitle_Renderer SHALL ensure no text pixels appear in the rightmost column of the frame
3. WHEN text width is calculated, THE System SHALL account for both x_margin and max_width_ratio constraints
4. FOR ALL video dimensions and subtitle modes, Edge_Clipping SHALL NOT occur

### Requirement 3: Consistent Word Display in Word-Highlight Mode

**User Story:** As a content creator, I want word-highlight mode to show consistent word sets without sudden breaks, so that viewers can follow the sentence smoothly.

#### Acceptance Criteria

1. WHEN Word_Highlight_Layout displays a chunk, THE System SHALL show only words that belong to the Active_Chunk
2. WHEN transitioning between chunks, THE System SHALL NOT show words from multiple chunks simultaneously
3. WHEN filtering words for display, THE System SHALL use a deterministic method that correctly identifies which words belong to each chunk
4. FOR ALL sentences that fit within Max_Text_Width, THE System SHALL display them as a single chunk without breaks
5. WHEN a sentence contains duplicate words, THE System SHALL correctly identify which instance belongs to each chunk

### Requirement 4: Multiline Wrapping Accuracy

**User Story:** As a content creator, I want long sentences to wrap correctly across multiple lines, so that all text is readable without overflow.

#### Acceptance Criteria

1. WHEN multiline mode is enabled and text exceeds Max_Text_Width, THE System SHALL wrap text into multiple lines
2. WHEN text is wrapped, THE System SHALL ensure each line fits within Max_Text_Width
3. WHEN calculating line breaks, THE System SHALL use the improved Character_Width_Estimator
4. WHEN multiline mode is disabled and text exceeds Max_Text_Width, THE System SHALL split text into time-based chunks

### Requirement 5: Maintain Test Coverage

**User Story:** As a developer, I want all existing stress tests to continue passing, so that bug fixes do not introduce regressions.

#### Acceptance Criteria

1. WHEN bug fixes are applied, THE System SHALL pass all parametrized stress tests in test_subtitle_stress.py
2. WHEN testing phone portrait videos (720x1280, 1080x1920), THE System SHALL pass edge clipping assertions
3. WHEN testing word-highlight mode, THE System SHALL display words consistently without sudden breaks
4. WHEN testing multiline mode with long paragraphs, THE System SHALL wrap text correctly without overflow
5. FOR ALL combinations of text cases, video dimensions, and subtitle modes, THE System SHALL render subtitles without errors

### Requirement 6: Preserve Existing Functionality

**User Story:** As a developer, I want bug fixes to be minimal and targeted, so that existing working features remain unaffected.

#### Acceptance Criteria

1. WHEN character width estimation is improved, THE System SHALL maintain compatibility with all subtitle modes (sentence, word, word-highlight, stacking)
2. WHEN word filtering logic is fixed, THE System SHALL NOT affect sentence-only or word-only modes
3. WHEN changes are applied, THE System SHALL preserve all existing configuration options and their behaviors
4. THE System SHALL maintain the same API surface for SubtitleLayoutContext, SubtitleConfig, and layout classes
5. WHEN internal data structures are enhanced, THE System SHALL maintain backward compatibility with existing code that uses those structures

### Requirement 7: Robust Word-to-Chunk Association

**User Story:** As a developer, I want the system to reliably track which words belong to which chunks, so that word filtering is unambiguous and correct.

#### Acceptance Criteria

1. WHEN chunks are created from a sentence, THE System SHALL record which words from the original segment belong to each chunk
2. WHEN a chunk is displayed, THE System SHALL use the recorded word associations to determine which words to show
3. WHEN a sentence contains duplicate words, THE System SHALL distinguish between different instances by their position
4. THE System SHALL handle empty or whitespace-only words without causing errors in word-to-chunk association

### Requirement 8: Test Validation and Regression Detection

**User Story:** As a developer, I want to validate changes through comprehensive testing, so that I can confirm fixes work correctly and detect any regressions.

#### Acceptance Criteria

1. WHEN code changes are made, THE Developer SHALL run the full test suite using `make test-stress` or `pytest tests/test_subtitle_stress.py`
2. WHEN tests fail after changes, THE Developer SHALL analyze whether failures are due to legitimate bugs being fixed or new regressions introduced
3. WHEN test failures occur, THE System SHALL provide clear diagnostic output showing which test case failed and why
4. WHEN bug fixes are complete, THE Developer SHALL evaluate whether additional unit tests are needed to prevent future regressions
5. IF new edge cases are discovered during testing, THE Developer SHALL add corresponding test cases to the test suite
