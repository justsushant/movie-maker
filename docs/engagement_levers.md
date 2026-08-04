# Engagement Levers and Limits

This document maps every knob in the PRISM pipeline to the engagement
dimension it affects, describes current technical and creative limits, and
points to runnable examples that exercise them.

---

## Engagement dimensions

| Dimension | What it is | Why it matters for short-form |
|-----------|------------|-------------------------------|
| **Pacing** | How often cuts and visual changes happen | Short-form thrives on fast, purposeful pacing (2–4 s per clip) |
| **Visual variety** | Mix of motion, colour, and style across clips | Monotony kills watch-time; variety rewards staying |
| **Rhythm** | Alignment of cuts and effects with audio | Rhythm creates a subconscious sense of polish |
| **Narrative clarity** | Spoken word + on-screen text reinforcing each other | Viewers scroll away when they can't follow |
| **Style** | Coherent or intentional visual look | A strong style signals "this was made on purpose" |

---

## Lever reference

### Pacing

| Lever | Where | Range / notes |
|-------|-------|---------------|
| `ImageClip.duration` | `engine/scene.py` | Shorter = faster pacing.  2–4 s is typical for short-form; 1 s is maximum intensity. |
| `Transition.duration` | `engine/scene.py` | Shorter transitions feel snappier.  0.3–0.8 s is the useful range. |
| Number of clips | Scene construction | More clips = more variety, but each clip's effective screen time shrinks. |
| `fade_in` / `fade_out` effects | `engine/effects.py` | Smooth per-clip entry/exit; keeps cuts from feeling jarring. |

### Visual variety

| Lever | Where | Range / notes |
|-------|-------|---------------|
| `ImageClip.motion` | `engine/scene.py` | 9 presets: `KEN_BURNS_ZOOM_IN/OUT`, `PAN_LEFT/RIGHT/UP/DOWN`, `ZOOM_IN/OUT`, `STATIC`.  Alternate between presets for variety. |
| `Transition.type` | `engine/scene.py` | 25 types across blend, geometric, and animated categories.  Mixing 3–5 distinct types avoids monotony without visual chaos. |
| Per-clip effect chains | `ImageClip.effects` | Each clip can have its own effect stack.  Use a consistent *base* style and vary one or two accent effects per clip. |

### Rhythm

| Lever | Where | Range / notes |
|-------|-------|---------------|
| `BeatSync.NEAREST_BEAT` | `Transition.sync` | Snaps transition start to the nearest detected beat in the audio. |
| `BeatSync.BEAT_GRID` | `Transition.sync` | Snaps both start and end to beat boundaries for rhythm-locked cuts. |
| `Scene.audio` | `engine/scene.py` | Path to audio file for beat/onset analysis.  When using `generate_video_from_text`, set this to the TTS output path (`output_dir / "output_moviepy.wav"`) — the file is created before the planner runs. |
| Audio-reactive effects | `engine/effects.py` | `OnsetFlash`, `OnsetZoomPulse`, `EnergyZoom`, `EnergyBrightness`, `EnergyShake`, `SpectralColorShift`.  These require `AudioSync` from the planner and currently need a two-stage render (see Limits below). |

### Narrative clarity

| Lever | Where | Range / notes |
|-------|-------|---------------|
| `SubtitleMode` | `subtitle/config.py` | `SENTENCE_WITH_WORD_HIGHLIGHT` is the most engaging mode — shows the full sentence with the current word highlighted. |
| `SubtitleConfig.highlight_color` | `subtitle/config.py` | A warm yellow `(255, 220, 50)` on white `(255, 255, 255)` is a proven combination. |
| `text_overlay()` effect | `engine/effects.py` | Adds a text label to any clip.  Useful for opening hooks or section titles. |
| `vertical_align` / `y_margin` | `subtitle/config.py` | `"bottom"` with 5–8 % margin keeps text visible without occluding images. |

### Style

| Lever | Where | Range / notes |
|-------|-------|---------------|
| Effect chains | `engine/effects.py` | Pre-built recipes: *cinematic* (gamma, saturation, vignette, colour temperature), *retro VHS* (CRT, scan lines, chromatic aberration), *glitch* (RGB split, scan line shift), *dreamy* (blur, light leak, hue shift), *noir* (threshold B&W, vignette). |
| Resolution / aspect ratio | `Scene.resolution` | `(1080, 1920)` = 9:16 vertical for Reels/TikTok/Shorts; `(1920, 1080)` = 16:9 landscape. |
| `film_grain()` | `engine/effects.py` | Small amounts (0.03–0.06) add organic texture without noise. |

---

## Current limits

### Technical

| Limit | Detail |
|-------|--------|
| **Scene duration vs TTS duration** | The pipeline uses `max(audio_duration, timeline_duration)`.  If the scene is shorter than the narration, the last frame is held.  If longer, there is silence at the end.  You must manually size clip durations so the scene covers the narration.  See *Duration Alignment* in `docs/video_engine.md`. |
| **Audio-reactive effects need two stages** | `OnsetFlash`, `EnergyZoom`, etc. require an `AudioSync` object that is only available after `ScenePlanner.plan()`.  The `generate_video_from_text()` API does not expose `AudioSync` back to the caller, so audio-reactive effects cannot be used through that entry point today.  Workaround: run TTS separately, then build and render the scene manually (see `examples/demo_phase3_audio_reactive.py`). |
| **Beat sync uses speech, not music** | When `Scene.audio` points to the TTS output, beats are detected from *speech* rhythm (pauses, emphasis), not from a musical track.  The effect is subtler than music-driven sync. |
| **No effect/transition recommendation** | Any effect or transition runs on any clip.  There is no validation or suggestion system — it is up to the user to choose what looks good.  See `openspec/changes/video-engine-phase4/specs/effect-transition-validity/spec.md` for future plans. |
| **Render time** | Each frame is rendered sequentially in Python (NumPy + OpenCV).  A 30 s video at 30 fps = 900 frames; heavy effects (sketch, blur, halftone) add ~10-20 ms per frame.  Expect 1–3 minutes per 30 s video on modern hardware. |

### Creative

| Limit | Guidance |
|-------|----------|
| **Effect stacking** | More than 4–5 effects per clip risks muddying the image.  A strong base style (2–3 effects) plus an accent (vignette, grain) is usually enough. |
| **Transition variety** | Using more than 4–5 distinct transition types in a single video can feel chaotic.  Pick 2–3 main types and one accent type. |
| **Clip duration floor** | Below ~1.5 s per clip, motion presets don't have enough time to be visible, and subtitles may not be readable. |
| **Vertical vs landscape** | Vertical (9:16) works best for short-form platforms; landscape (16:9) for YouTube or presentations.  Source images should match the target aspect ratio for best quality. |

---

## Quick-start recipes

### Cinematic short-form (recommended starting point)

```python
from engine.effects import (
    gamma_correction, saturation, contrast, vignette,
    color_temperature, film_grain, fade_in, fade_out,
)

effects = [
    fade_in(0.3),
    gamma_correction(1.15),
    saturation(0.95),
    contrast(1.05),
    vignette(0.45),
    color_temperature(6200),
    film_grain(0.04),
    fade_out(0.3),
]
```

### High-energy glitch

```python
from engine.effects import (
    glitch_rgb_split, chromatic_aberration, scan_lines,
    contrast, fade_in, fade_out,
)

effects = [
    fade_in(0.2),
    glitch_rgb_split(12),
    chromatic_aberration(6),
    scan_lines(1, 0.2),
    contrast(1.1),
    fade_out(0.2),
]
```

### Dreamy / ethereal

```python
from engine.effects import (
    gaussian_blur, light_leak, hue_shift, saturation,
    fade_in, fade_out,
)

effects = [
    fade_in(0.4),
    gaussian_blur(3),
    light_leak(0.4),
    hue_shift(20),
    saturation(1.2),
    fade_out(0.4),
]
```

---

## Runnable examples

| Script | What it does |
|--------|-------------|
| `examples/engagement_max_demo.py` | Single run with every lever maxed: TTS + subtitles + images + varied motion + cinematic effects + varied transitions + beat sync. |
| `examples/engagement_benchmark.py` | Renders the same narration through 5 presets (baseline → max) for side-by-side comparison. |
| `examples/demo_phase3_audio_reactive.py` | Two-stage render demonstrating audio-reactive effects (OnsetFlash, EnergyZoom, etc.). |
| `examples/dragon/create_dragon_video_phase4.py` | 7 effect styles applied to a dragon image set. |
| `examples/mahabharata/create_mahabharata_video_phase4.py` | 8 effect styles applied to a Mahabharata image set. |
