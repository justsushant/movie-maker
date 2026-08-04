# Subtitle Timestamp Reset Bugfix - Requirements

## Overview

Critical bug causing subtitle timestamps to reset mid-video, resulting in missing subtitles for 30-50% of video content and momentary flashing of incorrect subtitles during sentence transitions.

## Problem Statement

The Kokoro TTS engine processes long text in multiple batches, with each batch returning timestamps starting from 0. The current implementation only calculates the time offset once per paragraph (before processing any batches), causing all tokens from the second batch onward to have incorrect timestamps that overlap with earlier content.

### Impact
- **Missing subtitles**: 13-20 seconds of content in typical videos have no correct subtitle timing
- **Subtitle flashing**: Wrong sentences briefly appear during transitions
- **Affects all real-world scenarios**: Every test case with content >30 seconds is broken

## User Stories

### US-1: Accurate Subtitle Timing Throughout Video
**As a** content creator  
**I want** subtitles to appear at the correct time throughout the entire video  
**So that** viewers can follow along with the narration from start to finish

**Acceptance Criteria:**
1. Subtitle timestamps must be continuous and monotonically increasing
2. No timestamp resets should occur mid-video
3. All audio content must have corresponding subtitle timing
4. The maximum subtitle timestamp should match the audio duration (±0.5s tolerance)

### US-2: Smooth Subtitle Transitions
**As a** viewer  
**I want** smooth transitions between subtitle sentences  
**So that** I'm not distracted by flashing or incorrect text

**Acceptance Criteria:**
1. No previous sentence should flash when transitioning to the next sentence
2. Subtitle transitions should be clean with no overlapping incorrect content
3. Gap between sentences should be handled gracefully (blank or hold last word)

### US-3: Reliable Multi-Batch TTS Processing
**As a** developer  
**I want** the TTS engine to correctly handle multi-batch generation  
**So that** long-form content is processed reliably

**Acceptance Criteria:**
1. Time offsets must be calculated per batch, not per paragraph
2. Each batch's tokens must have offsets based on all previously accumulated audio
3. The implementation must work for any number of batches
4. Audio and subtitle timing must remain synchronized

## Technical Context

### Root Cause
Located in `tts/kokoro_engine.py`, method `KokoroTTSEngine.generate()`:

```python
# Current buggy implementation (lines 66-91)
for paragraph in paragraphs:
    generator = self._pipeline(paragraph, ...)
    
    paragraph_audio = []
    paragraph_tokens = []
    
    # Collects ALL tokens from ALL batches
    for result in generator:
        paragraph_audio.append(result.audio.cpu().numpy())
        paragraph_tokens.extend(result.tokens)  # ❌ Batch 2+ have reset timestamps
    
    # Offset calculated ONCE per paragraph
    time_offset = sum(len(seg) for seg in audio_segments) / 24000
    
    # Same offset applied to ALL tokens
    for token in paragraph_tokens:
        all_tokens.append(TTSToken(
            start_ts=token.start_ts + time_offset,  # ❌ Wrong for batch 2+
            end_ts=token.end_ts + time_offset
        ))
```

### Evidence from Tests

| Test Case | Audio Duration | Max Subtitle Time | Missing Content |
|-----------|---------------|-------------------|-----------------|
| educational_explainer | 43.27s | 27.77s | 15.5s (36%) |
| news_announcement | 46.45s | 26.48s | 19.97s (43%) |
| product_demo | 45.30s | 26.98s | 18.32s (40%) |
| story_narration | 39.67s | 23.70s | 15.97s (40%) |
| tutorial_walkthrough | 41.60s | 28.43s | 13.17s (32%) |

All tests show timestamp resets occurring at segment 6-8, around the 23-28 second mark.

## Constraints

1. **Backward Compatibility**: Fix must not break existing API or change output format
2. **Performance**: No significant performance degradation
3. **Kokoro API**: Must work with Kokoro's generator-based API (cannot change external library)
4. **Multi-paragraph Support**: Must continue to support multi-paragraph text input

## Success Metrics

1. **Zero timestamp resets** in all integration tests (verified by debug script)
2. **100% subtitle coverage** - max subtitle timestamp matches audio duration (±0.5s)
3. **All 5 existing integration tests pass** with corrected timing
4. **No regressions** - all other tests continue to pass

## Implementation Scope

This is a **minimal, surgical fix**:
- **Single file change**: `tts/kokoro_engine.py` (lines 66-91)
- **Core change**: Move token processing inside batch loop (~10 lines)
- **Validation**: Existing integration tests + debug script
- **Estimated time**: 20-30 minutes total

## Out of Scope

- Changing the Kokoro TTS library itself
- Modifying the subtitle rendering system
- Changing the JSON output format
- Performance optimizations beyond the fix

## Dependencies

- Kokoro TTS library (≥ 0.9.4)
- Existing test suite in `tests/integration/test_real_world_scenarios.py`
- Debug scripts: `debug_timestamp_issue.py`, `debug_audio_duration.py`

## References

- Bug analysis: `BUG_ANALYSIS.md`
- Affected file: `tts/kokoro_engine.py`
- Test outputs: `output/test/test_real_world_scenarios/*/output_moviepy.json`
