# Subtitle Timestamp Reset Bugfix - Design

## Design Overview

This design addresses the timestamp reset bug by restructuring the batch processing loop in `KokoroTTSEngine.generate()` to calculate time offsets per batch rather than per paragraph.

## Architecture

### Current Flow (Buggy)
```
Text Input
    ↓
Split into paragraphs
    ↓
For each paragraph:
    ↓
    Generate all batches → Collect all tokens
    ↓
    Calculate offset ONCE (based on previous paragraphs)
    ↓
    Apply same offset to ALL tokens ❌
    ↓
Output: Tokens with reset timestamps
```

### Fixed Flow
```
Text Input
    ↓
Split into paragraphs
    ↓
For each paragraph:
    ↓
    For each batch:
        ↓
        Calculate offset (based on ALL previous audio)
        ↓
        Apply offset to THIS batch's tokens ✅
        ↓
        Accumulate audio
    ↓
Output: Tokens with continuous timestamps
```

## Detailed Design

### Component: KokoroTTSEngine

**File:** `tts/kokoro_engine.py`  
**Method:** `generate(text: str) -> TTSResult`

#### Current Implementation Issues

1. **Batch collection before offset calculation**
   ```python
   for result in generator:
       paragraph_audio.append(result.audio.cpu().numpy())
       paragraph_tokens.extend(result.tokens)  # Accumulate all
   
   time_offset = calculate_once()  # Too late!
   ```

2. **Single offset for all tokens**
   ```python
   for token in paragraph_tokens:  # All tokens get same offset
       all_tokens.append(TTSToken(
           start_ts=token.start_ts + time_offset  # Wrong for batch 2+
       ))
   ```

#### Fixed Implementation

```python
def generate(self, text: str) -> TTSResult:
    paragraphs = re.split(r'\n+', text.strip())
    
    audio_segments = []
    all_tokens = []
    
    for paragraph in paragraphs:
        generator = self._pipeline(
            paragraph,
            voice=self._config.voice,
            speed=self._config.speed
        )
        
        paragraph_audio = []
        
        for result in generator:
            # Calculate offset based on ALL audio accumulated so far
            # This includes: previous paragraphs + current paragraph batches
            time_offset = (
                sum(len(seg) for seg in audio_segments) / 24000 +
                sum(len(chunk) for chunk in paragraph_audio) / 24000
            )
            
            # Apply offset to THIS batch's tokens immediately
            for token in result.tokens:
                if token.start_ts is not None and token.end_ts is not None:
                    all_tokens.append(TTSToken(
                        text=token.text,
                        whitespace=token.whitespace,
                        start_ts=token.start_ts + time_offset,
                        end_ts=token.end_ts + time_offset
                    ))
            
            # Then accumulate audio for next iteration
            paragraph_audio.append(result.audio.cpu().numpy())
        
        # Concatenate paragraph audio and add to segments
        if paragraph_audio:
            audio_segments.append(np.concatenate(paragraph_audio))
    
    # Concatenate all audio
    if audio_segments:
        audio = np.concatenate(audio_segments)
    else:
        audio = np.array([])
    
    return TTSResult(
        audio=audio,
        sample_rate=24000,
        tokens=all_tokens
    )
```

### Key Changes

1. **Move token processing inside batch loop**
   - Process tokens immediately when each batch arrives
   - Calculate offset before processing each batch

2. **Dynamic offset calculation**
   - `time_offset = previous_paragraphs_audio + current_paragraph_batches_audio`
   - Recalculated for every batch

3. **Maintain audio accumulation order**
   - Calculate offset BEFORE adding current batch audio
   - Ensures offset reflects audio duration up to (but not including) current batch

## Validation Strategy

### Primary Validation: Existing Integration Tests

**5 Existing Tests (Must All Pass)**
- `test_educational_explainer` - 43s video, currently fails at 27s
- `test_product_demo` - 45s video, currently fails at 27s
- `test_story_narration` - 40s video, currently fails at 24s
- `test_tutorial_walkthrough` - 42s video, currently fails at 28s
- `test_news_announcement` - 46s video, currently fails at 26s

These tests already validate:
- File creation (audio, video, JSON)
- JSON structure validity
- Subtitle segment existence

### Secondary Validation: Debug Scripts

**Automated Checks (Already Implemented)**

1. **`debug_timestamp_issue.py`** - Detects timestamp resets
   - Run after fix to confirm zero resets
   - Currently detects 1 reset per test case

2. **`debug_audio_duration.py`** - Validates audio/subtitle sync
   - Confirms max subtitle timestamp matches audio duration
   - Currently shows 13-20s gaps

### Correctness Verification

**Quick Manual Check (Optional)**
- Play one test video (e.g., `educational_explainer`)
- Verify subtitles appear throughout entire duration
- Confirm no flashing during transitions

## Correctness Properties

The fix must satisfy these properties (validated by existing tests):

### Property 1: Timestamp Monotonicity
**Validates:** US-1 AC 1.1, 1.2

Timestamps must continuously increase (or stay same), never reset or go backwards.

**Validation:** Debug script `debug_timestamp_issue.py` checks for resets

### Property 2: Complete Audio Coverage  
**Validates:** US-1 AC 1.3, 1.4

Subtitle timestamps must span the full audio duration (±0.5s tolerance).

**Validation:** Debug script `debug_audio_duration.py` compares audio vs subtitle duration

### Property 3: Batch Offset Accumulation
**Validates:** US-3 AC 3.1, 3.2

Each batch's offset must account for all previously accumulated audio (previous paragraphs + current paragraph batches).

**Validation:** Integration tests with long-form content (>30s) that trigger multiple batches

## Edge Cases

### Edge Case 1: Empty Text
- **Input:** Empty string or whitespace only
- **Expected:** Empty audio array, empty token list
- **Handling:** Existing code handles this correctly

### Edge Case 2: Single Word
- **Input:** "Hello"
- **Expected:** One batch, one token, timestamps start at 0
- **Handling:** No offset needed, works correctly

### Edge Case 3: Very Long Text
- **Input:** Text generating 10+ batches
- **Expected:** Timestamps continuously increase across all batches
- **Handling:** Fixed implementation handles any number of batches

### Edge Case 4: Multiple Paragraphs
- **Input:** "Para 1\n\nPara 2\n\nPara 3"
- **Expected:** Timestamps increase across paragraph boundaries
- **Handling:** Outer loop accumulates audio_segments correctly

### Edge Case 5: Tokens with None Timestamps
- **Input:** Special characters that Kokoro doesn't time
- **Expected:** Skip these tokens (existing behavior)
- **Handling:** `if token.start_ts is not None` check remains

## Performance Considerations

### Impact Analysis
- **Time Complexity:** O(n) → O(n) (unchanged)
- **Space Complexity:** O(n) → O(n) (slightly better - removes intermediate list)
- **Computational Cost:** Negligible increase (offset calc per batch vs per paragraph)
- **Typical batch count:** 2-5 batches for 30-60s videos

### Expected Performance
- **No measurable degradation** - offset calculation is trivial (sum + division)
- **Slightly better memory usage** - no intermediate `paragraph_tokens` list
- **Same audio processing time** - no changes to TTS generation

## Rollback Plan

If the fix causes unexpected issues:

1. **Immediate Rollback:** Revert `tts/kokoro_engine.py` to previous version
2. **Validation:** Run existing tests to confirm rollback successful
3. **Investigation:** Analyze what went wrong with the fix
4. **Alternative Approach:** Consider post-processing fix in `SentenceGrouper` instead

## Documentation Updates

### Code Comments
- Add detailed comment explaining batch-level offset calculation
- Document why offset must be calculated before adding current batch audio

### Architecture Docs
- Update `docs/how_it_works.md` to explain batch processing
- Add section on timestamp offset calculation

### API Docs
- No changes needed (internal implementation detail)

## Migration Notes

- **No API changes:** External callers see no difference
- **No data format changes:** JSON output format unchanged
- **Backward compatible:** Existing code continues to work
- **Test updates:** Add new validation checks, existing tests should pass
