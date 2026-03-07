# Subtitle Rendering Bug Analysis

## Issues Identified

### Issue 1: Text Overflow in Narrow Videos (Phone Portrait Mode)
**Affected Test Cases:**
- `punctuation_heavy_phone_1080x1920_sentence_highlight`
- `long_paragraph_phone_720x1280_sentence`
- All phone-sized video tests

**Root Cause:**
Character width estimation in `subtitle/layouts.py` is **too high** (overestimates actual width).

**Current Implementation:**
```python
avg_char_px = max(1, int(context.font_size * 0.55))
max_chars = max(8, context.max_text_width_px // avg_char_px)
```

**Problem:**
- Ratio of 0.55 overestimates actual text width by 17-29%
- This causes wrapping logic to think text won't fit when it actually would
- Results in unnecessary line breaks and potential overflow

**Evidence:**
- Font size 40px, text "This is a longer paragraph..." (87 chars)
  - Actual width: 1482px
  - Estimated with 0.55: 1914px (29% error)
  - Estimated with 0.50: 1740px (17% error)

### Issue 2: Sentence Breaks Mid-Display in Word Highlight Mode
**Affected Test Cases:**
- `punctuation_heavy_phone_1080x1920_sentence_highlight`
- All `sentence_with_word_highlight` mode tests

**Root Cause:**
`WordHighlightLayout` in `subtitle/layouts.py` doesn't properly filter words by active chunk.

**Current Implementation:**
```python
# Find which words belong to the active chunk
active_words = []
for w in seg.words:
    # Include words that overlap with the active chunk's time range
    if w.start_time <= active_chunk.end_time and w.end_time >= active_chunk.start_time:
        active_words.append(w)
```

**Problem:**
- Logic includes ALL words that overlap with chunk time range
- Doesn't check if words are actually part of the active chunk
- Results in showing words from multiple chunks simultaneously
- Then suddenly switches to only the last chunk, breaking the sentence mid-display

**Evidence:**
- Sentence: "what?! \"No way,\" she said; then paused and smiled"
- Full sentence fits (902px < 972px max)
- Chunking creates 2 chunks:
  - Chunk 1: "what?! \" No way,\" she said; then paused and" (0.65s - 3.16s)
  - Chunk 2: "smiled" (3.16s - 4.00s)
- At t=2.50s: Shows all 9 words (correct for chunk 1)
- At t=3.50s: Shows only 2 words ('and', 'smiled') - WRONG, should show only 'smiled'

### Issue 3: Multiline Wrapping Doesn't Account for Actual Text Width
**Affected Test Cases:**
- `long_paragraph_720_sentence_multiline`
- All `multiline_enabled: true` tests

**Root Cause:**
Same character width estimation issue as Issue 1, affecting `_wrap_sentence_text()`.

**Problem:**
- Wrapping uses character count estimation instead of actual pixel measurements
- Can result in lines that are too long or too short
- No validation that wrapped lines actually fit within max_text_width_px

## Recommended Fixes

### Fix 1: Improve Character Width Estimation
**Location:** `subtitle/layouts.py` - functions `_wrap_sentence_text()` and `_max_chars_for_context()`

**Change:**
```python
# OLD:
avg_char_px = max(1, int(context.font_size * 0.55))

# NEW:
avg_char_px = max(1, int(context.font_size * 0.50))
```

**Impact:**
- Reduces estimation error from 17-29% to 6-17%
- Better utilization of available screen width
- Fewer unnecessary line breaks

### Fix 2: Fix Word Filtering in WordHighlightLayout
**Location:** `subtitle/layouts.py` - `WordHighlightLayout.layout_frame()`

**Change:**
Instead of filtering by time overlap, filter by which words are actually in the active chunk's text.

**Approach:**
Build a set of word indices that belong to the active chunk, then only show those words.

### Fix 3: Add Safety Margin for Text Width
**Location:** `subtitle_config.py` - default `max_width_ratio`

**Optional Enhancement:**
Consider reducing default `max_width_ratio` from 0.9 to 0.85 to provide more safety margin, especially for narrow screens.

## Testing Strategy

1. Run existing stress tests to verify fixes don't break other cases
2. Specifically verify:
   - Phone portrait videos (720x1280, 1080x1920)
   - Long paragraph with multiline enabled
   - Sentence with word highlight mode
3. Check that `_assert_no_horizontal_edge_clipping` passes
4. Verify smooth transitions between chunks (no sudden breaks)
