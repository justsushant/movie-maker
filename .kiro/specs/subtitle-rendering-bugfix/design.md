# Design Document: Subtitle Rendering Bugfix

## Overview

This design addresses two critical bugs in the subtitle rendering system:

1. **Character Width Overestimation**: The current ratio of 0.55 × font_size overestimates actual character widths by 17-29%, causing unnecessary text wrapping and overflow in narrow videos (phone portrait mode)
2. **Incorrect Word Filtering**: WordHighlightLayout filters words by time overlap rather than chunk membership, causing sudden sentence breaks mid-display

### Root Cause Analysis

**Bug 1 - Deeper Issue:** The fundamental problem is not just the 0.55 ratio, but that we're using character count estimation instead of actual pixel measurements. Even with 0.50, we still have 6-17% error, which can cause overflow in edge cases.

**Bug 2 - Deeper Issue:** The fundamental problem is that chunk creation and word filtering are decoupled. We create chunks from word text, then try to reverse-engineer which words belong to each chunk by matching text strings. This is fragile and error-prone.

### Comprehensive Fixes

**Fix 1 - Character Width (Two-Phase Approach):**
1. **Immediate fix**: Change ratio from 0.55 to 0.50 (reduces error from 17-29% to 6-17%)
2. **Future enhancement**: Track actual measured widths during chunking to eliminate estimation errors entirely

**Fix 2 - Word Filtering (Structural Fix):**
- Modify `_TimedChunk` to store word indices that belong to the chunk
- During chunk creation, track which words go into each chunk
- During rendering, use stored indices to filter words (no text matching needed)

Both changes are localized to `subtitle/layouts.py` and maintain full backward compatibility with existing APIs and configuration options.

## Architecture

The subtitle system follows a three-stage pipeline:

```
Source → Layout → Renderer
```

This bugfix affects only the **Layout** stage, specifically:
- `_max_chars_for_context()` - used by chunking logic
- `_wrap_sentence_text()` - used by multiline wrapping
- `WordHighlightLayout.layout_frame()` - word filtering logic

The changes do not affect:
- Source (JsonSubtitleSource)
- Renderer (PillowSubtitleRenderer)
- Composer (SubtitleFrameComposer)
- Other layout modes (SentenceLayout, WordOnlyLayout, StackingLayout)

## Components and Interfaces

### Modified Functions

#### 1. `_max_chars_for_context(context: SubtitleLayoutContext) -> int`

**Current Implementation:**
```python
def _max_chars_for_context(context: SubtitleLayoutContext) -> int:
    avg_char_px = max(1, int(context.font_size * 0.55))
    return max(8, context.max_text_width_px // avg_char_px)
```

**Fixed Implementation:**
```python
def _max_chars_for_context(context: SubtitleLayoutContext) -> int:
    avg_char_px = max(1, int(context.font_size * 0.50))  # Changed from 0.55
    return max(8, context.max_text_width_px // avg_char_px)
```

**Impact:**
- Used by `_build_single_line_chunks()` for sentence mode and word-highlight mode
- Reduces estimation error from 17-29% to 6-17%
- Allows more text to fit per line without overflow

#### 2. `_wrap_sentence_text(text: str, context: SubtitleLayoutContext) -> List[str]`

**Current Implementation:**
```python
def _wrap_sentence_text(text: str, context: SubtitleLayoutContext) -> List[str]:
    # ... setup code ...
    avg_char_px = max(1, int(context.font_size * 0.55))
    max_chars = max(8, context.max_text_width_px // avg_char_px)
    # ... wrapping logic ...
```

**Fixed Implementation:**
```python
def _wrap_sentence_text(text: str, context: SubtitleLayoutContext) -> List[str]:
    # ... setup code ...
    avg_char_px = max(1, int(context.font_size * 0.50))  # Changed from 0.55
    max_chars = max(8, context.max_text_width_px // avg_char_px)
    # ... wrapping logic ...
```

**Impact:**
- Used by `SentenceLayout._layout_multiline()` for multiline sentence mode
- Better utilization of available screen width
- Fewer unnecessary line breaks

#### 3. `_build_single_line_chunks()` - Enhanced to Track Word Indices

**Current Implementation:**
```python
def _build_single_line_chunks(...) -> List[_TimedChunk]:
    words = segment.words
    # ...
    chunks: List[_TimedChunk] = []
    current_words: List[WordSegment] = []
    current_text = ""

    for w in words:
        # ... chunking logic ...
        chunks.append(
            _TimedChunk(
                text=current_text,
                start_time=current_words[0].start_time,
                end_time=current_words[-1].end_time,
            )
        )
```

**Enhanced Implementation:**
```python
def _build_single_line_chunks(...) -> List[_TimedChunk]:
    words = segment.words
    # ...
    chunks: List[_TimedChunk] = []
    current_words: List[WordSegment] = []
    current_word_indices: List[int] = []  # NEW: Track indices
    current_text = ""

    for i, w in enumerate(words):  # NEW: Use enumerate to get index
        # ... same chunking logic ...
        if current_words and (len(tentative) > max_chars or hit_word_cap):
            chunks.append(
                _TimedChunk(
                    text=current_text,
                    start_time=current_words[0].start_time,
                    end_time=current_words[-1].end_time,
                    word_indices=current_word_indices.copy(),  # NEW
                )
            )
            current_words = [w]
            current_word_indices = [i]  # NEW
            current_text = word_text
        else:
            current_words.append(w)
            current_word_indices.append(i)  # NEW
            current_text = tentative

    if current_words:
        chunks.append(
            _TimedChunk(
                text=current_text,
                start_time=current_words[0].start_time,
                end_time=current_words[-1].end_time,
                word_indices=current_word_indices.copy(),  # NEW
            )
        )
```

**Impact:**
- Each chunk now knows exactly which words from `segment.words` belong to it (by index position)
- Handles duplicate words correctly (uses position, not text matching)
- Handles empty/whitespace words correctly (they're skipped in chunking, so won't be in indices)
- No ambiguity in word filtering

#### 4. `WordHighlightLayout.layout_frame()` - Robust Word Filtering

**Current Implementation:**
```python
# Find which words belong to the active chunk
active_words = []
for w in seg.words:
    # Include words that overlap with the active chunk's time range
    if w.start_time <= active_chunk.end_time and w.end_time >= active_chunk.start_time:
        active_words.append(w)
```

**Problem:** This includes ALL words that have any time overlap with the chunk, not just words that are actually part of the chunk's text.

**Enhanced Implementation:**
```python
# Find which words belong to the active chunk using stored indices
active_words = [seg.words[i] for i in active_chunk.word_indices]
```

**Impact:**
- Direct lookup using stored indices - no ambiguity
- Only shows words that are actually part of the active chunk
- Prevents showing words from adjacent chunks
- Eliminates sudden sentence breaks mid-display
- Robust to punctuation, whitespace, and duplicate words

### Unchanged Components

- **SubtitleLayoutContext**: No changes to data structure or calculation logic
- **SubtitleConfig**: No changes to configuration options
- **ISubtitleLayout**: No changes to interface
- **Other layout classes**: SentenceLayout, WordOnlyLayout, StackingLayout remain unchanged
- **Renderer and Source**: No changes needed

## Data Models

### Modified Data Structure

#### `_TimedChunk` (Enhanced)

**Current:**
```python
@dataclass
class _TimedChunk:
    text: str
    start_time: float
    end_time: float
```

**Enhanced:**
```python
@dataclass
class _TimedChunk:
    text: str
    start_time: float
    end_time: float
    word_indices: List[int]  # NEW: Indices of words from segment.words that belong to this chunk
```

**Rationale:** By storing word indices during chunk creation, we eliminate the need to match words by text later. This makes word filtering robust and unambiguous.

### Unchanged Data Models

- `SubtitleSegment` - unchanged
- `WordSegment` - unchanged
- `PositionedSubtitle` - unchanged
- `SubtitleLayoutContext` - unchanged
- `SubtitleConfig` - unchanged

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Character Width Estimation Accuracy

*For any* font size and text string, when the character width estimator calculates the maximum characters that fit, the estimation error (difference between estimated width and actual PIL-measured width) should be 17% or less.

**Validates: Requirements 1.1**

### Property 2: Text Fits Within Bounds

*For any* text string, video dimensions, and subtitle configuration, when text is wrapped or chunked, each resulting line or chunk should have an actual rendered width less than or equal to max_text_width_px.

**Validates: Requirements 1.2, 4.2**

### Property 3: No Unnecessary Chunking

*For any* sentence and subtitle configuration, if the sentence's actual rendered width is less than or equal to max_text_width_px, then the chunking algorithm should produce exactly one chunk.

**Validates: Requirements 1.3**

### Property 4: No Edge Clipping

*For any* timestamp, video dimensions, subtitle mode, and text content, when a frame is rendered, there should be no non-background pixels in the leftmost column or rightmost column of the frame.

**Validates: Requirements 2.1, 2.2, 2.4**

### Property 5: Correct Width Calculation

*For any* video dimensions and subtitle configuration, the calculated max_text_width_px should equal (width × max_width_ratio) minus (2 × x_margin_px), accounting for integer rounding.

**Validates: Requirements 2.3**

### Property 6: Word-Highlight Shows Only Active Chunk Words

*For any* timestamp and sentence that gets split into multiple chunks, when WordHighlightLayout renders the frame, all displayed words should be present in the active chunk's word list (by index), and no words from other chunks should be displayed.

**Validates: Requirements 3.1, 3.5, 7.1, 7.2, 7.3**

### Property 7: Multiline Wrapping Produces Multiple Lines

*For any* text string that exceeds max_text_width_px, when multiline mode is enabled, the layout should produce two or more PositionedSubtitle objects (one per line).

**Validates: Requirements 4.1**

## Error Handling

### Existing Error Handling (Preserved)

The current implementation has defensive checks that remain unchanged:

1. **Empty text handling**: `_wrap_sentence_text()` returns empty list for empty/whitespace-only text
2. **Minimum character width**: `max(1, int(...))` prevents division by zero
3. **Minimum max_chars**: `max(8, ...)` ensures at least 8 characters per line
4. **Empty segments**: All layout methods check `if not segments: return []`
5. **Empty words**: Word filtering skips empty word text with `if not word_text: continue`

### New Error Handling

The word filtering fix adds robustness:

1. **Index-based filtering**: Using stored indices eliminates text matching ambiguity
2. **Bounds checking**: Indices are guaranteed valid since they're captured during chunk creation
3. **Empty word handling**: Empty words are skipped during chunking, so they won't appear in word_indices

### Edge Cases and Limitations

#### Edge Cases That Are Handled

1. **Single-word sentences**: Work correctly - chunk will have word_indices=[0]
2. **Punctuation-heavy text**: Punctuation is already merged into words by TTS pipeline
3. **Unicode text**: Character width estimation is approximate but works for all character sets
4. **Very narrow screens**: Minimum 8 characters per line ensures some text always displays
5. **Duplicate words**: Handled correctly by index-based filtering (not text matching)
6. **Empty/whitespace words**: Skipped during chunking, won't cause issues

#### Known Limitations

1. **Character width estimation is approximate**: 
   - 0.50 ratio gives 6-17% overestimation
   - Combined with max_width_ratio=0.9, provides ~27% total safety margin
   - Should prevent overflow in vast majority of cases
   - Extreme edge cases (very wide characters, unusual fonts) may still overflow

2. **Font variations not accounted for**:
   - Estimation assumes average character width
   - Monospace vs proportional fonts have different characteristics
   - System uses Helvetica by default, estimation tuned for that

3. **Very long single words**:
   - A single word longer than max_text_width_px will still overflow
   - This is unavoidable without breaking words mid-character
   - Rare in practice (would need 40+ character word in narrow video)

#### Mitigation Strategies

If overflow still occurs in edge cases after applying fixes:

1. **Reduce max_width_ratio**: Change from 0.9 to 0.85 in subtitle_config.py defaults
2. **Increase margins**: Increase x_margin from 0.05 to 0.08
3. **Add PIL measurement**: Future enhancement to measure actual text width during chunking (opt-in)
4. **Font size adjustment**: Automatically reduce font size for very narrow videos

The existing test suite with `_assert_no_horizontal_edge_clipping` will catch any remaining overflow issues.

## Testing Strategy

### Dual Testing Approach

The project uses both unit tests and property-based tests for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across randomized inputs

Both are complementary and necessary. Unit tests catch concrete bugs, property tests verify general correctness.

### Existing Test Suite

The project has comprehensive stress tests in `tests/test_subtitle_stress.py`:

**Test Matrix:**
- 6 text cases: short_single_sentence, long_paragraph, multi_paragraph, punctuation_heavy, unicode_sample, single_word
- 8 video variants: 1080p, 720p, phone portrait (720x1280, 1080x1920), different subtitle modes
- 48 total test combinations (6 × 8)

**Assertions:**
- `_assert_frame_has_subtitle_pixels`: Verifies subtitles are rendered
- `_assert_no_horizontal_edge_clipping`: Verifies no pixels at frame edges (validates Property 4)
- `_assert_sentence_layout_wraps`: Verifies multiline wrapping works (validates Property 7)
- `_assert_single_line_layout`: Verifies single-line mode works

### Running Tests

```bash
# Run full stress test suite
make test-stress

# Or directly with pytest
pytest tests/test_subtitle_stress.py -v

# Run specific test case
pytest tests/test_subtitle_stress.py::test_subtitle_stress_rendering[long_paragraph.txt-phone_1080x1920_sentence_highlight] -v
```

### Property-Based Testing

Python's property-based testing library: **Hypothesis**

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: `# Feature: subtitle-rendering-bugfix, Property N: <property text>`

**Property Test Implementation:**

Each correctness property should be implemented as a separate property-based test:

1. **Property 1 (Character Width Estimation)**: Generate random font sizes (20-80px) and text strings, measure with PIL, compare to estimate
2. **Property 2 (Text Fits Within Bounds)**: Generate random text and configs, wrap/chunk, measure each result
3. **Property 3 (No Unnecessary Chunking)**: Generate sentences that fit, verify single chunk
4. **Property 4 (No Edge Clipping)**: Generate random configs and timestamps, render frames, check edges
5. **Property 5 (Correct Width Calculation)**: Generate random dimensions and configs, verify calculation
6. **Property 6 (Word-Highlight Filtering)**: Generate sentences that split into chunks, verify word membership
7. **Property 7 (Multiline Wrapping)**: Generate long text, verify multiple lines produced

### Test Validation Process

After applying fixes:

1. **Run existing stress tests**: `make test-stress`
2. **Analyze failures**: Determine if failures are due to bugs being fixed or new regressions
3. **Expected changes**: Tests that previously failed due to overflow/clipping should now pass
4. **Unexpected failures**: Investigate and fix any new regressions
5. **Add new tests**: If new edge cases are discovered, add corresponding test cases

### Unit Test Balance

- Focus unit tests on specific examples and edge cases
- Avoid writing too many unit tests - property tests handle input coverage
- Unit tests should focus on:
  - Specific examples demonstrating correct behavior
  - Integration points between components
  - Edge cases (empty text, single word, very long words)
  - Error conditions (invalid inputs, boundary conditions)

## Implementation Notes

### Change Locations

All changes are in `subtitle/layouts.py`:

1. **Line ~76**: `_max_chars_for_context()` - change 0.55 to 0.50
2. **Line ~48**: `_wrap_sentence_text()` - change 0.55 to 0.50  
3. **Line ~68**: `_TimedChunk` dataclass - add `word_indices: List[int]` field
4. **Line ~81-140**: `_build_single_line_chunks()` - track word indices during chunk creation
5. **Line ~268-275**: `WordHighlightLayout.layout_frame()` - use stored indices for word filtering

### Why 0.50 is Sufficient (Not Perfect, But Good Enough)

**Question:** Will changing from 0.55 to 0.50 truly fix overflow issues, or do we need actual PIL measurements?

**Analysis:**
- Current 0.55 ratio: 17-29% overestimation → text wraps too early, can still overflow
- Proposed 0.50 ratio: 6-17% overestimation → better, but still approximate
- Actual PIL measurement: 0% error → perfect, but expensive

**Why 0.50 is the right choice:**

1. **Conservative estimation is intentional**: We want to slightly overestimate to provide safety margin. Perfect measurement would risk overflow due to font rendering variations.

2. **Performance**: PIL measurement requires creating a font object and drawing context for every chunking decision. This would slow down the pipeline significantly.

3. **Existing safety margins**: The system already has built-in safety:
   - `max_width_ratio` defaults to 0.9 (10% margin from edges)
   - `x_margin_px` provides additional padding
   - Combined, these give ~15-20% total safety margin

4. **Empirical evidence**: The bug analysis shows that with 0.50:
   - 87-character text at 40px font: 1740px estimated vs 1482px actual = 17% error
   - With max_width_ratio=0.9 and x_margin, this fits comfortably in 1080px width
   - The 17% overestimation + 10% width ratio margin = ~27% total safety

5. **Test coverage**: The existing stress tests with `_assert_no_horizontal_edge_clipping` will catch any remaining overflow issues across 48 test combinations.

**Conclusion:** The 0.50 ratio provides sufficient accuracy when combined with existing safety margins. If edge cases still appear in testing, we can:
- Reduce `max_width_ratio` from 0.9 to 0.85 (more conservative)
- Add actual PIL measurement as a future enhancement (opt-in for critical cases)

### Testing During Implementation

1. **Make character width changes first** (fixes Bug 1)
   - Change 0.55 to 0.50 in both functions
   - Run stress tests: `make test-stress`
   - Verify phone portrait tests pass edge clipping assertions
   - If any tests still fail, analyze whether we need to adjust max_width_ratio

2. **Make data model change** (prepare for Bug 2 fix)
   - Add `word_indices` field to `_TimedChunk`
   - Update `_build_single_line_chunks()` to populate indices
   - Run stress tests to verify no regressions

3. **Make word filtering change** (fixes Bug 2)
   - Update `WordHighlightLayout.layout_frame()` to use indices
   - Run stress tests to verify word-highlight mode is fixed
   - Verify smooth transitions without sudden breaks

4. **Final validation**
   - Verify all 48 test combinations pass
   - Manually inspect problematic test cases (punctuation_heavy, long_paragraph)
   - Check that no new edge cases emerged

### Backward Compatibility

- No API changes
- No configuration changes
- No data model changes to public interfaces
- Existing code using the subtitle system continues to work unchanged
- Only internal calculation logic is modified

**_TimedChunk Enhancement is Safe:**
- `_TimedChunk` is a private internal class (prefixed with `_`)
- Only used within `subtitle/layouts.py`, not exported
- Not part of any public API or interface
- Adding a field to a dataclass is backward compatible (existing code doesn't access it)
- All existing layout modes (sentence, word, stacking) continue to work unchanged

### Performance Impact

- Negligible: Only changes are two constant values and word filtering logic
- Word filtering is O(n) where n = number of words in segment (typically < 50)
- No additional memory allocation
- No additional file I/O or network calls
