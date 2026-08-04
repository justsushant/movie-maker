# Video Generation Engine — Extension Plan

## Context

movie-maker currently generates narrated videos from text: TTS produces audio + word timings, and the renderer composites subtitle frames over a solid-color background. The video output is functional but visually static — no images, no motion, no transitions.

This plan extends the project with a **video generation engine** that stitches images into a timeline, applies motion and visual effects, supports transitions, and renders to video. The existing TTS pipeline is untouched; the engine replaces the rendering layer.

---

## Implementation Status

| Phase | Status | Completion Date | Key Deliverables |
|-------|--------|-----------------|------------------|
| Phase 1: Core Engine | ✅ Complete | 2025 | Scene DSL, camera motion, Ken Burns, planner, renderer |
| Phase 2: Transitions & Effects | ✅ Complete | 2025 | Effect chain, basic transitions, color/texture effects |
| Phase 3: Audio Sync | ✅ Complete | 2025 | Librosa integration, beat sync, audio-reactive effects |
| **Phase 4: Rich Effects** | ✅ **Complete** | **March 2026** | **56 effects + 11 transitions** |
| Phase 5: Depth & Parallax | 🔲 Planned | TBD | Depth maps, parallax layers, depth-of-field |
| Phase 6: Typography | 🔲 Planned | TBD | Animated text, kinetic typography, lower thirds |

**Current Status:** Phase 4 complete with 67 new capabilities (56 effects + 11 transitions). See `.kiro/specs/video-engine-phase4-verification/PHASE4_COMPLETION_REPORT.md` for details.

---

## Architecture

The system uses a **clip-based abstraction** at the user level and a **linear effect chain** internally. No DAG, no tile-based rendering.

```mermaid
flowchart TD
    SceneDSL["Scene DSL (Python dataclasses)"] --> Planner
    AudioAnalysis["Audio Analysis (librosa)"] --> Planner
    Planner["Scene Planner"] --> Timeline["Resolved Timeline"]
    Timeline --> FrameRenderer["Frame Renderer"]
    FrameRenderer --> EffectChain["Per-Clip Effect Chain"]
    EffectChain --> TransitionBlend["Transition Blender"]
    TransitionBlend --> OverlayCompositor["Overlay Compositor (subtitles, text)"]
    OverlayCompositor --> Encoder["FFmpeg Encoder (via MoviePy)"]
```

### Per-frame rendering flow

For each output frame at time `t`:

```mermaid
flowchart LR
    Source["Source Image"] --> Spatial["Spatial Transform (Ken Burns, pan, zoom, parallax)"]
    Spatial --> FrameEffects["Frame Effects (color, blur, grain, vignette)"]
    FrameEffects --> OutputFrame["Clip Frame"]
```

When two clips overlap during a transition:

```mermaid
flowchart LR
    ClipA["Clip A chain"] --> FrameA["frame_a"]
    ClipB["Clip B chain"] --> FrameB["frame_b"]
    FrameA --> Blend["Transition Blend"]
    FrameB --> Blend
    Blend --> Overlays["Overlay (subtitles)"]
    Overlays --> FinalFrame["Output Frame"]
```

---

## Module Structure

New code lives in `engine/`, parallel to the existing modules:

```
engine/
  __init__.py
  scene.py            # Scene DSL: Scene, ImageClip, Transition, MotionPreset, etc.
  planner.py          # Resolves Scene into a concrete timeline with computed params
  timeline.py         # ResolvedTimeline, ResolvedClip (start_time, camera path, effects)
  camera.py           # Virtual camera, motion presets, rect interpolation
  easing.py           # Easing functions (ease-in/out, bounce, elastic, spring, bezier)
  effects/
    __init__.py
    base.py           # Effect base class/protocol: effect(frame, t, params) -> frame
    spatial.py         # Ken Burns, pan, zoom, rotate, perspective, shake, parallax
    color.py           # Brightness, contrast, saturation, hue, temperature, grades, LUT
    blur.py            # Gaussian, motion, radial, zoom, tilt-shift, depth-of-field
    texture.py         # Grain, vignette, scan lines, particles, bokeh, dust, overlays
    stylize.py         # Glitch, CRT, VHS, edge detect, sketch, halftone, chromatic aberration
    temporal.py        # Motion trail, ghosting, strobe, freeze frame
  transitions/
    __init__.py
    base.py            # Transition protocol: transition(frame_a, frame_b, progress) -> frame
    blend.py           # Crossfade, fade-through-black/white/color, dissolve
    geometric.py       # Slide, push, wipe, iris, clock, diamond, blinds, split
    animated.py        # Zoom-through, whip pan, pixelate, glitch transition
  audio/
    __init__.py
    analyzer.py        # Librosa wrapper: beat detection, onset, RMS energy, spectral
    sync.py            # BeatSync, snap transition times to beats, energy curves
  depth/
    __init__.py
    loader.py          # Load user-supplied depth maps, optional model-based estimation
    parallax.py        # Layer splitting, differential motion, compositing
  typography/
    __init__.py
    animated_text.py   # Fly-in, scale, bounce, typewriter, kinetic, lower thirds
  renderer.py          # Frame-based renderer: iterates timeline, applies chains, outputs frames
  output.py            # Encoding: wraps MoviePy/FFmpeg for final video export
```

---

## Dependencies

### New required dependencies

- **opencv-python** — spatial transforms (`warpAffine`, `warpPerspective`, `resize`), blur variants, color space conversions, stylization filters. Enables ~40 effects.
- **librosa** — beat/onset detection, RMS energy envelope, spectral features. Enables ~12 audio-reactive effects.
- **scipy** — easing curves (cubic spline, B-spline), signal smoothing (`savgol_filter`), interpolation. Foundation for all animation.

### New optional dependencies (for depth-based effects)

- **torch** — already present via kokoro
- **transformers** — for MiDaS / Depth Anything depth estimation models. Only needed if users want auto-generated depth maps instead of supplying their own.

### Updated requirements.txt

```
# Existing
kokoro>=0.9.4
soundfile
moviepy
pillow
numpy
pytest

# New - video engine
opencv-python
librosa
scipy
```

---

## Scene DSL (User-Facing API)

The user describes videos declaratively using Python dataclasses. Key types in `engine/scene.py`:

```python
@dataclass
class Scene:
    resolution: tuple[int, int] = (1920, 1080)
    fps: int = 30
    clips: list[ImageClip] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    audio: str | Path | None = None  # for beat analysis

@dataclass
class ImageClip:
    source: str | Path
    duration: float
    motion: MotionPreset = MotionPreset.STATIC
    parallax: bool = False
    depth_map: str | Path | None = None
    effects: list[Effect] = field(default_factory=list)

class MotionPreset(Enum):
    STATIC = "static"
    KEN_BURNS_ZOOM_IN = "ken_burns_zoom_in"
    KEN_BURNS_ZOOM_OUT = "ken_burns_zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SLOW_ZOOM_IN = "slow_zoom_in"

@dataclass
class Transition:
    type: TransitionType = TransitionType.CROSSFADE
    duration: float = 1.0
    easing: EasingType = EasingType.EASE_IN_OUT_CUBIC
    sync: BeatSync = BeatSync.NONE

class TransitionType(Enum):
    CROSSFADE = "crossfade"
    FADE_THROUGH_BLACK = "fade_through_black"
    SLIDE_LEFT = "slide_left"
    PUSH_LEFT = "push_left"
    WIPE_LEFT = "wipe_left"
    IRIS_OPEN = "iris_open"
    ZOOM_THROUGH = "zoom_through"
    WHIP_PAN = "whip_pan"
    GLITCH = "glitch"
    # ... etc
```

---

## Effect System

All effects follow a single protocol defined in `engine/effects/base.py`:

```python
class Effect(Protocol):
    def apply(self, frame: np.ndarray, t: float, progress: float) -> np.ndarray:
        """
        frame: current frame as HxWx3 uint8 numpy array
        t: absolute time in seconds
        progress: 0.0-1.0 within the clip's duration
        """
        ...
```

Effects are applied in list order (linear chain). Each clip carries its own effect list.

---

## Integration with Existing Codebase

The existing TTS pipeline and subtitle system remain unchanged. Integration points:

1. **renderer.py** — `create_video()` currently builds a `SubtitleFrameComposer` as the sole frame source. This will be updated to optionally use the engine's `FrameRenderer` as the base frame source, with subtitles composited on top. When no scene/clips are provided, behavior is identical to today (solid color background).
2. **api/library.py** — `generate_video_from_text()` gains an optional `scene: Scene` parameter. When provided, the engine renders visual content; when absent, falls back to the current solid-color background.
3. **subtitle/composer.py** — `SubtitleFrameComposer` becomes an overlay in the engine pipeline rather than the entire frame generator. Instead of creating a blank `Image.new()`, it receives the engine's frame as `base_image`.
4. **Subtitle config bug** — `generate_video_from_text` currently does not pass `subtitle_config` through to `create_video()`. This will be fixed as part of the integration.

```mermaid
flowchart TD
    Text["Input Text"] --> TTS["TTS Pipeline (unchanged)"]
    TTS --> Audio["Audio WAV"]
    TTS --> Metadata["Word Timing JSON"]

    Scene["Scene DSL (new)"] --> EnginePlanner["Engine Planner (new)"]
    Audio --> AudioAnalyzer["Audio Analyzer (new, librosa)"]
    AudioAnalyzer --> EnginePlanner

    EnginePlanner --> EngineRenderer["Engine Frame Renderer (new)"]
    EngineRenderer --> BaseFrame["Visual Frame (images + effects)"]

    Metadata --> SubtitleOverlay["Subtitle Composer (existing)"]
    BaseFrame --> SubtitleOverlay
    SubtitleOverlay --> FinalFrame["Final Frame"]

    FinalFrame --> MoviePy["MoviePy Encoder (existing)"]
    Audio --> MoviePy
    MoviePy --> MP4["Output MP4"]
```

---

## Implementation Phases

### Phase 1: Core engine scaffold

- Scene DSL dataclasses (Scene, ImageClip, Transition, MotionPreset, enums)
- Easing function library
- Scene planner (resolve clips to timeline with start/end times accounting for transitions)
- Virtual camera and motion presets (Ken Burns, pan, zoom)
- Frame-based renderer skeleton (iterate timeline, load images, apply camera, output frames)
- Integration with existing renderer.py
- Produce a working video: sequence of images with Ken Burns, no transitions yet

### Phase 2: Transitions and effect chain

- Transition protocol and implementations (crossfade, fade-through-black, slide, wipe, iris)
- Effect protocol and first batch of frame effects (brightness, contrast, saturation, vignette, grain)
- Wire effect chain into renderer (source -> spatial -> effects -> output)
- Wire transitions into renderer (detect overlap regions, blend two clips)

### Phase 3: Audio analysis and sync

- Librosa integration (beat detection, onset detection, RMS energy envelope)
- BeatSync on transitions (snap transition times to nearest beat)
- Audio-reactive effect parameters (energy-driven zoom, onset flash)

### Phase 4: Rich effects library ✅ **COMPLETE** (March 2026)

**Status:** Production-ready | **Completion:** 92% | **Tests:** 756 passing

**Implemented:**
- 21 color effects (hue shift, temperature, sepia, LUT, cinematic grades, duotone, tricolor, thermal, etc.)
- 11 blur variants (motion blur, radial, zoom blur, tilt-shift, depth-of-field simulation, etc.)
- 12 texture overlays (bokeh, light leaks, dust, scan lines, lens flare, vignette, etc.)
- 14 stylization effects (glitch variants, CRT, VHS, chromatic aberration, sketch, oil painting, etc.)
- 11 advanced transitions (push variants, blinds, diamond wipe, zoom-through, whip pan, pixelate, glitch)

**Total:** 56 effects + 11 transitions = 67 new capabilities

**Documentation:** See `.kiro/specs/video-engine-phase4-verification/PHASE4_COMPLETION_REPORT.md` for full details.

**Examples:**
- `examples/demo_phase4_rich_effects.py` - Comprehensive showcase
- `examples/PHASE4_SHOWCASE.md` - Usage guide
- `examples/dragon/create_dragon_video_phase4.py` - Dragon scene with effects
- `examples/mahabharata/create_mahabharata_video_phase4.py` - Epic scene with effects

### Phase 5: Depth and parallax

- Depth map loader (user-supplied PNG/EXR)
- Parallax layer splitting and differential motion
- Depth-of-field effect
- Optional: model-based depth estimation (MiDaS / Depth Anything)

### Phase 6: Typography animations

- Animated text elements (fly-in, scale, bounce, typewriter)
- Kinetic typography driven by TTS word timings
- Lower thirds, progress bars, tickers
- Integration with existing subtitle system (animated subtitles as a mode)

---

## Key Design Decisions

- **Clip-based abstraction is the user API.** All complexity is hidden behind `ImageClip`, `Transition`, and `Effect`. Users do not interact with timelines, frames, or effect chains directly.
- **Linear effect chain per clip.** No DAG, no graph engine. Effects apply sequentially: `source -> spatial -> [effect1 -> effect2 -> ...] -> output`. This covers 100% of the target effects.
- **Frame-based rendering.** Each frame is a full HxWx3 numpy array processed in sequence. No tiling. Acceptable for 1080p batch rendering.
- **Python-only rendering initially.** No FFmpeg filter graph compilation. MoviePy handles final encoding. Optimize to FFmpeg filters later if profiling shows need.
- **Effects are pure functions.** `(frame, t, progress) -> frame`. Stateless except for temporal effects which maintain an internal buffer. Easy to test, easy to compose.
- **Transitions are two-input functions.** `(frame_a, frame_b, progress) -> frame`. Clean separation from clip effects.
- **Audio analysis is optional.** If no audio is provided or librosa is not installed, beat sync is skipped and transitions use their declared times. Graceful degradation.

---

## Complete Effects Catalog

### Foundation: Easing Functions

Every animated parameter (position, scale, opacity, color) needs easing. These are pure math with no imaging dependency. Implemented in `engine/easing.py`.

| # | Function | Formula / Notes | Dep |
|---|---|---|---|
| E1 | Linear | `t` | none |
| E2 | Ease-in quadratic | `t^2` | none |
| E3 | Ease-in cubic | `t^3` | none |
| E4 | Ease-in quartic | `t^4` | none |
| E5 | Ease-in quintic | `t^5` | none |
| E6 | Ease-in exponential | `2^(10*(t-1))` | none |
| E7 | Ease-in sine | `1 - cos(t * pi/2)` | none |
| E8 | Ease-in circular | `1 - sqrt(1 - t^2)` | none |
| E9 | Ease-out quadratic | `1 - (1-t)^2` | none |
| E10 | Ease-out cubic | `1 - (1-t)^3` | none |
| E11 | Ease-out quartic | `1 - (1-t)^4` | none |
| E12 | Ease-out quintic | `1 - (1-t)^5` | none |
| E13 | Ease-out exponential | `1 - 2^(-10*t)` | none |
| E14 | Ease-out sine | `sin(t * pi/2)` | none |
| E15 | Ease-out circular | `sqrt(1 - (t-1)^2)` | none |
| E16 | Ease-in-out (all above variants) | Piecewise combination of in/out | none |
| E17 | Bounce | Damped absolute sine | none |
| E18 | Elastic | Damped oscillation with period/amplitude | none |
| E19 | Back (overshoot) | Cubic with overshoot constant (~1.70158) | none |
| E20 | Spring | Damped spring simulation | **scipy** |
| E21 | Custom bezier curve | Cubic bezier evaluation | **scipy** or manual |
| E22 | Step / quantized | `floor(t * n) / n` | none |
| E23 | Cubic spline through keyframes | Smooth path through N control points | **scipy** |

---

### Category 1: Spatial / Camera Effects (16 effects)

Modify geometry -- where pixels come from. Implemented in `engine/effects/spatial.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 1 | Ken Burns | Interpolate between two crop rects over time, resize to output | `crop` then `resize` with easing on rect params | **OpenCV** |
| 2 | Pan left | Slide crop rect rightward across source (scene moves left) | Animated crop x-offset, single axis | **OpenCV** |
| 3 | Pan right | Slide crop rect leftward across source | Animated crop x-offset, reversed | **OpenCV** |
| 4 | Pan up | Slide crop rect downward across source | Animated crop y-offset | **OpenCV** |
| 5 | Pan down | Slide crop rect upward across source | Animated crop y-offset, reversed | **OpenCV** |
| 6 | Zoom in | Shrinking crop rect toward center/subject | Animated crop rect, decreasing size | **OpenCV** |
| 7 | Zoom out | Growing crop rect from center/subject | Animated crop rect, increasing size | **OpenCV** |
| 8 | Rotate | Rotate frame around center by angle(t) | `cv2.getRotationMatrix2D` + `warpAffine` | **OpenCV** |
| 9 | Flip horizontal | Mirror left-right | `cv2.flip(frame, 1)` | **OpenCV** |
| 10 | Flip vertical | Mirror top-bottom | `cv2.flip(frame, 0)` | **OpenCV** |
| 11 | Camera shake / handheld | Random jitter on crop position, smoothed per frame | Random offsets smoothed with `savgol_filter` | numpy + **scipy** |
| 12 | Perspective tilt | Fake 3D rotation (top recedes, bottom forward) | `cv2.getPerspectiveTransform` + `warpPerspective` | **OpenCV** |
| 13 | Barrel distortion | Lens bulge / fisheye effect | `cv2.remap` with radial displacement field | **OpenCV** |
| 14 | Pincushion distortion | Inverse lens effect (edges bulge inward) | `cv2.remap` with inverse radial field | **OpenCV** |
| 15 | Crop (static) | Fixed sub-region of source | `image[y1:y2, x1:x2]` | numpy |
| 16 | Crop (animated) | Sub-region that moves/resizes over time | Interpolated crop coords with easing | numpy |

---

### Category 2: Color Effects (25 effects)

Pixel-level color transforms. Each operates on the frame array and outputs a same-sized array. Implemented in `engine/effects/color.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 17 | Brightness | Lighten/darken uniformly | `frame * factor` clipped to 0-255 | numpy |
| 18 | Contrast | Expand/compress tonal range | Scale pixel values around mean | numpy |
| 19 | Saturation | Increase/decrease color intensity | Convert to HSV, scale S channel, convert back | **OpenCV** |
| 20 | Hue shift | Rotate all colors around the color wheel | Convert to HSV, add offset to H channel | **OpenCV** |
| 21 | Color temperature (warm) | Shift toward amber tones | Increase R channel, decrease B channel | numpy |
| 22 | Color temperature (cool) | Shift toward blue tones | Decrease R channel, increase B channel | numpy |
| 23 | Tint / color overlay | Blend frame with a solid color at some opacity | `frame * (1-a) + color * a` | numpy |
| 24 | Sepia | Warm brownish vintage tone | 3x3 matrix multiply on RGB channels | numpy |
| 25 | Grayscale | Remove all color | Weighted sum of R/G/B or `cv2.cvtColor` | numpy or **OpenCV** |
| 26 | Invert / negative | Reverse all colors | `255 - frame` | numpy |
| 27 | Posterize | Reduce to N discrete color levels | `(frame // step) * step` | numpy |
| 28 | Solarize | Invert pixels above threshold | `where(frame > thresh, 255 - frame, frame)` | numpy |
| 29 | Gamma correction | Non-linear brightness curve | `((frame / 255) ** gamma * 255)` | numpy |
| 30 | Curves / LUT | Map each channel through a custom curve | 256-element lookup table per channel, `cv2.LUT` | numpy or **OpenCV** |
| 31 | Channel mixer | Cross-blend R/G/B channels via weights | 3x3 matrix multiply on channel axis | numpy |
| 32 | Duotone | Map luminance to two endpoint colors | Grayscale then lerp between two RGB colors | numpy |
| 33 | Tricolor / gradient map | Map luminance to N-color gradient | Grayscale then multi-stop colormap lookup | numpy |
| 34 | Cinematic teal-orange | Shadows go teal, highlights go warm orange | HSV selective color adjustment by luminance | **OpenCV** + numpy |
| 35 | Bleach bypass | Desaturated, high-contrast film look | Blend grayscale with original + contrast boost | numpy |
| 36 | Cross-process | Unnatural color shifts (lomography look) | Per-channel S-curve adjustments | numpy |
| 37 | Auto white balance | Correct color cast automatically | Gray-world algorithm: scale each channel to equal mean | numpy |
| 38 | Vibrance | Boost saturation on low-saturation pixels only | Conditional S-channel scaling in HSV based on existing S | **OpenCV** + numpy |
| 39 | Color pulse / flash | Brief brightness spike, animated over time | `frame * (1 + pulse_envelope(t))` with easing | numpy |
| 40 | Fade to color | Lerp entire frame toward a solid color over time | `frame * (1-progress) + color_array * progress` | numpy |
| 41 | Thermal / infrared | False-color heat map look | Grayscale then `cv2.applyColorMap(COLORMAP_JET)` | **OpenCV** |

---

### Category 3: Blur and Focus Effects (11 effects)

Implemented in `engine/effects/blur.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 42 | Gaussian blur | Soft uniform blur with configurable radius | `cv2.GaussianBlur(frame, (k, k), sigma)` | **OpenCV** |
| 43 | Box blur | Fast uniform blur (equal-weight kernel) | `cv2.blur(frame, (k, k))` | **OpenCV** |
| 44 | Motion blur | Directional streak (simulates camera movement) | `cv2.filter2D` with a line kernel at given angle | **OpenCV** |
| 45 | Radial blur | Blur radiating from center point outward | Sample pixels along radial lines, average | **OpenCV** |
| 46 | Zoom blur | Blur radiating outward (fast zoom feel) | Blend multiple scaled copies of frame | **OpenCV** + numpy |
| 47 | Tilt-shift / miniature | Sharp horizontal band in middle, blurred above/below | Gradient mask controlling per-pixel blur radius | **OpenCV** |
| 48 | Depth-of-field | Blur proportional to distance from focal depth | Depth map drives per-pixel blur radius | **OpenCV** + depth map |
| 49 | Sharpen | Enhance edges and fine detail | Unsharp mask: `frame + alpha * (frame - blurred)` | **OpenCV** |
| 50 | Pixelate | Blocky mosaic / low-res effect | Downscale with `INTER_NEAREST` then upscale back | **OpenCV** |
| 51 | Bilateral blur | Smooth flat regions while preserving sharp edges | `cv2.bilateralFilter(frame, d, sigmaColor, sigmaSpace)` | **OpenCV** |
| 52 | Animated blur | Blur intensity changes over clip duration | Animated kernel size parameter driven by easing | **OpenCV** |

---

### Category 4: Texture and Overlay Effects (20 effects)

Effects that add visual elements on top of the frame. Implemented in `engine/effects/texture.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 53 | Film grain | Random luminance noise simulating film stock | `frame + np.random.normal(0, intensity, shape)` clipped | numpy |
| 54 | Colored noise | Per-channel independent random noise | Same as grain but independent per R/G/B | numpy |
| 55 | Vignette | Darken edges, keep center bright | Precompute radial gradient mask, `frame * gradient` | numpy |
| 56 | Scan lines | Horizontal dark lines (CRT monitor feel) | Multiply every Nth row by a darkening factor | numpy |
| 57 | Letterbox bars | Cinematic black bars at top and bottom | Set top and bottom pixel rows to black | numpy |
| 58 | Border / frame | Colored rectangular border around frame | Draw rectangle inset or pad with color | Pillow or numpy |
| 59 | Gradient overlay | Linear or radial color gradient blended on top | Generate gradient array, blend: `frame * (1-a) + grad * a` | numpy |
| 60 | Image watermark | Semi-transparent image composited at a position | Load image, alpha-composite at fixed or animated position | Pillow or numpy |
| 61 | Pattern overlay | Repeating pattern (stripes, dots, grid) blended | Tile a small pattern array, multiply or blend | numpy |
| 62 | Light leak | Bright colored blobs near edges (film artifact) | Gaussian blobs at random edge positions, additive blend | numpy |
| 63 | Bokeh overlay | Blurred circular light highlights | Draw circles with radial gradient, additive blend | Pillow + numpy |
| 64 | Dust and scratches | Random marks and hairline scratches (old film) | Draw random lines/dots from precomputed or per-frame | Pillow + numpy |
| 65 | Lens flare | Bright radial streaks from a light source position | Radial gradient + streak lines at position, additive | numpy + Pillow |
| 66 | Snow | Falling white dots of varying size | Particle positions updated per frame by velocity, draw dots | Pillow + numpy |
| 67 | Rain | Falling semi-transparent streaks | Particle lines with downward velocity + slight angle | Pillow + numpy |
| 68 | Confetti | Colorful falling/tumbling small shapes | Particle system with rotation and color, draw rects/circles | Pillow + numpy |
| 69 | Floating particles / dust motes | Slow-drifting small dots (ambient motion) | Particle system with Perlin-like noise drift | Pillow + numpy |
| 70 | Sparkle / glint | Brief bright points that flash on and off randomly | Random positions with sine-based intensity envelope | Pillow + numpy |
| 71 | Smoke / fog overlay | Semi-transparent drifting cloud layer | Scrolling Perlin noise field, blended onto frame | numpy |
| 72 | Progress bar | Animated bar showing video playback progress | Draw filled rectangle where width = `total_width * (t / duration)` | Pillow |

---

### Category 5: Stylization Effects (15 effects)

Artistic transforms that alter the visual character. Implemented in `engine/effects/stylize.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 73 | Edge detection | Show only edges as white lines on black | `cv2.Canny(gray, threshold1, threshold2)` | **OpenCV** |
| 74 | Sketch / pencil | Black and white pencil drawing look | `cv2.pencilSketch(frame, sigma_s, sigma_r, shade)` | **OpenCV** |
| 75 | Oil painting | Smooth, painterly brush-stroke look | `cv2.stylization(frame, sigma_s, sigma_r)` | **OpenCV** |
| 76 | Emboss | Raised/stamped surface illusion | Convolution with emboss kernel `[[-2,-1,0],[-1,1,1],[0,1,2]]` | Pillow or **OpenCV** |
| 77 | Halftone | Dots of varying size based on local luminance | Map luminance to dot radius, draw on grid | Pillow + numpy |
| 78 | Chromatic aberration | Subtle RGB channel offset (lens fringing) | Shift R channel +2px and B channel -2px | numpy |
| 79 | Glitch -- RGB split | Large offset between color channels | Shift R/G/B by 5-20px in different directions | numpy |
| 80 | Glitch -- block displacement | Rectangular blocks shifted horizontally | Random horizontal row-slice offsets | numpy |
| 81 | Glitch -- scan line shift | Individual rows displaced horizontally | Per-row random horizontal pixel offset | numpy |
| 82 | Glitch -- color corruption | Random color channel swaps in rectangular regions | Swap R/G/B in random rects | numpy |
| 83 | CRT / retro | Scan lines + barrel distortion + color bleed | Combine: scan line mask + barrel remap + slight channel blur | numpy + **OpenCV** |
| 84 | VHS / tape distortion | Horizontal jitter + color bleed + noise bands | Row shifts + per-channel blur offsets + noise stripes | numpy + **OpenCV** |
| 85 | Threshold / high contrast B&W | Pure black and white, no grays | `np.where(gray > threshold, 255, 0)` | numpy |
| 86 | Dithering | Threshold with error diffusion (retro print) | Floyd-Steinberg algorithm on grayscale | numpy |
| 87 | Mosaic / stained glass | Voronoi-style colored regions | Random Voronoi cells or grid, fill each with mean color | **OpenCV** or **scipy** |

---

### Category 6: Text and Typography Effects (21 effects)

Use the existing Pillow text infrastructure with added animation. Implemented in `engine/typography/animated_text.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 88 | Static text overlay | Text drawn at a fixed position | `ImageDraw.text((x, y), text, font, fill)` | Pillow |
| 89 | Fade-in text | Text appears from fully transparent | Draw text on RGBA layer, composite with `alpha(t)` increasing | Pillow + numpy |
| 90 | Fade-out text | Text disappears to fully transparent | Same as above, alpha decreasing | Pillow + numpy |
| 91 | Fly-in (any direction) | Text slides in from off-screen edge | Animated `(x(t), y(t))` with easing, starting off-screen | Pillow |
| 92 | Fly-out (any direction) | Text slides out to off-screen edge | Same, reversed direction | Pillow |
| 93 | Scale up / pop-in | Text grows from zero to full size | Render text at increasing font size or render large + downscale | Pillow |
| 94 | Scale down / pop-out | Text shrinks from full size to zero | Same, reversed | Pillow |
| 95 | Bounce-in | Text arrives with overshoot bounce | Position or scale driven by bounce easing function | Pillow |
| 96 | Elastic-in | Text arrives with spring oscillation | Position or scale driven by elastic easing function | Pillow |
| 97 | Typewriter | Characters appear one by one left to right | `text[:n(t)]` where n increases with time | Pillow |
| 98 | Word-by-word reveal | Words appear sequentially based on timing | Words shown up to current time using TTS word timestamps | Pillow |
| 99 | Word highlight | Current spoken word shown in different color | Already implemented in existing subtitle system | Pillow |
| 100 | Kinetic typography | Spoken word animates (scale/bounce/fly) per word timing | Per-word position/scale/opacity driven by word start/end times with easing | Pillow |
| 101 | Text with drop shadow | Shadow copy drawn behind text | Draw text twice: first offset by (dx,dy) in shadow color, then normal | Pillow |
| 102 | Text with outline/stroke | Colored border around each character | `ImageDraw.text` with `stroke_width` + `stroke_fill` params (Pillow >= 8.0) | Pillow |
| 103 | Text with glow | Soft light halo behind text | Draw text on separate layer, apply Gaussian blur, composite behind crisp text | Pillow + **OpenCV** |
| 104 | Lower third | Animated bar/shape with text that slides in from edge | Draw filled rectangle + text, animate x/y position from off-screen | Pillow |
| 105 | Ticker / crawl | Text scrolls continuously left to right (news-style) | Animated x position that wraps, text wider than screen | Pillow |
| 106 | Vertical scroll / credits | Text scrolls upward continuously | Animated y position, text taller than screen | Pillow |
| 107 | Counter / number tick | Number that counts up or down between two values | Format `int(lerp(start, end, progress))` as text, draw | Pillow |
| 108 | Subtitle karaoke sweep | Highlight sweeps across text pixel-by-pixel (not word-by-word) | Gradient mask moving across text based on time within segment | Pillow + numpy |

---

### Category 7: Transition Effects (27 effects)

Two-input blends that sit between clips. Both clips render their frame independently, then the transition composites them. Implemented in `engine/transitions/`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 109 | Crossfade / dissolve | Smooth alpha blend from A to B | `A * (1-p) + B * p` | numpy |
| 110 | Fade through black | A fades to black, then B fades in from black | `A * max(0, 1-2p)` then `B * max(0, 2p-1)` | numpy |
| 111 | Fade through white | Same but through white | Lerp A toward 255, then B from 255 | numpy |
| 112 | Fade through color | Same but through any specified RGB color | Lerp A toward color, then B from color | numpy |
| 113 | Slide left | B slides in from right edge, covering A | Place B at `x = width * (1-p)`, A visible underneath | numpy |
| 114 | Slide right | B slides in from left edge, covering A | Place B at `x = -width * (1-p)` | numpy |
| 115 | Slide up | B slides in from bottom edge | Place B at `y = height * (1-p)` | numpy |
| 116 | Slide down | B slides in from top edge | Place B at `y = -height * (1-p)` | numpy |
| 117 | Push left | A and B both move left together | A scrolls left, B follows from right | numpy |
| 118 | Push right | Both move right | A scrolls right, B follows from left | numpy |
| 119 | Push up | Both move up | A scrolls up, B follows from below | numpy |
| 120 | Push down | Both move down | A scrolls down, B follows from above | numpy |
| 121 | Wipe left | Vertical boundary moves left to right revealing B | `output[:, :col] = B; output[:, col:] = A` where col = `width * p` | numpy |
| 122 | Wipe right | Boundary moves right to left | Same, reversed direction | numpy |
| 123 | Wipe up | Horizontal boundary moves top to bottom | Row-based boundary | numpy |
| 124 | Wipe down | Boundary moves bottom to top | Same, reversed | numpy |
| 125 | Wipe with soft edge | Wipe with gradient feather at boundary | Gradient mask instead of hard cut, width-configurable | numpy |
| 126 | Iris open (circle wipe) | Circle expands from center revealing B | Distance-from-center mask < `radius * p` selects B, else A | numpy |
| 127 | Iris close | Circle shrinks to center | Same mask, inverted | numpy |
| 128 | Clock wipe | Rotating line sweeps around center revealing B | Angle-from-center mask < `360 * p` selects B | numpy |
| 129 | Diamond wipe | Diamond shape expands from center | Manhattan distance mask `(abs(dx) + abs(dy))` < threshold | numpy |
| 130 | Blinds horizontal | Horizontal strips alternate between A and B | Striped row mask with moving threshold per strip | numpy |
| 131 | Blinds vertical | Vertical strips alternate | Striped column mask | numpy |
| 132 | Zoom through | A zooms past camera (scale up + fade), B appears behind | Scale A up while fading out, B underneath | **OpenCV** + numpy |
| 133 | Whip pan | Fast motion blur in one direction during switch | Apply motion blur to both, crossfade in middle | **OpenCV** + numpy |
| 134 | Pixelate transition | A pixelates out (increasing block size), B pixelates in | Progressive downscale-upscale with crossfade | **OpenCV** |
| 135 | Glitch transition | Glitch effects intensify at the cut point, then resolve | RGB split + block displacement layered over crossfade | numpy |

---

### Category 8: Audio-Reactive Effects (12 effects)

Require analyzing the audio (typically TTS output) with librosa, then feeding analysis results as parameters into other effects. Implemented in `engine/audio/`.

| # | Effect | What it does | Audio analysis used | Dep |
|---|---|---|---|---|
| 136 | Beat-synced transitions | Transition start/end snapped to nearest musical beat | `librosa.beat.beat_track` -> beat timestamps | **librosa** |
| 137 | Beat-synced cuts | Clip boundaries auto-placed on beats | Same beat timestamps | **librosa** |
| 138 | Onset flash | Brief brightness spike on percussive/sharp sounds | `librosa.onset.onset_detect` -> onset timestamps | **librosa** + numpy |
| 139 | Onset zoom pulse | Brief zoom bump triggered by sound onset | Same onset timestamps, drives zoom parameter | **librosa** + **OpenCV** |
| 140 | Energy-driven zoom | Subtle zoom level breathes with audio loudness | `librosa.feature.rms` -> frame-level energy envelope | **librosa** + **OpenCV** |
| 141 | Energy-driven brightness | Frame brightness scales with audio loudness | RMS energy envelope -> brightness multiplier | **librosa** + numpy |
| 142 | Energy-driven shake | Camera jitter amplitude follows loudness | RMS energy envelope -> shake displacement | **librosa** + numpy + **scipy** |
| 143 | Spectral color shift | Color temperature tracks tonal brightness of audio | `librosa.feature.spectral_centroid` -> warm/cool factor | **librosa** + numpy |
| 144 | Bass-driven pulse | Low-frequency energy drives scale or glow intensity | Band-pass filter on spectrum, extract sub-200Hz energy | **librosa** + numpy |
| 145 | Waveform visualization | Draw audio waveform shape overlaid on frame | Raw audio samples windowed around current time | **librosa** + Pillow |
| 146 | Spectrum bars | Animated frequency magnitude bars (EQ visualization) | `librosa.feature.melspectrogram` windowed at current time | **librosa** + Pillow |
| 147 | Auto-pacing | Clip durations automatically adapt to speech rhythm | Silence detection + word density analysis | **librosa** |

---

### Category 9: Depth-Based Effects (8 effects)

Require a per-pixel depth map -- either user-supplied or generated by an optional model. Implemented in `engine/depth/`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 148 | Parallax -- 2 layer | Foreground and background move at different rates | Split image by depth threshold into 2 layers, transform each with different motion scale, composite back-to-front | **OpenCV** + depth map |
| 149 | Parallax -- N layer | Multiple depth layers for smoother parallax | N depth thresholds, N independent transforms, composite in depth order | **OpenCV** + depth map |
| 150 | Depth-of-field | Blur intensity proportional to distance from focal plane | Per-pixel blur radius = `abs(depth - focal_depth) * scale`, variable-radius Gaussian | **OpenCV** + depth map |
| 151 | Fog / atmosphere | Distant objects fade into a fog color | `pixel * (1 - depth * intensity) + fog_color * (depth * intensity)` | numpy + depth map |
| 152 | Foreground pop | Slight scale-up on foreground subject for emphasis | Mask foreground by depth < threshold, scale up, composite over blurred/darkened background | **OpenCV** + depth map |
| 153 | Depth-based color grade | Different color grading by distance (warm close, cool far) | Per-pixel lerp between two color grade LUTs using depth as interpolation weight | numpy + depth map |
| 154 | Focus pull / rack focus | Focal plane shifts over time (cinematic technique) | Animated `focal_depth(t)` parameter for the depth-of-field effect | **OpenCV** + depth map |
| 155 | Depth-aware Ken Burns | Pan/zoom with automatic parallax from depth | Ken Burns camera path applied per-layer with depth-scaled offsets | **OpenCV** + depth map |

---

### Category 10: Temporal / State-Based Effects (5 effects)

Depend on more than the current frame. These maintain internal state (e.g., ring buffer of previous frames) but are still `frame_in -> effect -> frame_out` from the pipeline's perspective. Implemented in `engine/effects/temporal.py`.

| # | Effect | What it does | Implementation | Dep |
|---|---|---|---|---|
| 156 | Motion trail / echo | Current frame blended with N previous frames creating ghostly trails | Ring buffer of last N frames, weighted blend: `sum(w_i * frame_i)` | numpy |
| 157 | Ghosting | Faint copy of the immediately previous frame persists | `output = frame * 0.7 + prev_frame * 0.3`, single-frame memory | numpy |
| 158 | Strobe | Alternate between current frame and black/white at a frequency | `frame if (t * freq) % 1 > 0.5 else solid_color` | numpy |
| 159 | Freeze frame | Hold a single frame for a specified duration | Cache frame at freeze_time, return cached for duration | numpy |
| 160 | Flash frame | Single-frame burst of white or a color at a specific timestamp | Return `np.full(shape, color)` at exact time, normal frame otherwise | numpy |

---

### Dependency Summary

| Dependency | Status | Effects enabled | Count |
|---|---|---|---|
| **numpy** | Already installed | Array math for blending, color transforms, noise, masks, gradients, particles | Used by ~130 effects |
| **Pillow** | Already installed | Text rendering, drawing primitives (shapes, dots, lines), basic image I/O | ~30 effects |
| **OpenCV** (opencv-python) | New -- required | Spatial transforms, blur variants, color space (HSV), stylization filters, depth compositing, fast resize | ~45 effects |
| **scipy** | New -- required | Easing curves (splines, bezier), signal smoothing (camera shake), interpolation (camera paths) | Foundation for all animation + ~5 effects directly |
| **librosa** | New -- required | Beat detection, onset detection, RMS energy, spectral features -- drives audio-reactive effects | ~12 effects |
| Depth map (data input) | New -- user-supplied data | Parallax, depth-of-field, fog, focus pull, foreground pop, depth-aware Ken Burns | ~8 effects |
| **torch + transformers** | Optional (torch already present via kokoro) | Auto-generate depth maps when user does not supply them | Enables depth effects without manual depth map creation |


---

## Phase Completion Notes

### Phase 4: Rich Effects Library (Completed March 2026)

Phase 4 has been **successfully completed** and is production-ready. The implementation delivers:

**Implemented Effects (56 total):**
- ✅ 21 color effects (grayscale, invert, sepia, posterize, solarize, hue_shift, color_temperature, tint, gamma_correction, curves_lut, channel_mixer, duotone, tricolor, cinematic_teal_orange, bleach_bypass, cross_process, thermal, auto_white_balance, vibrance, color_pulse, fade_to_color)
- ✅ 11 blur effects (box_blur, gaussian_blur, bilateral_blur, sharpen, motion_blur, radial_blur, zoom_blur, animated_blur, pixelate, tilt_shift, depth_of_field)
- ✅ 12 texture effects (scan_lines, letterbox, vignette_simple, gradient_overlay, pattern_overlay, border, light_leak, bokeh_overlay, lens_flare, image_watermark, dust_scratches, progress_bar)
- ✅ 14 stylization effects (edge_detection, sketch, oil_painting, emboss, halftone, chromatic_aberration, glitch_rgb_split, glitch_block_displacement, glitch_scan_line_shift, glitch_color_corruption, crt_retro, vhs_tape_distortion, threshold_bw, dithering)

**Implemented Transitions (11 total):**
- ✅ 4 push transitions (push_left, push_right, push_up, push_down)
- ✅ 3 blinds/wipe transitions (blinds_horizontal, blinds_vertical, diamond_wipe)
- ✅ 4 animated transitions (zoom_through, whip_pan, pixelate, glitch)

**Testing:**
- ✅ 756 tests passing (99.9% pass rate)
- ✅ 55 property-based tests for Phase 4 effects
- ✅ Full backward compatibility with Phases 1-3
- ✅ Integration tests with Scene DSL verified

**Documentation:**
- ✅ User documentation in `docs/video_engine.md`
- ✅ Showcase examples in `examples/demo_phase4_rich_effects.py`
- ✅ Usage guide in `examples/PHASE4_SHOWCASE.md`
- ✅ Completion report in `.kiro/specs/video-engine-phase4-verification/PHASE4_COMPLETION_REPORT.md`

**Performance:**
- Color effects: 5-15ms per frame at 1080p
- Blur effects: 10-50ms per frame at 1080p
- Texture effects: 5-30ms per frame at 1080p
- Stylization effects: 20-100ms per frame at 1080p
- Transitions: 50-150ms per frame at 1080p

**Status:** Production-ready with 92% overall completion (core implementation 100%, documentation 85%).

### Deferred to Phase 5

The following effects from the original catalog are intentionally deferred to Phase 5 (Depth and Parallax):
- Particle systems (snow, rain, confetti, sparkles, floating particles)
- Real depth-based effects (parallax layers, accurate depth-of-field)
- Mosaic/stained glass effect
- Advanced physics simulations

### Next Steps

**Phase 5: Depth and Parallax** (Planned)
- Depth map loader (user-supplied PNG/EXR)
- Parallax layer splitting and differential motion
- Real depth-of-field effect
- Optional: model-based depth estimation (MiDaS / Depth Anything)
- Particle systems with physics

**Phase 6: Typography Animations** (Planned)
- Animated text elements (fly-in, scale, bounce, typewriter)
- Kinetic typography driven by TTS word timings
- Lower thirds, progress bars, tickers
- Integration with existing subtitle system (animated subtitles as a mode)

---

**Document Version:** 1.4  
**Last Updated:** March 8, 2026  
**Phase 4 Completion Date:** March 8, 2026
