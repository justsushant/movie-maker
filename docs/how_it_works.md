# How It Works — Technical Deep Dive

This document explains the full pipeline from text input to final video output, covering the data flow, key algorithms, and the dependency injection architecture.

## Architecture Overview

```
main.py (orchestrator)
  │
  ├─ loads config from ─── config.py
  │
  ├─ injects settings into ─── tts_pipeline.py
  │   └─ produces: .wav audio, .json timestamps, .srt subtitles
  │
  └─ injects settings into ─── renderer.py
      └─ produces: .mp4 video
```

**Dependency injection:** `tts_pipeline` and `renderer` never import `config`. They receive all paths, voices, dimensions, and colors as function/constructor arguments. `main.py` is the only file that knows about `config.py` and wires everything together.

---

## Stage 1: TTS Audio Generation

**File:** `tts_pipeline.py` → `MoviePySubtitleExtractor.__init__`

Kokoro TTS converts text to speech and provides **token-level timing metadata** — this is the key ingredient that makes word-highlighting possible.

### How it works:

1. Input text is split into paragraphs (`\n+` boundaries)
2. Each paragraph is fed to `KPipeline`, which yields results containing:
   - `result.audio` — raw audio as a PyTorch tensor
   - `result.tokens` — list of tokens with `start_ts`, `end_ts`, `text`, and `whitespace`
3. Audio segments from all paragraphs are concatenated into one continuous WAV (24 kHz)
4. A cumulative `time_offset` is tracked so that timestamps across paragraphs remain globally correct

### Output: Raw tokens with global timestamps

```
Token("The", start=0.225, end=0.325)
Token("novel", start=0.325, end=0.750)
Token(",", start=0.750, end=0.775)    ← standalone punctuation
...
```

---

## Stage 2: Punctuation Merging

**File:** `tts_pipeline.py` → `_merge_punctuation()`

Kokoro sometimes produces standalone tokens for punctuation (commas, periods, quotes, em-dashes). If left as-is, the video renderer would try to highlight a comma by itself, which looks broken.

### Algorithm:

```
For each token:
  if token has NO alphanumeric characters AND there's a previous word:
    → append token's text to previous word
    → extend previous word's end_time to cover this token
  else:
    → start a new word entry
```

### Before merging:
```
["Wait", ",", "\"", " ", "he"]  ← 5 separate tokens
```

### After merging:
```
["Wait,\" ", "he"]  ← 2 words (punctuation absorbed)
```

---

## Stage 3: Sentence Grouping

**File:** `tts_pipeline.py` → `_group_into_sentences()`

Words are grouped into sentence-sized chunks for display. Each sentence becomes one "line" shown on screen.

### Splitting rules (in order of priority):

1. **Sentence-ending punctuation** — split after `.`, `!`, or `?`
2. **Duration limit** — split if a sentence exceeds 5 seconds (prevents very long lines)
3. **End of input** — the last word always closes the current sentence

### Output structure:

```json
{
  "sentence_text": "Today is a new beginning!",
  "start_time": 2.5,
  "end_time": 4.8,
  "words": [
    {"text": "Today ", "start_time": 2.5, "end_time": 2.9},
    {"text": "is ",    "start_time": 2.9, "end_time": 3.0},
    ...
  ]
}
```

This hierarchical structure is what makes the rolling highlight possible — the renderer knows both *which sentence to display* and *which word within it to highlight*.

---

## Stage 4: Video Rendering

**File:** `renderer.py` → `make_frame()`

MoviePy calls `make_frame(t)` for every frame of the video. This function builds a PIL image from scratch 30 times per second.

### Frame generation algorithm for time `t`:

```
1. FIND the sentence where start_time ≤ t ≤ end_time
   → If no sentence covers time t, return a blank black frame

2. MEASURE each word's pixel width using the font
   → Calculate the total width of the sentence

3. CENTER the sentence horizontally and vertically on the canvas

4. DRAW each word:
   → If the word's start_time ≤ t ≤ end_time: draw in YELLOW (highlighted)
   → Otherwise: draw in WHITE (default)
```

### Visual result at t=3.1:

```
               Today is a new beginning!
                        ^^
                      YELLOW (active word)
```

### Final assembly (`create_video`):

1. Load the subtitle JSON and audio WAV
2. Determine video duration = max(audio length, last subtitle timestamp)
3. Create a `VideoClip` with `make_frame` as the frame generator
4. Attach the audio track
5. Export to MP4 (H.264 video + AAC audio)

---

## Data Flow Diagram

```
files/input.txt
      │
      ▼
  ┌───────────────────────────────┐
  │  tts_pipeline.py              │
  │                               │
  │  text ──► Kokoro TTS          │
  │            │                  │
  │            ├─► raw tokens     │
  │            │    │             │
  │            │    ▼             │
  │            │  merge punct.    │
  │            │    │             │
  │            │    ▼             │
  │            │  group sentences │
  │            │    │             │
  │            ▼    ▼             │
  │         .wav   .json + .srt  │
  └───────────────────────────────┘
      │         │
      ▼         ▼
  ┌───────────────────────────────┐
  │  renderer.py                  │
  │                               │
  │  for each frame at time t:    │
  │    find sentence ──► draw     │
  │    find active word ──► highlight│
  │                               │
  │         ▼                     │
  │      .mp4                     │
  └───────────────────────────────┘
```

---

## Why This Structure?

| Design choice | Reason |
|---|---|
| Hierarchical JSON (not flat SRT) | Need sentence context + per-word timing simultaneously |
| Punctuation merging | Prevents highlighting bare commas/quotes as separate words |
| 5-second sentence cap | Keeps displayed text readable — avoids extremely long lines |
| Dependency injection | Any module can be tested/replaced independently; data flow is traceable |
| `files/` directory | Separates code from data; `.gitignore` keeps outputs out of version control |
