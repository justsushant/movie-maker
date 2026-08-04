# Subtitle Timestamp Reset Bug Analysis

## Summary

Subtitles are missing in later parts of videos, and there's a momentary flash of the previous sentence when transitioning between sentences. This affects all real-world scenario test cases.

## Root Cause

The `KokoroTTSEngine.generate()` method in `tts/kokoro_engine.py` has a critical timestamp offset bug:

1. **Kokoro's generator yields multiple batches** - The `KPipeline` generator yields results in batches, each batch containing audio chunks and tokens with timestamps relative to that batch (starting from 0).

2. **Offset calculated only once per paragraph** - The current code calculates `time_offset` once per paragraph based on previous audio segments, but doesn't account for multiple batches within a single paragraph.

3. **Timestamps reset mid-paragraph** - When the generator yields a second batch, those tokens have timestamps starting from 0 again, but the code applies the same offset that was calculated before processing any batches.

## Evidence

### Test Results
All 5 real-world scenario tests show the same pattern:

| Test Case | Audio Duration | Max Subtitle Time | Reset at Segment | Gap |
|-----------|---------------|-------------------|------------------|-----|
| educational_explainer | 43.27s | 27.77s | 7 | 15.5s missing |
| news_announcement | 46.45s | 26.48s | 8 | 19.97s missing |
| product_demo | 45.30s | 26.98s | 6 | 18.32s missing |
| story_narration | 39.67s | 23.70s | 7 | 15.97s missing |
| tutorial_walkthrough | 41.60s | 28.43s | 7 | 13.17s missing |

### Example from educational_explainer.txt

Input: Single paragraph, no newlines (7 sentences)

Output JSON shows:
- Sentences 1-7: timestamps 0.3s → 27.775s ✅
- Sentence 8: timestamps 0.275s → 5.45s ❌ (should be ~28s → ~33s)
- Sentence 9: timestamps 5.45s → 6.75s ❌ (should be ~33s → ~35s)
- Sentences 10-11: continue from 6.8s ❌ (should be ~35s → ~43s)

The audio file is 43.27 seconds (complete), but subtitles only cover up to 27.77s before resetting.

## The Bug in Code

```python
# tts/kokoro_engine.py, lines 66-91
for paragraph in paragraphs:
    generator = self._pipeline(paragraph, voice=..., speed=...)
    
    paragraph_audio = []
    paragraph_tokens = []
    
    # BUG: This loop collects ALL tokens from ALL batches
    for result in generator:
        paragraph_audio.append(result.audio.cpu().numpy())
        paragraph_tokens.extend(result.tokens)  # Tokens from batch 2+ have reset timestamps!
    
    # BUG: Offset calculated ONCE, before processing tokens
    time_offset = sum(len(seg) for seg in audio_segments) / 24000 if audio_segments else 0
    
    # BUG: Same offset applied to ALL tokens, even those from later batches
    for token in paragraph_tokens:
        if token.start_ts is not None and token.end_ts is not None:
            all_tokens.append(TTSToken(
                text=token.text,
                whitespace=token.whitespace,
                start_ts=token.start_ts + time_offset,  # Wrong for batch 2+
                end_ts=token.end_ts + time_offset        # Wrong for batch 2+
            ))
```

## Correct Approach

The offset must be calculated and applied **per batch**, not per paragraph:

```python
for paragraph in paragraphs:
    generator = self._pipeline(paragraph, voice=..., speed=...)
    
    paragraph_audio = []
    
    for result in generator:
        # Calculate offset based on audio accumulated SO FAR
        time_offset = sum(len(seg) for seg in audio_segments) / 24000
        time_offset += sum(len(chunk) for chunk in paragraph_audio) / 24000
        
        # Apply offset to THIS batch's tokens
        for token in result.tokens:
            if token.start_ts is not None and token.end_ts is not None:
                all_tokens.append(TTSToken(
                    text=token.text,
                    whitespace=token.whitespace,
                    start_ts=token.start_ts + time_offset,
                    end_ts=token.end_ts + time_offset
                ))
        
        # Then add audio
        paragraph_audio.append(result.audio.cpu().numpy())
    
    if paragraph_audio:
        audio_segments.append(np.concatenate(paragraph_audio))
```

## Impact

1. **Missing subtitles** - The latter part of videos (typically 30-50% of content) has no subtitles or incorrect subtitle timing
2. **Subtitle flashing** - When transitioning between sentences, the previous sentence briefly appears because the renderer is looking up timestamps that don't exist or are out of order
3. **Affects all real-world scenarios** - Every test case with realistic content length (>30 seconds) is impacted

## Next Steps

1. Fix `tts/kokoro_engine.py` to calculate offset per batch
2. Re-run all integration tests to verify fix
3. Consider adding validation to detect timestamp resets in the pipeline
4. Add unit tests for multi-batch TTS generation
